"""
BDFAutotest Integration Module

This module provides a simple interface to run BDF calculations through BDFAutotest.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional


class BDFAutotestRunner:
    """
    BDFAutotest 执行器
    
    通过 BDFAutotest 工程运行 BDF 计算。
    执行逻辑全部交给 BDFAutotest 管理。
    """
    
    def __init__(
        self,
        bdfautotest_path: str,
        config_file: Optional[str] = None
    ):
        """
        初始化 BDFAutotest 执行器
        
        Args:
            bdfautotest_path: BDFAutotest 工程路径
            config_file: BDFAutotest 配置文件路径（可选，默认使用 config/config.yaml）
        """
        self.bdfautotest_path = Path(bdfautotest_path).resolve()
        
        if not self.bdfautotest_path.exists():
            raise ValueError(f"BDFAutotest path does not exist: {bdfautotest_path}")
        
        # 默认配置文件路径
        if config_file:
            self.config_file = Path(config_file).resolve()
        else:
            self.config_file = self.bdfautotest_path / "config" / "config.yaml"
        
        # 检查配置文件是否存在
        if not self.config_file.exists():
            raise ValueError(
                f"BDFAutotest config file not found: {self.config_file}\n"
                f"Please create a config file at {self.config_file} or specify one with config_file parameter."
            )
        
        # BDFAutotest orchestrator 脚本路径
        self.orchestrator_script = self.bdfautotest_path / "src" / "orchestrator.py"
        
        if not self.orchestrator_script.exists():
            raise ValueError(
                f"BDFAutotest orchestrator script not found: {self.orchestrator_script}\n"
                f"Please ensure BDFAutotest is properly installed."
            )
    
    def run(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        use_debug_dir: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行 BDF 计算
        
        使用 BDFAutotest 的 run_input_command 功能来执行单个输入文件。
        
        Args:
            input_file: BDF 输入文件路径（.inp 文件）
            output_dir: 输出目录（可选，默认与输入文件同目录）
            timeout: 超时时间（秒，可选）
            **kwargs: 其他传递给 BDFAutotest 的参数
        
        Returns:
            包含执行结果的字典：
            {
                'status': 'success' | 'failed' | 'timeout',
                'output_file': str,      # 输出文件路径（.out 或 .log）
                'error_file': str,      # 错误文件路径（如果有）
                'exit_code': int,       # 退出码
                'stdout': str,          # 标准输出
                'stderr': str,          # 标准错误
                'execution_time': float # 执行时间（秒）
            }
        """
        input_path = Path(input_file).resolve()
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if input_path.suffix.lower() != '.inp':
            raise ValueError(f"Input file must have .inp extension, got: {input_path.suffix}")
        
        # 确定输出目录
        # 如果 use_debug_dir=True，使用项目根目录的 debug 目录
        if use_debug_dir:
            # 从 bdfeasyinput/execution/bdfautotest.py 向上三级到项目根目录
            project_root = Path(__file__).parent.parent.parent
            debug_dir = project_root / "debug"
            output_path = debug_dir
            output_path.mkdir(parents=True, exist_ok=True)
            # 将输入文件复制到 debug 目录
            debug_input_file = output_path / input_path.name
            import shutil
            shutil.copy2(input_path, debug_input_file)
            # 使用 debug 目录中的输入文件
            input_path = debug_input_file
        elif output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path.parent
        
        # 输出文件路径（BDF 通常生成 .out 文件）
        output_file = output_path / input_path.with_suffix('.out').name
        log_file = output_path / input_path.with_suffix('.log').name
        
        # 调用 BDFAutotest 的 run-input 命令
        # 命令格式：python3 -m src.orchestrator run-input input.inp --config config.yaml
        # 需要在 BDFAutoTest 目录下运行
        cmd = [
            'python3',
            '-m', 'src.orchestrator',
            'run-input',
            str(input_path),
            '--config', str(self.config_file)
        ]
        
        # 添加额外参数
        for key, value in kwargs.items():
            if value is not None:
                cmd.extend([f'--{key.replace("_", "-")}', str(value)])
        
        start_time = time.time()
        
        try:
            # 运行命令
            # 需要在 BDFAutoTest 目录下运行，并设置 PYTHONPATH
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.bdfautotest_path) + (os.pathsep + env.get('PYTHONPATH', ''))
            
            process = subprocess.run(
                cmd,
                cwd=str(self.bdfautotest_path),  # 在 BDFAutoTest 目录下运行
                env=env,  # 设置环境变量
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            execution_time = time.time() - start_time
            
            # 确定实际输出文件（BDFAutotest 会在工作目录生成 .log 文件）
            # 根据 BDFAutotest 的 run_input_command，输出文件在工作目录
            work_dir = output_path  # 使用输出目录作为工作目录
            log_file_work = work_dir / input_path.with_suffix('.log').name
            err_file_work = work_dir / input_path.with_suffix('.err').name
            
            actual_output_file = None
            if log_file_work.exists():
                actual_output_file = str(log_file_work)
            elif output_file.exists():
                actual_output_file = str(output_file)
            elif log_file.exists():
                actual_output_file = str(log_file)
            else:
                # 尝试查找其他可能的输出文件
                for ext in ['.log', '.out', '.out.tmp']:
                    candidate = work_dir / input_path.with_suffix(ext).name
                    if candidate.exists():
                        actual_output_file = str(candidate)
                        break
            
            # 确定状态
            if process.returncode == 0:
                status = 'success'
            elif timeout and execution_time >= timeout:
                status = 'timeout'
            else:
                status = 'failed'
            
            result = {
                'status': status,
                'output_file': actual_output_file or str(output_file),
                'exit_code': process.returncode,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'execution_time': execution_time,
                'command': ' '.join(cmd)
            }
            
            # 如果有错误输出，尝试提取错误文件路径
            if process.stderr:
                result['error_info'] = process.stderr[:500]  # 前500字符
            
            # 检查是否有错误文件
            if err_file_work.exists():
                result['error_file'] = str(err_file_work)
            
            # 检查是否有错误文件
            if err_file_work.exists():
                result['error_file'] = str(err_file_work)
            
            return result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                'status': 'timeout',
                'output_file': str(output_file),
                'exit_code': -1,
                'stdout': '',
                'stderr': f'Calculation timed out after {timeout} seconds',
                'execution_time': execution_time,
                'command': ' '.join(cmd)
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'status': 'failed',
                'output_file': str(output_file),
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': execution_time,
                'command': ' '.join(cmd),
                'error': str(e)
            }
    
    def check_bdf_installation(self) -> Dict[str, Any]:
        """
        检查 BDF 安装是否可用
        
        Returns:
            包含检查结果的字典
        """
        # 读取配置文件获取 BDFHOME
        import yaml
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            build_cfg = config.get('build', {})
            git_cfg = config.get('git', {})
            default_source_dir = git_cfg.get('local_path', './package_source')
            source_dir = Path(build_cfg.get('source_dir', default_source_dir)).resolve()
            build_dir = source_dir / build_cfg.get('build_dir', 'build')
            bdf_home = build_dir / 'bdf-pkg-full'
            bdf_executable = bdf_home / 'sbin' / 'bdf.drv'
            
            return {
                'bdf_home': str(bdf_home),
                'bdf_executable': str(bdf_executable),
                'bdf_home_exists': bdf_home.exists(),
                'bdf_executable_exists': bdf_executable.exists(),
                'config_file': str(self.config_file),
                'config_file_exists': self.config_file.exists()
            }
        except Exception as e:
            return {
                'error': str(e),
                'config_file': str(self.config_file)
            }

