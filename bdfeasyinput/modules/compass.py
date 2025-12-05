"""
COMPASS Module Generator

This module generates the COMPASS block for BDF input files.
"""

from typing import Dict, Any, List
from ..utils import format_coordinates, normalize_point_group, should_add_saorb


def generate_compass_block(config: Dict[str, Any]) -> List[str]:
    """Generate COMPASS module block."""
    lines = ["$COMPASS"]
    
    molecule = config.get('molecule', {})
    settings = config.get('settings', {})
    
    # Title
    title = molecule.get('name', '')
    task = config.get('task', {})
    task_desc = task.get('description', '')
    
    if task_desc:
        title = task_desc
    elif not title:
        method = config.get('method', {})
        method_type = method.get('type', '')
        functional = method.get('functional', '')
        
        # Generate descriptive title
        if method_type == 'dft' and functional:
            title = f"H2O single point energy calculation, {functional.upper()}"
        elif method_type == 'hf':
            title = "H2O single point energy calculation"
        else:
            title = "H2O single point energy calculation"
    
    lines.append("Title")
    lines.append(f" {title}")
    
    # Basis
    # BDF supports:
    # 1. Uniform basis for all atoms: Basis [name]
    # 2. Different basis for different elements: Basis-block ... End Basis
    # 3. Custom basis file: Basis [filename] (filename must be all uppercase)
    # 4. Inline basis data: Basis-block ... inline ... end line ... End Basis
    # Note: BDF uses spherical basis functions (not Cartesian)
    # Reference: BDF Gaussian Basis Sets manual
    basis = config.get('method', {}).get('basis', '')
    compass_settings = settings.get('compass', {})
    basis_settings = compass_settings.get('basis', {})
    basis_block = basis_settings.get('block')
    
    if basis_block:
        # Use Basis-block for different elements/atoms
        lines.append("Basis-block")
        default_basis = basis_block.get('default') or basis
        if default_basis:
            lines.append(f" {default_basis}")
        
        # Element-specific basis assignments
        elements = basis_block.get('elements', {})
        for element, basis_name in elements.items():
            lines.append(f" {element} = {basis_name}")
        
        # Inline basis data (if provided)
        inline_data = basis_block.get('inline')
        if inline_data:
            lines.append("inline")
            if isinstance(inline_data, list):
                lines.extend(inline_data)
            else:
                lines.append(inline_data)
            lines.append("end line")
        
        lines.append("End Basis")
    elif basis:
        # Use simple Basis keyword for uniform basis
        lines.append("Basis")
        lines.append(f" {basis}")
    
    # Geometry
    coordinates = molecule.get('coordinates', [])
    units = molecule.get('units', 'angstrom')
    
    if coordinates:
        lines.append("Geometry")
        formatted_coords = format_coordinates(coordinates, units)
        lines.extend(formatted_coords)
        lines.append("End geometry")
        
        # Unit keyword (BDF defaults to Angstrom, but we can be explicit)
        if units.lower() == 'bohr':
            lines.append("Unit")
            lines.append(" Bohr")
        # If Angstrom, we can omit Unit keyword (BDF default)
    
    # Group (point group symmetry) or NoSymm (mutually exclusive)
    settings = config.get('settings', {})
    compass_settings = settings.get('compass', {})
    symmetry_settings = compass_settings.get('symmetry', {})
    no_symmetry = symmetry_settings.get('no_symmetry', False)
    user_group = symmetry_settings.get('group')
    
    # nosymm and group are mutually exclusive, nosymm has priority
    if no_symmetry:
        # nosymm takes priority - ignore group if both are set
        # BDF keyword is "NoSymm" (more readable than "NOSY")
        lines.append("NoSymm")
    elif user_group:
        # Only add group if nosymm is not set
        normalized_group = normalize_point_group(user_group)
        if normalized_group:
            lines.append("Group")
            lines.append(f" {normalized_group}")
        else:
            # Invalid point group - could raise warning or error
            # For now, we'll skip it but could add validation
            pass
    
    # Check keyword (always added)
    lines.append("Check")
    
    # SAORB: only add if MCSCF/TRAINT is present and no RI basis sets
    if should_add_saorb(config):
        lines.append("SAORB")
    
    lines.append("$END")
    
    return lines

