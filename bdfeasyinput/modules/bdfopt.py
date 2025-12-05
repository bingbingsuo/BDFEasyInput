"""
BDFOPT Module Generator

This module generates the BDFOPT block for BDF input files.
"""

from typing import Dict, Any, List


def generate_bdfopt_block(config: Dict[str, Any]) -> List[str]:
    """
    Generate BDFOPT module block for geometry optimization.
    
    Reference: BDF Optimization manual
    
    Args:
        config: YAML configuration dictionary
    
    Returns:
        List of lines for BDFOPT block
    """
    lines = ["$BDFOPT"]
    
    settings = config.get('settings', {})
    opt_settings = settings.get('geometry_optimization', {})
    
    # Solver: 0=DL-FIND, 1=BDF built-in optimizer
    solver = opt_settings.get('solver', 1)
    lines.append("solver")
    lines.append(f" {solver}")
    
    # Optimization type: iopt
    opt_type = opt_settings.get('optimization_type')
    if opt_type == 'transition_state':
        lines.append("iopt")
        lines.append(" 10")
    elif opt_type == 'minimum':
        lines.append("iopt")
        lines.append(" 3")
    
    # Hessian calculation mode
    hess_settings = opt_settings.get('hessian', {})
    hess_mode = hess_settings.get('mode')
    if hess_mode:
        lines.append("hess")
        if hess_mode == 'only':
            lines.append(" only")
        elif hess_mode == 'init':
            lines.append(" init")
        elif hess_mode == 'final':
            lines.append(" final")
        elif hess_mode == 'init+final' or hess_mode == 'init_final':
            lines.append(" init+final")
    
    # Convergence tolerances
    tolerance = opt_settings.get('tolerance', {})
    tolgrad = tolerance.get('gradient')
    if tolgrad:
        lines.append("tolgrad")
        lines.append(f" {tolgrad}")
    
    tolstep = tolerance.get('step')
    if tolstep:
        lines.append("tolstep")
        lines.append(f" {tolstep}")
    
    tolene = tolerance.get('energy')
    if tolene:
        lines.append("tolene")
        lines.append(f" {tolene}")
    
    # Trust radius
    trust = opt_settings.get('trust')
    if trust is not None:
        lines.append("trust")
        lines.append(f" {trust}")
    
    # Max iterations
    max_iterations = opt_settings.get('max_iterations')
    if max_iterations:
        lines.append("maxcycle")
        lines.append(f" {max_iterations}")
    
    # Remove imaginary frequencies
    if opt_settings.get('remove_imaginary_frequencies'):
        lines.append("rmimag")
    
    # Dimer method (for transition state, requires solver=0)
    if opt_settings.get('dimer'):
        lines.append("dimer")
    
    # O1NumHess
    if opt_settings.get('o1numhess'):
        lines.append("o1numhess")
        ncorepergrad = opt_settings.get('ncorepergrad')
        if ncorepergrad:
            lines.append("ncorepergrad")
            lines.append(f" {ncorepergrad}")
    
    # ParHess (parallel Hessian calculation)
    if opt_settings.get('parhess'):
        lines.append("parhess")
    
    # Recalculate Hessian periodically
    recalchess = opt_settings.get('recalchess')
    if recalchess:
        lines.append("recalchess")
        lines.append(f" {recalchess}")
    
    # Read Hessian from file
    if opt_settings.get('read_hessian'):
        lines.append("readhess")
    
    # Restart Hessian calculation
    if opt_settings.get('restart_hessian'):
        lines.append("restarthess")
    
    # QRRHO (for large systems, noncovalent interactions)
    if opt_settings.get('qrrho'):
        lines.append("qrrho")
    
    # Thermal chemistry settings
    thermo = opt_settings.get('thermochemistry', {})
    # Support both 'frequency_scale' and 'scale_factor' for backward compatibility
    scale = thermo.get('frequency_scale') or thermo.get('scale_factor')
    if scale is not None:
        lines.append("scale")
        lines.append(f" {scale}")
    
    temp = thermo.get('temperature')
    if temp is not None:
        lines.append("temp")
        lines.append(f" {temp}")
    
    press = thermo.get('pressure')
    if press is not None:
        lines.append("press")
        lines.append(f" {press}")
    
    ndeg = thermo.get('electronic_degeneracy')
    if ndeg is not None:
        lines.append("ndeg")
        lines.append(f" {ndeg}")
    
    # Constraints
    constraints = opt_settings.get('constraints', [])
    if constraints:
        lines.append("constrain")
        lines.append(f" {len(constraints)}")
        for constraint in constraints:
            atoms = constraint.get('atoms', [])
            value = constraint.get('value')
            if value is not None:
                atoms_str = ' '.join(str(a) for a in atoms)
                lines.append(f" {atoms_str} = {value}")
            else:
                atoms_str = ' '.join(str(a) for a in atoms)
                lines.append(f" {atoms_str}")
    
    # Frozen atoms
    frozen = opt_settings.get('frozen', [])
    if frozen:
        lines.append("frozen")
        lines.append(f" {len(frozen)}")
        for frozen_item in frozen:
            atom = frozen_item.get('atom')
            freeze_type = frozen_item.get('type', -1)
            lines.append(f" {atom} {freeze_type}")
    
    # Scan
    scan = opt_settings.get('scan')
    if scan:
        lines.append("scan")
        scan_dims = scan.get('dimensions', 1)
        scan_points = scan.get('points')
        if scan_points:
            lines.append(f" {scan_dims} {scan_points}")
        else:
            lines.append(f" {scan_dims}")
        
        coordinates = scan.get('coordinates', [])
        for coord in coordinates:
            atoms = coord.get('atoms', [])
            start = coord.get('start')
            end = coord.get('end')
            interval = coord.get('interval')
            if start is not None and end is not None and interval is not None:
                atoms_str = ' '.join(str(a) for a in atoms)
                lines.append(f" {atoms_str} = {start} {end} {interval}")
            elif scan_points:
                # Scattered points
                atoms_str = ' '.join(str(a) for a in atoms)
                lines.append(f" {atoms_str}")
                values = coord.get('values', [])
                for val in values:
                    lines.append(f" {val}")
            else:
                atoms_str = ' '.join(str(a) for a in atoms)
                lines.append(f" {atoms_str}")
    
    # Multi-state optimization
    multistate = opt_settings.get('multistate')
    if multistate:
        lines.append("multistate")
        nstates = multistate.get('nstates', 2)
        soc_constant = multistate.get('soc_constant', 400)
        lines.append(f" {nstates}soc  {soc_constant}")
    
    # CI/MECP optimization
    imulti = opt_settings.get('imulti')
    if imulti:
        lines.append("imulti")
        lines.append(f" {imulti}")
    
    if opt_settings.get('noncoupl'):
        lines.append("noncoupl")
    
    # CI-NEB
    neb = opt_settings.get('neb')
    if neb:
        lines.append("neb-block")
        if neb.get('crude'):
            lines.append(" crude")
        nebmode = neb.get('nebmode')
        if nebmode is not None:
            lines.append("nebmode")
            lines.append(f"  {nebmode}")
        nimage = neb.get('nimage')
        if nimage:
            lines.append("nimage")
            lines.append(f"  {nimage}")
        lines.append("end neb")
        
        geometry2 = neb.get('geometry2')
        if geometry2:
            lines.append("geometry2")
            for coord_line in geometry2:
                lines.append(f" {coord_line}")
            lines.append("end geometry2")
    
    lines.append("$END")
    
    return lines

