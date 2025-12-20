"""
Remote Slurm BDF Execution Module

This module provides functionality to submit BDF calculations to a remote
Slurm cluster via password-less SSH.

当前设计：
- 在本地渲染 Slurm 作业脚本（基于一个简单模板）
- 通过 scp 上传 BDF 输入和作业脚本
- 在远程执行 sbatch，返回 jobid
- 不轮询作业状态，仅负责“提交”
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class SSHSlurmRunner:
    """
    通过 SSH + Slurm 提交 BDF 作业的执行器。
    """

    def __init__(
        self,
        host: str,
        user: Optional[str] = None,
        workdir: str = ".",
        sbatch_command: str = "sbatch",
        job_script_template: Optional[str] = None,
        env_setup: Optional[List[str]] = None,
        default_slurm: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            host: 远程 Slurm 登录节点
            user: 远程用户名
            workdir: 远程工作根目录
            sbatch_command: 提交命令（默认 \"sbatch\"）
            job_script_template: 本地 Slurm 脚本模板路径
            env_setup: 远程环境初始化命令列表
            default_slurm: 默认 Slurm 参数（partition, ntasks, cpus_per_task, time 等）
        """
        self.host = host
        self.user = user
        self.workdir = workdir.rstrip("/") or "."
        self.sbatch_command = sbatch_command
        self.job_script_template = job_script_template
        self.env_setup = env_setup or []
        self.default_slurm = default_slurm or {}

    def _remote_target(self) -> str:
        if self.user:
            return f"{self.user}@{self.host}"
        return self.host

    def _run_local_cmd(self, cmd: List[str]) -> subprocess.CompletedProcess:
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

    def _render_job_script(
        self,
        template_path: Path,
        job_name: str,
        input_filename: str,
        slurm_opts: Dict[str, Any],
        bdf_command: str,
    ) -> str:
        """
        使用非常简单的占位符替换渲染脚本：
        - {{JOB_NAME}}
        - {{INPUT_FILE}}
        - {{PARTITION}}
        - {{NTASKS}}
        - {{CPUS_PER_TASK}}
        - {{TIME}}
        - {{BDF_COMMAND}}
        """
        content = template_path.read_text(encoding="utf-8")
        # 填充缺省值
        partition = slurm_opts.get("partition", "compute")
        ntasks = slurm_opts.get("ntasks", 1)
        cpus_per_task = slurm_opts.get("cpus_per_task", 8)
        time_str = slurm_opts.get("time", "02:00:00")

        replacements = {
            "{{JOB_NAME}}": job_name,
            "{{INPUT_FILE}}": input_filename,
            "{{PARTITION}}": str(partition),
            "{{NTASKS}}": str(ntasks),
            "{{CPUS_PER_TASK}}": str(cpus_per_task),
            "{{TIME}}": str(time_str),
            "{{BDF_COMMAND}}": bdf_command,
        }
        for key, value in replacements.items():
            content = content.replace(key, value)
        return content

    def run(
        self,
        input_file: str,
        timeout: Optional[int] = None,
        use_debug_dir: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        将 BDF 计算作为 Slurm 作业提交到远程集群（非阻塞，只返回 jobid）。
        """
        input_path = Path(input_file).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        if input_path.suffix.lower() != ".inp":
            raise ValueError(f"Input file must have .inp extension, got: {input_path.suffix}")

        if not self.job_script_template:
            raise ValueError("job_script_template is required for SSHSlurmRunner")

        template_path = Path(self.job_script_template).resolve()
        if not template_path.exists():
            raise FileNotFoundError(f"Slurm job script template not found: {template_path}")

        job_name = input_path.stem
        ssh_target = self._remote_target()
        remote_workdir = f"{self.workdir}/{job_name}"

        # 合并默认 Slurm 参数和调用时传入的覆盖参数
        slurm_opts = dict(self.default_slurm)
        slurm_opts.update(kwargs.get("slurm", {}))

        # 渲染本地 job 脚本
        job_script_content = self._render_job_script(
            template_path=template_path,
            job_name=job_name,
            input_filename=input_path.name,
            slurm_opts=slurm_opts,
            bdf_command=slurm_opts.get("bdf_command", "run.x"),
        )
        local_job_script = input_path.with_suffix(".slurm.sh")
        local_job_script.write_text(job_script_content, encoding="utf-8")

        # 1) 在远程创建工作目录
        self._run_local_cmd(["ssh", ssh_target, f"mkdir -p {remote_workdir}"])

        # 2) 上传输入文件和脚本
        remote_input = f"{ssh_target}:{remote_workdir}/{input_path.name}"
        remote_script = f"{ssh_target}:{remote_workdir}/{local_job_script.name}"
        self._run_local_cmd(["scp", str(input_path), remote_input])
        self._run_local_cmd(["scp", str(local_job_script), remote_script])

        # 3) 远程执行 sbatch
        setup_cmd = " && ".join(self.env_setup) if self.env_setup else ""
        cd_cmd = f"cd {remote_workdir}"
        sbatch_cmd = f"{self.sbatch_command} {local_job_script.name}"
        full_remote_cmd = " && ".join([c for c in [setup_cmd, cd_cmd, sbatch_cmd] if c])

        proc = subprocess.run(
            ["ssh", ssh_target, full_remote_cmd],
            text=True,
            capture_output=True,
        )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        job_id = None

        # 尝试从 stdout 中解析 jobid，例如：Submitted batch job 123456
        m = re.search(r"Submitted batch job\s+(\d+)", stdout)
        if m:
            job_id = m.group(1)

        status = "submitted" if proc.returncode == 0 and job_id else "failed"

        return {
            "status": status,
            "remote_workdir": remote_workdir,
            "ssh_target": ssh_target,
            "remote_command": full_remote_cmd,
            "job_id": job_id,
            "stdout": stdout,
            "stderr": stderr,
        }

