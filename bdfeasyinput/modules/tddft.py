"""
TDDFT Module Generator

This module generates the TDDFT block for BDF input files.
"""

from typing import Dict, Any, List, Optional


def generate_tddft_block(
    config: Dict[str, Any],
    tddft_block_settings: Optional[Dict[str, Any]] = None,
    isf: Optional[int] = None,
    istore: Optional[int] = None
) -> List[str]:
    """
    Generate TDDFT module block.
    
    Reference: BDF TDDFT manual
    
    Args:
        config: Full YAML configuration dictionary
        tddft_block_settings: Specific settings for this TDDFT block
        isf: Spin flip flag (0=singlet, 1=triplet, -1=spin-flip down)
        istore: Store wavefunction to file number (for SOC or gradient calculations)
    
    Returns:
        List of strings representing the BDF TDDFT block.
    """
    lines = ["$TDDFT"]
    
    # General settings from the main config
    settings = config.get('settings', {})
    global_tddft_settings = settings.get('tddft', {})
    
    # Merge global settings with block-specific settings, block-specific takes precedence
    current_tddft_settings = {**global_tddft_settings, **(tddft_block_settings or {})}
    
    # ISF (Spin-flip / Spin-conservation)
    if isf is not None:
        lines.append("isf")
        lines.append(f" {isf}")
    elif current_tddft_settings.get('spin_flip') is not None:
        lines.append("isf")
        lines.append(f" {current_tddft_settings['spin_flip']}")
    
    # IROOT: Number of roots per irrep
    n_states = current_tddft_settings.get('n_states')
    if n_states:
        lines.append("iroot")
        lines.append(f" {n_states}")
    
    # ITDA: TDA approximation
    use_tda = current_tddft_settings.get('tda', False)
    if use_tda:
        lines.append("itda")
        lines.append(" 1")
    
    # IDIAG: Diagonalization method
    idiag = current_tddft_settings.get('diagonalization_method')
    if idiag:
        lines.append("idiag")
        lines.append(f" {idiag}")
    
    # IWINDOW: Energy window
    energy_window = current_tddft_settings.get('energy_window')
    if energy_window:
        lines.append("iwindow")
        if isinstance(energy_window, dict):
            min_e = energy_window.get('min')
            max_e = energy_window.get('max')
            unit = energy_window.get('unit', 'eV')
            if min_e is not None and max_e is not None:
                lines.append(f" {min_e} {max_e} {unit}")
        elif isinstance(energy_window, list) and len(energy_window) == 2:
            lines.append(f" {energy_window[0]} {energy_window[1]}")
    
    # ISTORE: Store wavefunction
    if istore is not None:
        lines.append("istore")
        lines.append(f" {istore}")
    elif current_tddft_settings.get('store_wavefunction'):
        lines.append("istore")
        lines.append(f" {current_tddft_settings['store_wavefunction']}")
    
    # Convergence criteria
    crit_vec = current_tddft_settings.get('crit_vec')
    if crit_vec:
        lines.append("crit_vec")
        lines.append(f" {crit_vec}")
    
    crit_e = current_tddft_settings.get('crit_e')
    if crit_e:
        lines.append("crit_e")
        lines.append(f" {crit_e}")
    
    # IPRT: Print level
    iprt = current_tddft_settings.get('print_level')
    if iprt is not None:
        lines.append("iprt")
        lines.append(f" {iprt}")
    
    # Solvent non-equilibrium effects
    if current_tddft_settings.get('linear_response_non_equilibrium'):
        lines.append("solneqlr")
    if current_tddft_settings.get('linear_response_equilibrium'):
        lines.append("soleqlr")
    
    lines.append("$END")
    
    return lines

