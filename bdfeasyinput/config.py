"""
Configuration Management Module

This module provides functionality to load and manage BDFEasyInput configuration.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def find_config_file(config_path: Optional[str] = None) -> Path:
    """
    查找配置文件
    
    Args:
        config_path: 指定的配置文件路径（可选）
    
    Returns:
        配置文件路径
    
    查找顺序：
    1. 指定的 config_path
    2. 环境变量 BDFEASYINPUT_CONFIG
    3. 当前目录的 config/config.yaml
    4. 用户主目录的 .bdfeasyinput/config.yaml
    """
    if config_path:
        return Path(config_path).expanduser().resolve()
    
    # 检查环境变量
    env_config = os.getenv("BDFEASYINPUT_CONFIG")
    if env_config:
        return Path(env_config).expanduser().resolve()
    
    # 检查当前目录
    current_dir_config = Path.cwd() / "config" / "config.yaml"
    if current_dir_config.exists():
        return current_dir_config
    
    # 检查用户主目录
    home_config = Path.home() / ".bdfeasyinput" / "config.yaml"
    if home_config.exists():
        return home_config
    
    # 默认返回当前目录的配置文件（可能不存在）
    return current_dir_config


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    会自动加载 config.yaml 和 ai_config.yaml（如果存在），并合并它们。
    config.yaml 包含供应商配置，ai_config.yaml 包含 AI 参数设置。
    
    Args:
        config_path: 配置文件路径（可选）
    
    Returns:
        配置字典（已合并）
    
    Raises:
        FileNotFoundError: 如果主配置文件不存在
        yaml.YAMLError: 如果 YAML 格式错误
    """
    config_file = find_config_file(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            f"Please create a config file at {config_file} or set BDFEASYINPUT_CONFIG environment variable."
        )
    
    # 加载主配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if config is None:
        config = {}
    
    # 尝试加载 ai_config.yaml（如果存在）
    ai_config_file = config_file.parent / "ai_config.yaml"
    if ai_config_file.exists():
        try:
            with open(ai_config_file, 'r', encoding='utf-8') as f:
                ai_config = yaml.safe_load(f)
            
            if ai_config and 'ai' in ai_config:
                # 合并 AI 配置（ai_config.yaml 中的设置会覆盖 config.yaml 中的）
                if 'ai' not in config:
                    config['ai'] = {}
                
                # 深度合并 AI 配置
                def deep_merge(base: Dict, update: Dict) -> Dict:
                    result = base.copy()
                    for key, value in update.items():
                        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                            result[key] = deep_merge(result[key], value)
                        else:
                            result[key] = value
                    return result
                
                config['ai'] = deep_merge(config['ai'], ai_config['ai'])
        except Exception as e:
            # 如果加载 ai_config.yaml 失败，只记录警告，不影响主配置
            import warnings
            warnings.warn(f"Failed to load ai_config.yaml: {e}")
    
    return config


def get_execution_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取执行配置
    
    Args:
        config: 完整配置字典
    
    Returns:
        执行配置字典
    """
    return config.get('execution', {})


def get_ai_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取 AI 配置
    
    Args:
        config: 完整配置字典
    
    Returns:
        AI 配置字典
    """
    return config.get('ai', {})


def get_analysis_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取分析配置
    
    Args:
        config: 完整配置字典
    
    Returns:
        分析配置字典
    """
    return config.get('analysis', {})


def merge_config_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并配置与默认值
    
    Args:
        config: 用户配置
    
    Returns:
        合并后的配置
    """
    # 默认配置
    defaults = {
        'execution': {
            'type': 'direct',
            'timeout': 3600,
            'direct': {
                'bdf_tmpdir': '/tmp/$RANDOM',
                'omp_stacksize': '512M',
            },
        },
        'ai': {
            'enabled': True,
            'default_provider': 'ollama',
            'defaults': {
                'temperature': 0.7,
                'max_tokens': 2000,
            },
            'planning': {
                'auto_fill': True,
                'suggest_methods': True,
                'suggest_optimization': True,
            },
        },
        'analysis': {
            'enabled': True,
            'output': {
                'format': 'markdown',
                'include_raw_data': True,
                'include_recommendations': True,
                'include_expert_insights': True,
            },
            'expert_mode': {
                'enabled': True,
                'depth': 'detailed',
            },
            'parsing': {
                'extract_all': True,
                'extract': {
                    'energy': True,
                    'geometry': True,
                    'frequencies': True,
                    'properties': True,
                    'warnings': True,
                    'errors': True,
                },
            },
        },
    }
    
    # 简单的深度合并（仅合并字典，不处理列表）
    def deep_merge(base: Dict, update: Dict) -> Dict:
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    return deep_merge(defaults, config)

