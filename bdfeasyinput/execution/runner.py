"""
BDF Execution Runner Factory

This module provides a factory function to create the appropriate runner
based on YAML configuration.
"""

from typing import Dict, Any, Optional, Union
from .bdfautotest import BDFAutotestRunner
from .bdf_direct import BDFDirectRunner


def create_runner(
    config: Optional[Dict[str, Any]] = None,
    bdfautotest_path: Optional[str] = None,
    bdf_home: Optional[str] = None,
    **kwargs
) -> Union[BDFAutotestRunner, BDFDirectRunner]:
    """
    创建 BDF 执行器
    
    根据配置或参数创建合适的执行器：
    - 如果提供了 bdfautotest_path，使用 BDFAutotestRunner
    - 如果提供了 bdf_home，使用 BDFDirectRunner
    - 如果提供了 config，从配置中读取 execution 部分
    
    Args:
        config: YAML 配置字典（可选）
        bdfautotest_path: BDFAutotest 路径（可选）
        bdf_home: BDF 安装目录（可选）
        **kwargs: 其他参数传递给执行器
    
    Returns:
        BDFAutotestRunner 或 BDFDirectRunner 实例
    
    Examples:
        # 从配置创建
        runner = create_runner(config=yaml_config)
        
        # 直接指定 BDFAutotest
        runner = create_runner(bdfautotest_path="/path/to/BDFAutoTest")
        
        # 直接指定 BDF 安装目录
        runner = create_runner(bdf_home="/path/to/bdf")
    """
    # 如果提供了 config，优先使用配置
    if config:
        execution_config = config.get('execution', {})
        execution_type = execution_config.get('type', 'direct')
        
        if execution_type == 'direct':
            # 直接执行模式
            # 支持新的配置格式：execution.direct.bdf_home
            direct_config = execution_config.get('direct', {})
            if direct_config:
                # 新格式：execution.direct.bdf_home
                bdf_home = direct_config.get('bdf_home')
                if not bdf_home:
                    raise ValueError("execution.direct.bdf_home is required when execution.type is 'direct'")
                return BDFDirectRunner(
                    bdf_home=bdf_home,
                    bdf_tmpdir=direct_config.get('bdf_tmpdir'),
                    omp_num_threads=direct_config.get('omp_num_threads'),
                    omp_stacksize=direct_config.get('omp_stacksize')
                )
            else:
                # 旧格式兼容：execution.bdf_home
                return BDFDirectRunner.from_config(config)
        elif execution_type == 'bdfautotest':
            # BDFAutotest 模式
            # 支持新的配置格式：execution.bdfautotest.path
            bdfautotest_config = execution_config.get('bdfautotest', {})
            if bdfautotest_config:
                # 新格式：execution.bdfautotest.path
                bdfautotest_path = bdfautotest_config.get('path') or bdfautotest_path
                if not bdfautotest_path:
                    raise ValueError(
                        "execution.bdfautotest.path is required when execution.type is 'bdfautotest'"
                    )
                config_file = bdfautotest_config.get('config_file')
                return BDFAutotestRunner(bdfautotest_path, config_file=config_file)
            else:
                # 旧格式兼容：execution.bdfautotest_path
                bdfautotest_path = execution_config.get('bdfautotest_path') or bdfautotest_path
                if not bdfautotest_path:
                    raise ValueError(
                        "execution.bdfautotest_path is required when execution.type is 'bdfautotest'"
                    )
                config_file = execution_config.get('config_file')
                return BDFAutotestRunner(bdfautotest_path, config_file=config_file)
        else:
            raise ValueError(
                f"Unknown execution type: {execution_type}. "
                f"Supported types: 'direct', 'bdfautotest'"
            )
    
    # 如果没有配置，根据参数决定
    if bdf_home:
        return BDFDirectRunner(
            bdf_home=bdf_home,
            bdf_tmpdir=kwargs.get('bdf_tmpdir'),
            omp_num_threads=kwargs.get('omp_num_threads'),
            omp_stacksize=kwargs.get('omp_stacksize')
        )
    elif bdfautotest_path:
        return BDFAutotestRunner(bdfautotest_path, config_file=kwargs.get('config_file'))
    else:
        raise ValueError(
            "Either config, bdfautotest_path, or bdf_home must be provided"
        )

