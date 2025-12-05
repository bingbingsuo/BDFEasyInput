"""
RESP Module Generator

This module generates the RESP block for BDF input files.
"""

from typing import Dict, Any, List, Optional, Union


def generate_resp_block(
    config: Dict[str, Any],
    method: Optional[int] = None,
    norder: Optional[int] = None,
    nfiles: Optional[int] = None,
    iroot: Optional[Union[int, List[int]]] = None
) -> List[str]:
    """
    Generate RESP module block for gradient/Hessian calculation.
    
    Reference: BDF Optimization manual
    
    Args:
        config: Full YAML configuration dictionary
        method: Method for response properties (1=SCF, 2=TDDFT)
        norder: Order of nuclear derivative (1=gradient, 2=Hessian, 0=energy only)
        nfiles: Number of files to read (for TDDFT)
        iroot: Root index for TDDFT gradient/properties
    
    Returns:
        List of strings representing the BDF RESP block.
    """
    lines = ["$RESP"]
    
    settings = config.get('settings', {})
    resp_settings = settings.get('resp', {})
    
    # Override with explicit parameters if provided
    if method is not None:
        resp_method = method
    else:
        resp_method = resp_settings.get('method', 1)
    
    if norder is not None:
        resp_norder = norder
    else:
        resp_norder = resp_settings.get('norder', 1)
    
    if nfiles is not None:
        resp_nfiles = nfiles
    else:
        resp_nfiles = resp_settings.get('nfiles')
    
    if iroot is not None:
        resp_iroot = iroot
    else:
        resp_iroot = resp_settings.get('iroot')
    
    # geom: indicates geometry optimization
    lines.append("geom")
    
    # norder: derivative order
    lines.append("norder")
    lines.append(f" {resp_norder}")
    
    # method: calculation method
    lines.append("method")
    lines.append(f" {resp_method}")
    
    # nfiles: for TDDFT gradient
    if resp_nfiles:
        lines.append("nfiles")
        lines.append(f" {resp_nfiles}")
    
    # iroot: for TDDFT gradient (which excited state)
    if resp_iroot:
        lines.append("iroot")
        if isinstance(resp_iroot, list):
            lines.append(f" {' '.join(map(str, resp_iroot))}")
        else:
            lines.append(f" {resp_iroot}")
    
    # Print level
    iprt = resp_settings.get('print_level')
    if iprt is not None:
        lines.append("iprt")
        lines.append(f" {iprt}")
    
    # Max memory (for analytical Hessian)
    maxmem = resp_settings.get('maxmem')
    if maxmem:
        lines.append("maxmem")
        lines.append(f" {maxmem}")
    
    # Solvent settings for RESP
    resp_solvent = resp_settings.get('solvent', {})
    if resp_solvent.get('linear_response_non_equilibrium'):
        lines.append("solneqlr")
    if resp_solvent.get('linear_response_equilibrium'):
        lines.append("soleqlr")
    if resp_solvent.get('state_specific_non_equilibrium'):
        lines.append("solneqss")
    if resp_solvent.get('state_specific_equilibrium'):
        lines.append("soleqss")
    
    lines.append("$END")
    
    return lines

