"""
Remote SSH BDF Execution Module

This module provides functionality to start BDF calculations on a remote
machine via password-less SSH.

设计原则：
- 不负责建立 SSH 凭据（由用户预先配置好免密登录）
- 支持“提交 + 轮询 + 拉回输出”的简单同步工作流
"""

import subprocess
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


class SSHRemoteRunner:
    """
    通过 SSH 在远程节点上直接运行 BDF（如 nohup 方式）的执行器。

    典型流程：
    1. 本地生成 BDF 输入文件 (.inp)
    2. 通过 scp 上传到远程工作目录
    3. 通过 ssh 在远程执行类似命令：
       - source 环境
       - cd 到工作目录
       - nohup run.x input.inp > job.log 2>&1 &
    4. 返回提交状态、远程工作目录等信息
    """

    def __init__(
        self,
        host: str,
        user: Optional[str] = None,
        workdir: str = ".",
        bdf_command: str = "run.x",
        env_setup: Optional[List[str]] = None,
        port: Optional[int] = None,
        poll_interval: Optional[int] = 30,
        max_wait: Optional[int] = None,
        download: bool = True,
    ):
        """
        Args:
            host: 远程主机名或 IP（如 "login1.cluster.com"）
            user: 远程用户名（如 "bsuo"，为空则使用本地默认 SSH 用户配置）
            workdir: 远程工作根目录（所有作业子目录在其下创建）
            bdf_command: 远程运行 BDF 的命令（如 "run.x" 或完整路径）
            env_setup: 远程环境初始化命令列表（如 ["source ~/.bashrc", "module load bdf"]）
            port: SSH 端口号（如 20214；为空则使用默认 22 或 ssh_config 中的配置）
            poll_interval: 轮询远程作业状态的时间间隔（秒），None 或 <=0 表示不轮询
            max_wait: 最大等待时间（秒），None 或 <=0 表示不限制（受上层超时时间约束）
            download: 作业结束后是否尝试将远程输出文件拉回本地
        """
        self.host = host
        self.user = user
        self.port = port
        self.workdir = workdir.rstrip("/") or "."
        self.bdf_command = bdf_command
        self.env_setup = env_setup or []

        # 轮询间隔：None 表示使用默认 30s，<=0 表示不轮询
        if poll_interval is None:
            self.poll_interval = 30
        elif poll_interval > 0:
            self.poll_interval = poll_interval
        else:
            self.poll_interval = 0

        # 最大等待时间：None 或 <=0 表示不限制（由上层 timeout 控制）
        self.max_wait = max_wait if (max_wait and max_wait > 0) else None
        self.download = download

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _remote_target(self) -> str:
        """返回 user@host 形式的 SSH 目标。"""
        if self.user:
            return f"{self.user}@{self.host}"
        return self.host

    def _run_local_cmd(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """运行本地命令，抛出异常时包含命令信息。"""
        try:
            return subprocess.run(
                cmd,
                check=True,
                text=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Command failed: {' '.join(cmd)}\n"
                f"Exit code: {e.returncode}\n"
                f"Stdout: {e.stdout}\n"
                f"Stderr: {e.stderr}"
            ) from e

    def _extract_referenced_geometry_files(self, inp_path: Path) -> List[Path]:
        """
        从 BDF 输入文件中提取引用的外部几何文件（如 file=xxx.xyz）。

        Args:
            inp_path: BDF 输入文件路径

        Returns:
            引用的几何文件路径列表（相对于输入文件所在目录）
        """
        referenced = []
        try:
            content = inp_path.read_text(encoding="utf-8")
            # 查找 Geometry ... End geometry 块中的 file= 行
            # 模式：Geometry ... file=filename.xyz ... End geometry
            geometry_block_pattern = re.compile(
                r"Geometry\s+(.*?)End\s+geometry",
                re.IGNORECASE | re.DOTALL,
            )
            match = geometry_block_pattern.search(content)
            if match:
                geometry_content = match.group(1)
                # 查找 file= 行
                file_pattern = re.compile(r"file\s*=\s*([^\s\n]+)", re.IGNORECASE)
                for file_match in file_pattern.finditer(geometry_content):
                    filename = file_match.group(1).strip()
                    # 如果是相对路径，相对于输入文件所在目录
                    if not Path(filename).is_absolute():
                        ref_path = inp_path.parent / filename
                    else:
                        ref_path = Path(filename)
                    referenced.append(ref_path)
        except Exception:
            # 解析失败不影响主流程，只是不会上传引用的文件
            pass
        return referenced

    # ------------------------------------------------------------------
    # 对外接口
    # ------------------------------------------------------------------
    def run(
        self,
        input_file: str,
        timeout: Optional[int] = None,
        use_debug_dir: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        在远程节点上启动 BDF 计算。

        - 如果未配置 poll_interval，则仅提交并立即返回 status='submitted'
        - 如果配置了 poll_interval，则在本次调用中轮询远程作业状态，直到
          - 检测到正常结束 / 错误结束，或
          - 超过 max_wait / timeout

        Args:
            input_file: 本地 BDF 输入文件路径 (.inp)
            timeout: 当前版本忽略（仅保留接口兼容性）
            use_debug_dir: 与本地 Runner 接口兼容，此处不使用
            **kwargs: 预留扩展

        Returns:
            result: 字典，字段视执行模式而定，典型字段包括：
                - status: 'submitted' | 'success' | 'failed' | 'timeout'
                - remote_workdir: 远程作业目录
                - remote_command: 远程执行的完整命令
                - ssh_target: user@host
                - output_file: 本地输出文件路径（如果已下载）
                - stdout/stderr: 提交阶段的输出
        """
        input_path = Path(input_file).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        if input_path.suffix.lower() != ".inp":
            raise ValueError(f"Input file must have .inp extension, got: {input_path.suffix}")

        job_name = input_path.stem

        # 远程作业目录：<workdir>/<job_name>
        remote_workdir = f"{self.workdir}/{job_name}"
        ssh_target = self._remote_target()

        # 1) 在远程创建工作目录
        ssh_cmd = ["ssh"]
        if self.port:
            ssh_cmd.extend(["-p", str(self.port)])
        ssh_cmd.extend([ssh_target, f"mkdir -p {remote_workdir}"])
        self._run_local_cmd(ssh_cmd)

        # 2) 上传输入文件到远程
        remote_input = f"{ssh_target}:{remote_workdir}/{input_path.name}"
        scp_cmd = ["scp"]
        if self.port:
            scp_cmd.extend(["-P", str(self.port)])
        scp_cmd.extend([str(input_path), remote_input])
        self._run_local_cmd(scp_cmd)

        # 2.5) 检查输入文件中是否引用了外部几何文件（如 file=xxx.xyz），如果有则上传
        referenced_files = self._extract_referenced_geometry_files(input_path)
        for ref_file in referenced_files:
            if ref_file.exists():
                remote_ref = f"{ssh_target}:{remote_workdir}/{ref_file.name}"
                scp_ref_cmd = ["scp"]
                if self.port:
                    scp_ref_cmd.extend(["-P", str(self.port)])
                scp_ref_cmd.extend([str(ref_file), remote_ref])
                self._run_local_cmd(scp_ref_cmd)
            else:
                # 警告：引用的文件不存在，但继续执行（BDF 会在运行时报错）
                import warnings
                warnings.warn(
                    f"Referenced geometry file not found: {ref_file}. "
                    f"BDF calculation may fail if the file is not available on remote."
                )

        # 3) 组装远程命令
        #    env_setup1 && env_setup2 && cd workdir && nohup bdf_command input.inp > job.log 2>&1 &
        setup_cmd = " && ".join(self.env_setup) if self.env_setup else ""
        cd_cmd = f"cd {remote_workdir}"
        run_cmd = f"nohup {self.bdf_command} {input_path.name} > {job_name}.log 2>&1 &"
        full_remote_cmd = " && ".join([c for c in [setup_cmd, cd_cmd, run_cmd] if c])

        # 4) 通过 SSH 启动远程作业
        ssh_run_cmd = ["ssh"]
        if self.port:
            ssh_run_cmd.extend(["-p", str(self.port)])
        ssh_run_cmd.extend([ssh_target, full_remote_cmd])
        proc = subprocess.run(
            ssh_run_cmd,
            text=True,
            capture_output=True,
        )

        # 提交阶段失败，直接返回
        if proc.returncode != 0:
            return {
                "status": "failed",
                "remote_workdir": remote_workdir,
                "remote_command": full_remote_cmd,
                "ssh_target": ssh_target,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "error": f"SSH submission failed with exit code {proc.returncode}",
            }

        # 如果未配置轮询，则只返回提交成功
        if self.poll_interval <= 0:
            return {
                "status": "submitted",
                "remote_workdir": remote_workdir,
                "remote_command": full_remote_cmd,
                "ssh_target": ssh_target,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }

        # --------------------
        # 轮询远程作业状态
        # --------------------
        start_time = time.time()
        status = "running"
        final_state = None  # DONE_OK, DONE_ERR, TIMEOUT

        # 优先使用 runner 自己的 max_wait，其次用调用者传入的 timeout
        max_wait = self.max_wait
        if max_wait is None and timeout:
            max_wait = timeout

        # 状态检查命令：在远程工作目录中检查日志内容
        check_cmd = (
            f"cd {remote_workdir} && "
            f"if grep -q 'Congratulations! BDF normal termination' {job_name}.log 2>/dev/null; then "
            f"echo DONE_OK; "
            f"elif grep -Ei 'ERROR|FATAL|ABORT' {job_name}.log 2>/dev/null; then "
            f"echo DONE_ERR; "
            f"elif [ -f {job_name}.err ]; then "
            f"echo DONE_ERR; "
            f"else "
            f"echo RUNNING; "
            f"fi"
        )

        while True:
            elapsed = time.time() - start_time
            if max_wait is not None and elapsed >= max_wait:
                final_state = "TIMEOUT"
                break

            ssh_check_cmd = ["ssh"]
            if self.port:
                ssh_check_cmd.extend(["-p", str(self.port)])
            ssh_check_cmd.extend([ssh_target, check_cmd])
            proc_check = subprocess.run(
                ssh_check_cmd,
                text=True,
                capture_output=True,
            )
            out = (proc_check.stdout or "").strip()

            if "DONE_OK" in out:
                final_state = "DONE_OK"
                break
            elif "DONE_ERR" in out:
                final_state = "DONE_ERR"
                break

            # 未识别为结束状态，继续等待
            time.sleep(self.poll_interval)

        # --------------------
        # 如需，尝试下载输出文件
        # --------------------
        local_output_file: Optional[Path] = None
        if self.download:
            # 下载主日志文件到本地输入文件所在目录
            local_log = input_path.with_suffix(".log")
            remote_log = f"{ssh_target}:{remote_workdir}/{job_name}.log"
            try:
                scp_back_cmd = ["scp"]
                if self.port:
                    scp_back_cmd.extend(["-P", str(self.port)])
                scp_back_cmd.extend([remote_log, str(local_log)])
                self._run_local_cmd(scp_back_cmd)
                local_output_file = local_log
            except Exception:
                # 下载失败不视为致命错误，只是不提供本地输出路径
                local_output_file = None

        # 映射 final_state 到对外 status
        if final_state == "DONE_OK":
            result_status = "success"
        elif final_state == "DONE_ERR":
            result_status = "failed"
        else:  # TIMEOUT 或 None
            result_status = "timeout"

        result: Dict[str, Any] = {
            "status": result_status,
            "remote_workdir": remote_workdir,
            "remote_command": full_remote_cmd,
            "ssh_target": ssh_target,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
        if local_output_file:
            result["output_file"] = str(local_output_file)

        return result

