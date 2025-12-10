"""
XUANYUAN Module Generator

This module generates the XUANYUAN block for BDF input files.
"""

from typing import Dict, Any, List
from .passthrough import append_passthrough_lines


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
    xuanyuan_settings = {
        **settings.get('xuanyuan', {}),
        **settings.get('atomic_orbital_integral', {}),
    }
    # hamiltonian is at top level, same as method and settings
    hamiltonian_settings = config.get('hamiltonian', {})
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
    # Hamiltonian (relativistic) controls: map scalar_Hamiltonian -> heff, spin-orbit-coupling -> hso
    def _elements_from_coordinates(cfg: Dict[str, Any]) -> List[str]:
        elems: List[str] = []
        mol = cfg.get('molecule', {})
        coords = mol.get('coordinates', [])
        for item in coords:
            sym = None
            if isinstance(item, str):
                parts = item.strip().split()
                if parts:
                    sym = parts[0]
            elif isinstance(item, (list, tuple)) and item:
                sym = str(item[0])
            if sym:
                elems.append(sym.capitalize())
        return elems

    HEAVY_ELEMENTS = {
        # Period >= 4
        'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
        'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
        'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
        'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
        'Cs', 'Ba',
        'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
        'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
        'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
        'Fr', 'Ra',
        'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr',
        'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og',
    }

    elements = _elements_from_coordinates(config)
    has_heavy = any(e in HEAVY_ELEMENTS for e in elements)

    basis = method.get('basis', '') or ''
    basis_lower = str(basis).lower()
    has_relativistic_basis = any(tag in basis_lower for tag in ['x2c', 'dkh', 'dk', 'dyall', 'relativistic', 'rcc'])
    has_ecp = 'ecp' in basis_lower

    user_scalar = hamiltonian_settings.get('scalar_Hamiltonian')
    user_soc = hamiltonian_settings.get('spin-orbit-coupling')

    need_auto = (has_heavy or has_relativistic_basis) and not has_ecp
    add_heff = (user_scalar is not None and user_scalar is not False) or (user_scalar is None and need_auto)
    def _boolish(val: Any) -> bool:
        if isinstance(val, bool):
            return val
        if val is None:
            return False
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return val.strip().lower() not in ("", "0", "false", "no")
        return True

    add_hso = _boolish(user_soc)

    if add_heff:
        # Default to sf-X2C when auto-enabled or user sets True
        default_heff = 3
        heff_value = default_heff
        if isinstance(user_scalar, (int, float, str)) and not isinstance(user_scalar, bool):
            heff_value = user_scalar
        lines.append("heff")
        lines.append(f" {heff_value}")
    if add_hso:
        # Default SOC value: 2 for all-electron; 10 when ECP is used
        if user_soc is None or isinstance(user_soc, bool):
            hso_value = 10 if has_ecp else 2
        else:
            hso_value = user_soc
        lines.append("hso")
        lines.append(f" {hso_value}")

    # Passthrough for XUANYUAN / atomic orbital integral keywords
    protected = {'rs', 'heff', 'hso'}  
    append_passthrough_lines(lines, xuanyuan_settings, protected_keys=protected)

    lines.append("$END")
    return lines

