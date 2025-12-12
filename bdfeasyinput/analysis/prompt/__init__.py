"""
Analysis Prompt Templates

This module provides prompt templates for AI analysis.
Supports both Chinese and English languages.
"""

from .analysis_prompts import (
    QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT,
    QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_ZH,
    build_analysis_prompt,
    get_system_prompt,
    get_analysis_prompt,
    format_geometry,
    format_frequencies,
    Language,
)

__all__ = [
    'QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT',
    'QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_ZH',
    'build_analysis_prompt',
    'get_system_prompt',
    'get_analysis_prompt',
    'format_geometry',
    'format_frequencies',
    'Language',
]

