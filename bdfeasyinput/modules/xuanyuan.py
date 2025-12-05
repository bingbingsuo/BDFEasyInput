"""
XUANYUAN Module Generator

This module generates the XUANYUAN block for BDF input files.
"""

from typing import Dict, Any, List


def generate_xuanyuan_block(config: Dict[str, Any]) -> List[str]:
    """
    Generate XUANYUAN module block.
    
    For simple SCF calculations, XUANYUAN is typically empty.
    For Range-Separated (RS) functionals (e.g., CAM-B3LYP), 
    the RS parameter should be set here.
    
    Reference: BDF SCF manual
    """
    lines = ["$XUANYUAN"]
    
    settings = config.get('settings', {})
    xuanyuan_settings = settings.get('xuanyuan', {})
    method = config.get('method', {})
    functional = method.get('functional', '').lower()
    
    # Check for RS functional and RS parameter
    # Common RS functionals: cam-b3lyp, lc-blyp, wb97x, etc.
    rs_functionals = ['cam-b3lyp', 'cam-b3lyp-d3', 'lc-blyp', 'wb97x', 'wb97xd', 
                     'wb97xd3', 'm11', 'm11-l', 'n12-sx', 'hse', 'hse06']
    
    rs_value = xuanyuan_settings.get('rs')
    is_rs_functional = any(rs_func in functional for rs_func in rs_functionals)
    
    if rs_value is not None:
        # User explicitly set RS parameter
        lines.append("RS")
        lines.append(f" {rs_value}")
    elif is_rs_functional:
        # RS functional detected but no RS parameter set
        # Use default value for CAM-B3LYP (0.33), otherwise warn
        if 'cam-b3lyp' in functional:
            lines.append("RS")
            lines.append(" 0.33")  # CAM-B3LYP default
        # For other RS functionals, user should set RS explicitly
        # We'll leave it empty and let user set it if needed
    
    lines.append("$END")
    return lines

