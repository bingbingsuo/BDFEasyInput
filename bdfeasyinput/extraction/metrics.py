"""
BDF Calculation Metrics Data Classes

This module defines structured data classes for BDF calculation metrics,
providing a unified interface for extracting and serializing calculation results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class GeometryMetrics:
    """几何优化指标"""
    max_force: Optional[float] = None
    rms_force: Optional[float] = None
    final_energy: Optional[float] = None
    scf_converged: Optional[bool] = None
    optimization_converged: Optional[bool] = None
    n_iterations: Optional[int] = None
    final_geometry: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'max_force': self.max_force,
            'rms_force': self.rms_force,
            'final_energy': self.final_energy,
            'scf_converged': self.scf_converged,
            'optimization_converged': self.optimization_converged,
            'n_iterations': self.n_iterations,
            'final_geometry': self.final_geometry,
        }

    @classmethod
    def from_parsed_data(cls, parsed_data: Dict[str, Any]) -> 'GeometryMetrics':
        """从解析数据创建 GeometryMetrics"""
        optimization = parsed_data.get('optimization', {})
        steps = optimization.get('steps', [])
        current_values = optimization.get('current_values', {})
        
        # 提取最终能量：优先使用 optimization.final_energy，否则使用根级别的 energy
        final_energy = optimization.get('final_energy')
        if final_energy is None:
            final_energy = parsed_data.get('energy')
        
        # 提取最终几何：优先使用 optimization.final_geometry，否则使用根级别的 geometry
        final_geometry = optimization.get('final_geometry')
        if final_geometry is None:
            final_geometry = parsed_data.get('geometry', [])
        
        # 提取力值：优先使用最后一步的力值（收敛时的力值），否则使用 current_values
        # 注意：current_values 可能包含第一步的值，不是收敛时的值
        max_force = None
        rms_force = None
        
        if steps:
            # 使用最后一步的力值（收敛时的值）
            last_step = steps[-1]
            max_force = last_step.get('force_max')
            rms_force = last_step.get('force_rms')
        
        # 如果最后一步没有力值，回退到 current_values
        if max_force is None:
            max_force = current_values.get('force_max')
        if rms_force is None:
            rms_force = current_values.get('force_rms')
        
        return cls(
            max_force=max_force,
            rms_force=rms_force,
            final_energy=final_energy,
            scf_converged=parsed_data.get('converged'),
            optimization_converged=optimization.get('converged'),
            n_iterations=optimization.get('iterations'),
            final_geometry=final_geometry if final_geometry else None,
        )


@dataclass
class FrequencyMetrics:
    """频率分析指标"""
    min_freq: Optional[float] = None
    max_freq: Optional[float] = None
    imaginary_count: Optional[int] = None
    frequencies: List[float] = field(default_factory=list)
    vibrations: List[float] = field(default_factory=list)
    translations_rotations: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'min_freq': self.min_freq,
            'max_freq': self.max_freq,
            'imaginary_count': self.imaginary_count,
            'frequencies': self.frequencies,
            'vibrations': self.vibrations,
            'translations_rotations': self.translations_rotations,
        }

    @classmethod
    def from_parsed_data(cls, parsed_data: Dict[str, Any]) -> 'FrequencyMetrics':
        """从解析数据创建 FrequencyMetrics"""
        frequency_data = parsed_data.get('frequency_data', {})
        
        # 提取频率列表
        if isinstance(frequency_data, dict):
            vibrations = frequency_data.get('vibrations', [])
            translations_rotations = frequency_data.get('translations_rotations', [])
            all_frequencies = frequency_data.get('all', [])
        else:
            # 向后兼容：如果 frequency_data 是列表
            all_frequencies = frequency_data if isinstance(frequency_data, list) else []
            vibrations = []
            translations_rotations = []
        
        # 如果没有 all 字段，合并 vibrations 和 translations_rotations
        if not all_frequencies and (vibrations or translations_rotations):
            all_frequencies = vibrations + translations_rotations
        
        # 计算统计信息
        min_freq = None
        max_freq = None
        imaginary_count = 0
        
        if all_frequencies:
            numeric_freqs = [f for f in all_frequencies if isinstance(f, (int, float))]
            if numeric_freqs:
                min_freq = min(numeric_freqs)
                max_freq = max(numeric_freqs)
                imaginary_count = sum(1 for f in numeric_freqs if f < 0)
        
        return cls(
            min_freq=min_freq,
            max_freq=max_freq,
            imaginary_count=imaginary_count,
            frequencies=all_frequencies,
            vibrations=vibrations,
            translations_rotations=translations_rotations,
        )


@dataclass
class ExcitedStateMetrics:
    """激发态计算指标"""
    n_states_converged: Optional[int] = None
    states: List[Dict[str, Any]] = field(default_factory=list)
    energies: List[float] = field(default_factory=list)
    oscillator_strengths: List[float] = field(default_factory=list)
    wavelengths: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'n_states_converged': self.n_states_converged,
            'states': self.states,
            'energies': self.energies,
            'oscillator_strengths': self.oscillator_strengths,
            'wavelengths': self.wavelengths,
        }

    @classmethod
    def from_parsed_data(cls, parsed_data: Dict[str, Any]) -> 'ExcitedStateMetrics':
        """从解析数据创建 ExcitedStateMetrics"""
        tddft = parsed_data.get('tddft', [])
        
        # 使用第一个 TDDFT 计算块（通常只有一个）
        if not tddft:
            return cls()
        
        first_tddft = tddft[0]
        states = first_tddft.get('states', [])
        
        # 提取各状态的信息
        energies = []
        oscillator_strengths = []
        wavelengths = []
        
        for state in states:
            if 'energy_ev' in state:
                energies.append(state['energy_ev'])
            if 'oscillator_strength' in state:
                oscillator_strengths.append(state.get('oscillator_strength'))
            if 'wavelength_nm' in state:
                wavelengths.append(state.get('wavelength_nm'))
        
        return cls(
            n_states_converged=len(states),
            states=states,
            energies=energies,
            oscillator_strengths=oscillator_strengths,
            wavelengths=wavelengths,
        )


@dataclass
class CalculationMetrics:
    """计算指标总容器"""
    task_type: str
    geometry: Optional[GeometryMetrics] = None
    frequency: Optional[FrequencyMetrics] = None
    excited: Optional[ExcitedStateMetrics] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'task_type': self.task_type,
        }
        
        if self.geometry:
            result['geometry'] = self.geometry.to_dict()
        if self.frequency:
            result['frequency'] = self.frequency.to_dict()
        if self.excited:
            result['excited'] = self.excited.to_dict()
        
        return result
