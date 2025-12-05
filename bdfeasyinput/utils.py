"""
BDFEasyInput Utility Functions

This module contains utility functions used across the converter.
"""

from typing import List, Optional
import re

# Valid point group names for BDF
# Reference: BDF Point-group manual
VALID_POINT_GROUPS = [
    # Abelian groups (D(2h) and its subgroups)
    "D(2h)", "D(2)", "C(2v)", "C(2h)", "C(s)", "C(2)", "C(1)", "C(i)",
    # Common non-Abelian groups (examples, not exhaustive)
    "C(3v)", "C(4v)", "C(5v)", "C(6v)",
    "D(3)", "D(4)", "D(5)", "D(6)",
    "D(3h)", "D(4h)", "D(5h)", "D(6h)",
    "D(3d)", "D(4d)", "D(5d)", "D(6d)",
    "T(d)", "O", "O(h)", "I", "I(h)",
    # Special groups
    "C(LIN)", "D(LIN)"
]


def select_scf_method(
    method_type: str,
    multiplicity: int,
    functional: Optional[str] = None,
    spin_adapted: bool = False
) -> str:
    """
    Select SCF method type based on configuration.

    Args:
        method_type: 'hf' or 'dft'
        multiplicity: Spin multiplicity (2S+1)
        functional: DFT functional name (for DFT methods)
        spin_adapted: Whether to use spin-adapted TDDFT

    Returns:
        SCF method keyword: 'RHF', 'UHF', 'ROHF', 'RKS', 'UKS', or 'ROKS'
    """
    if spin_adapted:
        if method_type == 'hf':
            return 'ROHF'
        elif method_type == 'dft':
            return 'ROKS'
    else:
        if method_type == 'hf':
            return 'RHF' if multiplicity == 1 else 'UHF'
        elif method_type == 'dft':
            return 'RKS' if multiplicity == 1 else 'UKS'
    
    raise ValueError(f"Invalid method_type: {method_type}")


def format_coordinates(
    coordinates: List[str],
    units: str = 'angstrom'
) -> List[str]:
    """
    Format coordinates for BDF input.
    
    BDF defaults to Angstrom, so if input is also Angstrom,
    no conversion is needed.
    
    Args:
        coordinates: List of coordinate strings in format "ATOM X Y Z"
        units: Input coordinate units ('angstrom' or 'bohr')
    
    Returns:
        List of formatted coordinate strings
    """
    formatted = []
    for coord in coordinates:
        if isinstance(coord, str):
            parts = coord.strip().split()
            if len(parts) == 4:
                atom, x, y, z = parts[0], float(parts[1]), float(parts[2]), float(parts[3])
                
                # Convert from Bohr to Angstrom if needed
                # BDF uses Angstrom as default, so we only convert if input is in Bohr
                if units.lower() == 'bohr':
                    # Convert Bohr to Angstrom (1 Bohr = 0.529177 Angstrom)
                    x *= 0.529177
                    y *= 0.529177
                    z *= 0.529177
                
                formatted.append(f" {atom:>4s} {x:12.4f} {y:12.4f} {z:12.4f}")
            else:
                formatted.append(f" {coord}")
        else:
            formatted.append(f" {coord}")
    
    return formatted


