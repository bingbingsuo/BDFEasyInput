"""
SCF Module Generator

This module generates the SCF block for BDF input files.
"""

from typing import Dict, Any, List
from ..xc_functional import process_functional_input
from .passthrough import append_passthrough_lines
from ..utils import select_scf_method


def generate_scf_block(config: Dict[str, Any]) -> List[str]:
    """Generate SCF module block."""
    lines = ["$SCF"]
    
    method = config.get('method', {})
    molecule = config.get('molecule', {})
    settings = config.get('settings', {})
    scf_settings = settings.get('scf', {})
    
    method_type = method.get('type', '')
    functional = method.get('functional')
    
    # Validate required fields first
    if 'charge' not in molecule:
        raise ValueError("molecule.charge is required in YAML input")
    if 'multiplicity' not in molecule:
        raise ValueError("molecule.multiplicity is required in YAML input")
    
    multiplicity = molecule.get('multiplicity')
    charge = molecule.get('charge')
    
    # Check for spin-adapted TDDFT
    tddft_settings = settings.get('tddft', {})
    spin_adapted = tddft_settings.get('spin_adapted', False)
    
    # Select SCF method
    scf_method = select_scf_method(
        method_type, multiplicity, functional, spin_adapted
    )
    lines.append(scf_method)
    
    # DFT functional
    if method_type == 'dft' and functional:
        functional_str = process_functional_input(functional)
        lines.append("dft functional")
        lines.append(f" {functional_str}")
    
    # Occupied (only for RHF/RKS, and only if user specified)
    occupied = scf_settings.get('occupied')
    if occupied and scf_method in ['RHF', 'RKS']:
        lines.append("Occupied")
        if isinstance(occupied, list):
            occupied_str = ' '.join(str(x) for x in occupied)
        else:
            occupied_str = str(occupied)
        lines.append(f" {occupied_str}")
    
    # Charge - REQUIRED field, always add to SCF block
    lines.append("Charge")
    lines.append(f" {charge}")
    
    # Spin multiplicity - REQUIRED field, always add to SCF block
    lines.append("Spin")
    lines.append(f" {multiplicity}")

    # Always add molden keyword to save wavefunction in molden format
    lines.append("molden")

    # Convergence threshold:
    # BDF 默认能量收敛阈值为 1.0E-08，无需显式设置。
    # 若用户显式提供且与默认不同，则使用 THRENE 关键词设置。
    convergence = scf_settings.get('convergence')
    if convergence is not None:
        try:
            conv_val = float(convergence)
            if abs(conv_val - 1e-8) > 0:  # 用户提供且不同于默认
                lines.append("THRENE")
                lines.append(f" {conv_val:.1E}")
        except (TypeError, ValueError):
            pass
    
    # Solvent settings
    # Support both settings.scf.solvent and settings.solvent
    solvent_settings = scf_settings.get('solvent', {})
    if not solvent_settings:
        # Fallback to settings.solvent if settings.scf.solvent is not present
        all_settings = config.get('settings', {})
        solvent_settings = all_settings.get('solvent', {})
    
    if solvent_settings:
        # Support both 'name' and 'solvent' keys for solvent name
        solvent_name = solvent_settings.get('name') or solvent_settings.get('solvent')
        if solvent_name:
            lines.append("solvent")
            if solvent_name.lower() == 'user':
                lines.append(" user")
                dielectric = solvent_settings.get('dielectric')
                if dielectric is not None:
                    lines.append("dielectric")
                    lines.append(f" {dielectric}")
                optical_dielectric = solvent_settings.get('optical_dielectric')
                if optical_dielectric is not None:
                    lines.append("opticalDielectric")
                    lines.append(f" {optical_dielectric}")
            else:
                lines.append(f" {solvent_name}")
        
        # Solvent model
        model = solvent_settings.get('model')
        if model:
            # Map common model names to BDF keywords
            model_mapping = {
                'pcm': 'iefpcm',  # PCM typically refers to IEFPCM
                'iefpcm': 'iefpcm',
                'cosmo': 'cosmo',
                'cpcm': 'cpcm',
                'smd': 'smd',
                'ssvpe': 'ssvpe',
                'ddcosmo': 'ddcosmo',
            }
            bdf_model = model_mapping.get(model.lower(), model.lower())
            lines.append("solmodel")
            lines.append(f" {bdf_model}")
        
        # COSMO/CPCM factor K
        cosmo_factor_k = solvent_settings.get('cosmo_factor_k')
        if cosmo_factor_k is not None:
            lines.append("cosmoFactorK")
            lines.append(f" {cosmo_factor_k}")
        
        # SMD model parameters
        smd_params = solvent_settings.get('smd', {})
        if smd_params:
            refractive_index = smd_params.get('refractive_index')
            if refractive_index is not None:
                lines.append("refractiveIndex")
                lines.append(f" {refractive_index}")
            hbond_acidity = smd_params.get('hbond_acidity')
            if hbond_acidity is not None:
                lines.append("HBondAcidity")
                lines.append(f" {hbond_acidity}")
            hbond_basicity = smd_params.get('hbond_basicity')
            if hbond_basicity is not None:
                lines.append("HBondBasicity")
                lines.append(f" {hbond_basicity}")
            surface_tension = smd_params.get('surface_tension')
            if surface_tension is not None:
                lines.append("SurfaceTensionAtInterface")
                lines.append(f" {surface_tension}")
            carbon_aromaticity = smd_params.get('carbon_aromaticity')
            if carbon_aromaticity is not None:
                lines.append("CarbonAromaticity")
                lines.append(f" {carbon_aromaticity}")
            halogenicity = smd_params.get('electronegative_halogenicity')
            if halogenicity is not None:
                lines.append("ElectronegativeHalogenicity")
                lines.append(f" {halogenicity}")
        
        # Cavity settings
        cavity = solvent_settings.get('cavity', {})
        if cavity:
            cavity_type = cavity.get('type')
            if cavity_type:
                lines.append("cavity")
                lines.append(f" {cavity_type}")
            uatm = cavity.get('uatm')
            if uatm is not None:
                lines.append("uatm")
                lines.append(f" {str(uatm).lower()}")
            radius_type = cavity.get('radius_type')
            if radius_type:
                lines.append("radiusType")
                lines.append(f" {radius_type}")
            vdw_scale = cavity.get('vdW_scale')
            if vdw_scale is not None:
                lines.append("vdWScale")
                lines.append(f" {vdw_scale}")
            radii = cavity.get('radii')
            if radii:
                lines.append("radii")
                if isinstance(radii, dict):
                    radii_str = ' '.join(f"{k}={v}" for k, v in radii.items())
                    lines.append(f" {radii_str}")
                elif isinstance(radii, list):
                    radii_str = ' '.join(radii)
                    lines.append(f" {radii_str}")
            acid_h_radius = cavity.get('acid_h_radius')
            if acid_h_radius is not None:
                lines.append("acidHRadius")
                lines.append(f" {acid_h_radius}")
            cavity_ngrid = cavity.get('cavity_ngrid')
            if cavity_ngrid is not None:
                lines.append("cavityNGrid")
                lines.append(f" {cavity_ngrid}")
            cavity_precision = cavity.get('precision')
            if cavity_precision:
                lines.append("cavityPrecision")
                lines.append(f" {cavity_precision}")
        
        # Non-electrostatic solvation energy
        nonels = solvent_settings.get('non_electrostatic', {})
        if nonels:
            components = nonels.get('components', [])
            if components:
                lines.append("nonels")
                lines.append(f" {' '.join(components)}")
            solvent_atoms = nonels.get('solvent_atoms')
            if solvent_atoms:
                lines.append("solventAtoms")
                lines.append(f" {solvent_atoms}")
            solvent_rho = nonels.get('solvent_rho')
            if solvent_rho is not None:
                lines.append("solventRho")
                lines.append(f" {solvent_rho}")
            solvent_radius = nonels.get('solvent_radius')
            if solvent_radius is not None:
                lines.append("solventRadius")
                lines.append(f" {solvent_radius}")
            solvent_sas_radii = nonels.get('solvent_atomic_sas_radii')
            if solvent_sas_radii:
                lines.append("solventAtomicSASRadii")
                if isinstance(solvent_sas_radii, dict):
                    radii_str = ' '.join(f"{k}={v}" for k, v in solvent_sas_radii.items())
                    lines.append(f" {radii_str}")
            radii_for_cav = nonels.get('radii_for_cav_energy')
            if radii_for_cav:
                lines.append("radiiForCavEnergy")
                if isinstance(radii_for_cav, dict):
                    radii_str = ' '.join(f"{k}={v}" for k, v in radii_for_cav.items())
                    lines.append(f" {radii_str}")
            acid_h_radius_cav = nonels.get('acid_h_radius_for_cav_energy')
            if acid_h_radius_cav is not None:
                lines.append("acidHRadiusForCavEnergy")
                lines.append(f" {acid_h_radius_cav}")
        
        # Save COSMO data
        if solvent_settings.get('cosmosave'):
            lines.append("cosmosave")

    # Passthrough: user-defined SCF keywords
    protected = {
        'charge',
        'spin',
        'convergence',
        'occupied',
        'solvent',
        'dft',
        'functional',
        'molden',
        'threne',
    }
    append_passthrough_lines(lines, scf_settings, protected_keys=protected)

    lines.append("$END")
    
    return lines

