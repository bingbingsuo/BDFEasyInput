"""
Direct BDF Execution Module

This module provides functionality to execute BDF calculations directly
without using BDFAutotest.
"""

import os
import random
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional


class BDFDirectRunner:
    """
    直接 BDF 执行器
    
    不通过 BDFAutotest，直接执行 BDF 计算。
    需要在 YAML 配置中指定 BDF 安装目录和相关参数。
    """
    
    def __init__(
        self,
        bdf_home: str,
        bdf_tmpdir: Optional[str] = None,
        omp_num_threads: Optional[int] = None,
        omp_stacksize: Optional[str] = None
    ):
        """
        初始化直接 BDF 执行器
        
        Args:
            bdf_home: BDF 安装目录路径（将设置为 BDFHOME 环境变量）
            bdf_tmpdir: BDF 临时文件目录（将设置为 BDF_TMPDIR 环境变量）
            omp_num_threads: OpenMP 线程数（将设置为 OMP_NUM_THREADS 环境变量）
            omp_stacksize: OpenMP 栈大小（将设置为 OMP_STACKSIZE 环境变量，如 "512M"）
        """
        self.bdf_home = Path(bdf_home).resolve()
        
        if not self.bdf_home.exists():
            raise ValueError(f"BDF installation directory does not exist: {bdf_home}")
        
        # 检查 BDF 可执行文件
        self.bdf_executable = self.bdf_home / "sbin" / "bdf.drv"
        if not self.bdf_executable.exists():
            # 尝试其他可能的可执行文件名称
            alt_executable = self.bdf_home / "sbin" / "bdfdrv.py"
            if alt_executable.exists():
                self.bdf_executable = alt_executable
            else:
                raise ValueError(
                    f"BDF executable not found at {self.bdf_executable} or {alt_executable}\n"
                    f"Please check that BDF is properly installed at {bdf_home}"
                )
        
        # 临时目录模板（支持 $RANDOM 占位符）
        # 如果未指定，默认使用 /tmp/$RANDOM 格式
        # 注意：不在初始化时创建目录，而是在每次 run() 时生成新的随机目录
        if bdf_tmpdir:
            self.bdf_tmpdir_template = bdf_tmpdir
        else:
            # 默认使用 /tmp/$RANDOM 格式
            self.bdf_tmpdir_template = "/tmp/$RANDOM"
        
        # OpenMP 设置
        self.omp_num_threads = omp_num_threads or os.cpu_count() or 1
        self.omp_stacksize = omp_stacksize or "512M"
    
    def run(
        self,
        input_file: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行 BDF 计算
        
        Args:
            input_file: BDF 输入文件路径（.inp 文件）
            timeout: 超时时间（秒，可选）
            **kwargs: 其他参数（暂未使用）
        
        Returns:
            包含执行结果的字典：
            {
                'status': 'success' | 'failed' | 'timeout',
                'output_file': str,      # 输出文件路径（name.log）
                'error_file': str,      # 错误文件路径（name.err）
                'exit_code': int,       # 退出码
                'stdout': str,          # 标准输出（从文件读取）
                'stderr': str,          # 标准错误（从文件读取）
                'execution_time': float # 执行时间（秒）
            }
        """
        input_path = Path(input_file).resolve()
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if input_path.suffix.lower() != '.inp':
            raise ValueError(f"Input file must have .inp extension, got: {input_path.suffix}")
        
        # 工作目录：输入文件所在目录（将设置为 BDF_WORKDIR）
        work_dir = input_path.parent
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # 输出文件路径（在 BDF_WORKDIR 中）
        # 输入文件名：name.inp
        # 输出文件名：name.log
        # 错误文件名：name.err
        input_name = input_path.stem
        log_file = work_dir / f"{input_name}.log"
        err_file = work_dir / f"{input_name}.err"
        
        # 为本次运行生成临时目录（支持 $RANDOM 占位符）
        # 每次运行都使用新的随机目录，避免冲突
        if "$RANDOM" in self.bdf_tmpdir_template:
            rnd = random.randint(0, 999999)
            run_tmpdir_str = self.bdf_tmpdir_template.replace("$RANDOM", str(rnd))
        else:
            run_tmpdir_str = self.bdf_tmpdir_template
        run_tmpdir = Path(run_tmpdir_str).resolve()
        run_tmpdir.mkdir(parents=True, exist_ok=True)
        
        # 构建 BDF 命令
        # 命令格式：{BDFHOME}/sbin/bdf.drv -r {input_file}
        cmd = [
            str(self.bdf_executable),
            "-r",
            input_path.name  # 只使用文件名，因为工作目录已设置为输入文件目录
        ]
        
        # 准备环境变量
        env = os.environ.copy()
        env["BDFHOME"] = str(self.bdf_home)
        env["BDF_WORKDIR"] = str(work_dir)
        env["BDF_TMPDIR"] = str(run_tmpdir)  # 使用本次运行的临时目录
        env["OMP_NUM_THREADS"] = str(self.omp_num_threads)
        env["OMP_STACKSIZE"] = str(self.omp_stacksize)
        
        start_time = time.time()
        
        try:
            # 运行 BDF 命令
            # 标准输出和标准错误都保存到文件
            with open(log_file, "w", encoding="utf-8") as log_f, \
                 open(err_file, "w", encoding="utf-8") as err_f:
                process = subprocess.run(
                    cmd,
                    cwd=str(work_dir),
                    env=env,
                    stdout=log_f,
                    stderr=err_f,
                    timeout=timeout,
                    check=False,
                    text=True
                )
            
            execution_time = time.time() - start_time
            
            # 读取输出文件内容
            stdout_content = ""
            stderr_content = ""
            if log_file.exists():
                try:
                    stdout_content = log_file.read_text(encoding="utf-8")
                except Exception:
                    stdout_content = f"Failed to read log file: {log_file}"
            
            if err_file.exists():
                try:
                    stderr_content = err_file.read_text(encoding="utf-8")
                except Exception:
                    stderr_content = f"Failed to read error file: {err_file}"
            
            # 确定状态
            if process.returncode == 0:
                status = 'success'
            elif timeout and execution_time >= timeout:
                status = 'timeout'
            else:
                status = 'failed'
            
            result = {
                'status': status,
                'output_file': str(log_file),
                'error_file': str(err_file),
                'exit_code': process.returncode,
                'stdout': stdout_content,
                'stderr': stderr_content,
                'execution_time': execution_time,
                'command': ' '.join(cmd),
                'bdf_home': str(self.bdf_home),
                'bdf_workdir': str(work_dir),
                'bdf_tmpdir': str(run_tmpdir)  # 本次运行使用的临时目录
            }
            
            return result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                'status': 'timeout',
                'output_file': str(log_file),
                'error_file': str(err_file),
                'exit_code': -1,
                'stdout': '',
                'stderr': f'Calculation timed out after {timeout} seconds',
                'execution_time': execution_time,
                'command': ' '.join(cmd),
                'bdf_home': str(self.bdf_home),
                'bdf_workdir': str(work_dir),
                'bdf_tmpdir': str(run_tmpdir)  # 本次运行使用的临时目录
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'status': 'failed',
                'output_file': str(log_file),
                'error_file': str(err_file),
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': execution_time,
                'command': ' '.join(cmd),
                'bdf_home': str(self.bdf_home),
                'bdf_workdir': str(work_dir),
                'bdf_tmpdir': str(run_tmpdir) if 'run_tmpdir' in locals() else str(self.bdf_tmpdir_template),
                'error': str(e)
            }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BDFDirectRunner':
        """
        从 YAML 配置创建执行器
        
        Args:
            config: YAML 配置字典，应包含 execution 部分：
                execution:
                  type: direct  # 或 "bdfautotest"
                  bdf_home: "/path/to/bdf"
                  bdf_tmpdir: "/path/to/tmp"  # 可选
                  omp_num_threads: 8  # 可选
                  omp_stacksize: "512M"  # 可选
        
        Returns:
            BDFDirectRunner 实例
        """
        execution_config = config.get('execution', {})
        
        bdf_home = execution_config.get('bdf_home')
        if not bdf_home:
            raise ValueError(
                "execution.bdf_home is required in YAML config for direct BDF execution"
            )
        
        return cls(
            bdf_home=bdf_home,
            bdf_tmpdir=execution_config.get('bdf_tmpdir'),
            omp_num_threads=execution_config.get('omp_num_threads'),
            omp_stacksize=execution_config.get('omp_stacksize')
        )