def normalize_point_group(group: str) -> Optional[str]:
    """
    Normalize point group name for BDF input.
    
    BDF supports real representation point groups:
    - Abelian groups: C(1), C(i), C(s), C(2), C(2v), C(2h), D(2), D(2h)
    - Non-Abelian groups: C(nv), D(n), D(nh), D(nd), T(d), O, O(h), I, I(h)
    - Special groups: C(LIN) for C∞v, D(LIN) for D∞h
    
    Rules:
    1. Case-insensitive matching
    2. Auto-add parentheses if missing (e.g., 'C2v' -> 'C(2v)')
    3. Special groups: C∞v -> C(LIN), D∞h -> D(LIN)
    4. Validate against valid point groups
    
    Args:
        group: User-provided point group name
    
    Returns:
        Normalized point group name if valid, None otherwise
    """
    if not group:
        return None
    
    # Remove any existing parentheses and whitespace for processing
    group_clean = group.strip().replace('(', '').replace(')', '').upper()
    
    # Handle special groups first
    if group_clean in ['CLIN', 'CINFV', 'C∞V', 'CINFINITYV']:
        return "C(LIN)"
    elif group_clean in ['DLIN', 'DINFH', 'D∞H', 'DINFINITYH']:
        return "D(LIN)"
    
    # Try direct match first (case-insensitive, with or without parentheses)
    for valid_group in VALID_POINT_GROUPS:
        valid_clean = valid_group.replace('(', '').replace(')', '').upper()
        if group_clean == valid_clean:
            return valid_group
    
    # Try to add parentheses if missing
    if group_clean == 'CS':
        return "C(s)"
    elif group_clean == 'C1':
        return "C(1)"
    elif group_clean == 'CI':
        return "C(i)"
    elif re.match(r'^C(\d+)$', group_clean):  # C2, C3, C4, etc.
        match = re.match(r'^C(\d+)$', group_clean)
        n = match.group(1)
        return f"C({n})"
    elif re.match(r'^C(\d+)V$', group_clean):  # C2v, C3v, C4v, etc.
        match = re.match(r'^C(\d+)V$', group_clean)
        n = match.group(1)
        return f"C({n}v)"
    elif re.match(r'^C(\d+)H$', group_clean):  # C2h, C3h, C4h, etc.
        match = re.match(r'^C(\d+)H$', group_clean)
        n = match.group(1)
        return f"C({n}h)"
    elif re.match(r'^D(\d+)$', group_clean):  # D2, D3, D4, etc.
        match = re.match(r'^D(\d+)$', group_clean)
        n = match.group(1)
        return f"D({n})"
    elif re.match(r'^D(\d+)H$', group_clean):  # D2h, D3h, D4h, etc.
        match = re.match(r'^D(\d+)H$', group_clean)
        n = match.group(1)
        return f"D({n}h)"
    elif re.match(r'^D(\d+)D$', group_clean):  # D2d, D3d, D4d, etc.
        match = re.match(r'^D(\d+)D$', group_clean)
        n = match.group(1)
        return f"D({n}d)"
    elif group_clean in ['TD', 'T(D)']:
        return "T(d)"
    elif group_clean == 'O':
        return "O"
    elif group_clean in ['OH', 'O(H)']:
        return "O(h)"
    elif group_clean == 'I':
        return "I"
    elif group_clean in ['IH', 'I(H)']:
        return "I(h)"
    
    # If no match found, return None (invalid)
    return None


def should_add_saorb(config: dict) -> bool:
    """
    Determine if SAORB keyword should be added.
    
    SAORB is added only when:
    1. MCSCF or TRAINT module is present, AND
    2. No RI basis sets are used (RI-J, RI-K, RI-C, CD-RI)
    
    Args:
        config: YAML configuration dictionary
    
    Returns:
        True if SAORB should be added, False otherwise
    """
    task_type = config.get('task', {}).get('type', '')
    settings = config.get('settings', {})

    has_mcscf = (
        task_type == 'mcscf' or
        'mcscf' in settings or
        config.get('method', {}).get('type') == 'mcscf'
    )
    has_traint = (
        'traint' in settings or
        task_type == 'traint'
    )

    if not (has_mcscf or has_traint):
        return False

    compass_settings = settings.get('compass', {})
    ri_settings = compass_settings.get('ri', {})

    has_ri = (
        ri_settings.get('ri_j_basis') or
        ri_settings.get('ri_k_basis') or
        ri_settings.get('ri_c_basis') or
        ri_settings.get('cd_ri')
    )
    return not has_ri

