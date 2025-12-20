"""
BDF Result Extractor

This module provides a unified interface for extracting structured metrics
from BDF calculation outputs.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ..analysis.parser.output_parser import BDFOutputParser
from .metrics import (
    CalculationMetrics,
    GeometryMetrics,
    FrequencyMetrics,
    ExcitedStateMetrics,
)


class BDFResultExtractor:
    """
    BDF 结果提取器
    
    封装 BDFOutputParser，提供统一的指标提取接口。
    """
    
    def __init__(self):
        """初始化提取器"""
        self.parser = BDFOutputParser()
    
    def extract_metrics(
        self,
        output_file: str,
        task_type: Optional[str] = None,
    ) -> CalculationMetrics:
        """
        从 BDF 输出文件提取指标
        
        Args:
            output_file: BDF 输出文件路径（.log 文件）
            task_type: 任务类型（'single_point', 'optimize', 'frequency', 
                       'optimize_frequency', 'excited'）。如果为 None，则自动检测。
        
        Returns:
            CalculationMetrics: 包含所有提取的指标
        
        Raises:
            FileNotFoundError: 如果输出文件不存在
            ValueError: 如果解析失败或任务类型无效
        """
        output_path = Path(output_file)
        if not output_path.exists():
            raise FileNotFoundError(f"Output file not found: {output_file}")
        
        # 解析输出文件
        try:
            parsed_data = self.parser.parse(str(output_path))
        except Exception as e:
            raise ValueError(f"Failed to parse BDF output: {e}") from e
        
        # 自动检测任务类型（如果未指定）
        if task_type is None:
            task_type = self._detect_task_type(parsed_data)
        
        # 根据任务类型提取相应的指标
        geometry = None
        frequency = None
        excited = None
        
        # 几何优化相关任务（包括激发态优化）
        if task_type in ('optimize', 'optimize_frequency'):
            geometry = GeometryMetrics.from_parsed_data(parsed_data)
        
        # 频率分析相关任务
        if task_type in ('frequency', 'optimize_frequency'):
            frequency = FrequencyMetrics.from_parsed_data(parsed_data)
        
        # 激发态计算（可能是纯激发态或激发态优化）
        if task_type == 'excited' or parsed_data.get('tddft'):
            excited = ExcitedStateMetrics.from_parsed_data(parsed_data)
            # 如果是激发态优化，也需要提取几何信息
            if task_type == 'excited' and parsed_data.get('optimization', {}).get('steps'):
                geometry = GeometryMetrics.from_parsed_data(parsed_data)
        
        # 单点能计算也可能有几何信息（最终几何结构）
        if task_type == 'single_point' and parsed_data.get('geometry'):
            geometry = GeometryMetrics.from_parsed_data(parsed_data)
        
        return CalculationMetrics(
            task_type=task_type,
            geometry=geometry,
            frequency=frequency,
            excited=excited,
        )
    
    def _detect_task_type(self, parsed_data: Dict[str, Any]) -> str:
        """
        自动检测任务类型
        
        Args:
            parsed_data: 解析后的数据字典
        
        Returns:
            任务类型字符串
        """
        optimization = parsed_data.get('optimization', {})
        frequency_data = parsed_data.get('frequency_data', {})
        tddft = parsed_data.get('tddft', [])
        
        # 检查是否有优化步骤
        has_optimization = bool(optimization.get('steps'))
        
        # 检查是否有频率数据
        has_frequency = bool(
            frequency_data and (
                frequency_data.get('vibrations') or
                frequency_data.get('translations_rotations') or
                frequency_data.get('all')
            )
        )
        
        # 检查是否有 TDDFT 数据
        has_tddft = bool(tddft and len(tddft) > 0)
        
        # 判断任务类型
        # 注意：激发态优化（如 TDDFT 优化）可能同时有优化步骤和 TDDFT 数据
        if has_optimization and has_frequency:
            return 'optimize_frequency'
        elif has_optimization and has_tddft:
            # 激发态优化：同时有优化步骤和 TDDFT 数据
            return 'optimize'  # 仍标记为 optimize，但会提取 excited 信息
        elif has_optimization:
            return 'optimize'
        elif has_frequency:
            return 'frequency'
        elif has_tddft:
            return 'excited'
        else:
            return 'single_point'
