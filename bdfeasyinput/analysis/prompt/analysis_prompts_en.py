"""
English Analysis Prompt Templates

This module provides English prompt templates for AI-powered analysis of BDF results.
"""

from typing import Dict, List, Optional, Any


QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_EN = """You are a senior quantum chemistry computational expert specializing in analyzing output results from the BDF quantum chemistry software.

Your tasks are:
1. Analyze the quality and reliability of calculation results
2. Explain the significance of calculation results
3. Identify potential issues and warnings
4. Provide professional advice and insights
5. Explain complex quantum chemistry concepts to users in accessible language

Analysis focus:
- **Energy Analysis**: Total energy, SCF energy, relative energy, etc.
- **Geometry**: Bond lengths, bond angles, dihedral angles, symmetry, etc.
- **Convergence**: SCF convergence, geometry optimization convergence, etc.
- **Electronic Structure**: Orbital energies, HOMO-LUMO gap, electron density, etc.
- **Vibrational Analysis**: Frequencies, IR intensities, thermodynamic properties, etc.
- **Method Assessment**: Applicability of computational methods, basis set quality, etc.

Output requirements:
- Use professional but accessible language
- Provide specific numerical values and units
- Give clear conclusions and recommendations
- Point out issues that need attention
- Use Markdown format to organize content
"""


def format_geometry_en(geometry: List[Dict[str, Any]]) -> str:
    """Format geometry as string (English)"""
    if not geometry:
        return "No geometry information found"
    
    # Detect units (from first atom, assume all atoms use same unit)
    units = geometry[0].get('units', 'bohr').lower() if geometry else 'bohr'
    
    # Select label based on unit
    if units == 'bohr':
        unit_label = "Bohr (atomic units, 1 Bohr ≈ 0.529177 Å)"
    elif units == 'angstrom' or units == 'ang':
        unit_label = "Angstrom (Å)"
    else:
        unit_label = f"{units} (unspecified)"
    
    lines = [f"Atomic coordinates (units: {unit_label}):"]
    lines.append("")
    lines.append("  Atom      X              Y              Z")
    lines.append("  " + "-" * 50)
    for atom in geometry:
        element = atom.get('element', '?')
        x = atom.get('x', 0.0)
        y = atom.get('y', 0.0)
        z = atom.get('z', 0.0)
        lines.append(f"  {element:3s}  {x:12.6f}  {y:12.6f}  {z:12.6f}")
    
    lines.append("")
    lines.append("  Note: Coordinates are extracted from 'Atom Cartcoord(Bohr)' section in BDF output")
    
    return "\n".join(lines)


def format_frequencies_en(frequencies: List[float]) -> str:
    """Format frequencies as string (English)"""
    if not frequencies:
        return "No frequency information found"
    
    lines = ["Vibrational frequencies (units: cm⁻¹):"]
    for i, freq in enumerate(frequencies, 1):
        lines.append(f"  {i:3d}. {freq:10.2f} cm⁻¹")
    
    return "\n".join(lines)


def format_tddft_calculations_en(tddft: List[Dict[str, Any]]) -> str:
    """Format TDDFT calculation results as string (English)"""
    if not tddft:
        return "No TDDFT calculation results found"
    
    lines = []
    for idx, calc in enumerate(tddft, 1):
        lines.append(f"TDDFT Calculation Block {idx}:")
        
        # Method description
        approx_method = calc.get('approximation_method')
        itda = calc.get('itda')
        if approx_method:
            lines.append(f"  - Method: {approx_method}")
        if itda is not None:
            lines.append(f"  - ITDA parameter: {itda}")
            if itda == 1:
                lines.append("    Note: Using TDA approximation (Tamm–Dancoff Approximation)")
            elif itda == 0:
                lines.append("    Note: Using standard TDDFT (Time-Dependent Density Functional Theory)")
        
        # Other parameters
        isf = calc.get('isf')
        is_spin_flip = (isf is not None and isf != 0)
        
        if isf is not None:
            spin_dir = calc.get('spin_flip_direction')
            if spin_dir:
                lines.append(f"  - Spin-flip parameter (ISF): {isf} ({spin_dir})")
            else:
                lines.append(f"  - Spin-flip parameter (ISF): {isf}")
            
            if is_spin_flip:
                lines.append("  - ⚠️ **Spin-Flip Calculation**: This is a spin-flip TDDFT calculation")
                lines.append("  - Note: When ISF ≠ 0, this TDDFT block is a spin-flip calculation")
                lines.append("  - Feature: The excited state has a flipped spin relative to the reference state")
                lines.append("  - **Important**: Oscillator strengths in spin-flip calculations are necessarily zero (normal physical phenomenon)")
                lines.append("    - Reason: Electric dipole operator does not involve spin, so spin-flip transition oscillator strengths are theoretically zero")
                lines.append("    - If oscillator strength is 0, this is expected, not a calculation error")
        
        ialda = calc.get('ialda')
        if ialda is not None:
            lines.append(f"  - IALDA parameter: {ialda}")
        
        method = calc.get('method')
        if method:
            lines.append(f"  - Method type: {method}")
        
        # Excited state information
        states = calc.get('states', [])
        if states:
            lines.append(f"  - Number of excited states: {len(states)}")
            if is_spin_flip:
                lines.append("  - ⚠️ This is a Spin-Flip calculation: ISF ≠ 0, oscillator strengths are necessarily zero (normal)")
            lines.append("  - First 3 excited states:")
            for state in states[:3]:
                idx_state = state.get('index', '?')
                energy = state.get('energy_ev', 0)
                wavelength = state.get('wavelength_nm', 0)
                osc = state.get('oscillator_strength', 0)
                osc_str = f"{osc:.6f}"
                if is_spin_flip and osc == 0:
                    osc_str += " (spin-flip, normal)"
                lines.append(f"    State {idx_state}: Energy = {energy:.4f} eV, "
                           f"Wavelength = {wavelength:.2f} nm, "
                           f"Oscillator strength = {osc_str}")
        lines.append("")
    
    return "\n".join(lines)


def build_analysis_prompt_en(
    parsed_data: Dict[str, Any],
    input_file: Optional[str] = None,
    error_file: Optional[str] = None,
    task_type: Optional[str] = None
) -> str:
    """
    Build analysis prompt (English)
    
    Args:
        parsed_data: Parsed output data
        input_file: Input file path (optional)
        error_file: Error file path (optional)
        task_type: Task type (optional)
    
    Returns:
        Complete analysis prompt
    """
    prompt_parts = []
    
    prompt_parts.append("Please analyze the following BDF quantum chemistry calculation results:\n")
    
    # Task type
    if task_type:
        prompt_parts.append(f"**Task Type**: {task_type}\n")
    
    # Energy information
    energy = parsed_data.get('energy')
    scf_energy = parsed_data.get('scf_energy')
    converged = parsed_data.get('converged', False)
    properties = parsed_data.get('properties', {})
    
    prompt_parts.append("**Calculation Results**:")
    if energy is not None:
        prompt_parts.append(f"- Total energy (E_tot): {energy:.10f} Hartree")
    if scf_energy is not None and scf_energy != energy:
        prompt_parts.append(f"- SCF energy: {scf_energy:.10f} Hartree")
    prompt_parts.append(f"- SCF convergence: {'Yes' if converged else 'No'}")
    prompt_parts.append(f"- Calculation status: {'Success' if converged else 'Not converged or failed'}\n")
    
    # SCF energy components
    if properties:
        prompt_parts.append("**SCF Energy Component Descriptions**:")
        prompt_parts.append("")
        prompt_parts.append("Key energy definitions in BDF output:")
        prompt_parts.append("- **E_tot**: Total electronic energy in BO approximation, includes nuclear repulsion")
        prompt_parts.append("- **E_ele**: Electronic energy, excluding nuclear repulsion")
        prompt_parts.append("- **E_nn**: Nuclear repulsion energy")
        prompt_parts.append("- **Relation**: E_tot = E_ele + E_nn")
        prompt_parts.append("")
        prompt_parts.append("- **E_1e**: One-electron energy")
        prompt_parts.append("- **E_ne**: Nuclear-electron attraction potential energy")
        prompt_parts.append("- **E_kin**: Electronic kinetic energy")
        prompt_parts.append("- **Relation**: E_1e = E_ne + E_kin")
        prompt_parts.append("")
        prompt_parts.append("- **E_ee**: Two-electron interaction energy, including Coulomb repulsion and electron exchange")
        prompt_parts.append("- **E_xc**: Exchange-correlation energy from DFT calculation")
        prompt_parts.append("- **Virial Ratio**: For non-relativistic all-electron systems, should be close to 2.0")
        prompt_parts.append("")
        
        # Display actual values
        e_tot = properties.get('E_tot') or energy
        e_ele = properties.get('E_ele')
        e_nn = properties.get('E_nn')
        e_1e = properties.get('E_1e')
        e_ne = properties.get('E_ne')
        e_kin = properties.get('E_kin')
        e_ee = properties.get('E_ee')
        e_xc = properties.get('E_xc')
        virial_ratio = properties.get('virial_ratio')
        
        if e_tot is not None or e_ele is not None or e_nn is not None:
            prompt_parts.append("Actual values:")
            if e_tot is not None:
                prompt_parts.append(f"  E_tot = {e_tot:.10f} Hartree")
            if e_ele is not None:
                prompt_parts.append(f"  E_ele = {e_ele:.10f} Hartree")
            if e_nn is not None:
                prompt_parts.append(f"  E_nn = {e_nn:.10f} Hartree")
            prompt_parts.append("")
        
        if e_1e is not None or e_ne is not None or e_kin is not None:
            if e_ne is not None:
                prompt_parts.append(f"  E_ne = {e_ne:.10f} Hartree")
            if e_kin is not None:
                prompt_parts.append(f"  E_kin = {e_kin:.10f} Hartree")
            if e_1e is not None:
                prompt_parts.append(f"  E_1e = {e_1e:.10f} Hartree")
            prompt_parts.append("")
        
        if e_ee is not None:
            prompt_parts.append(f"  E_ee = {e_ee:.10f} Hartree")
        if e_xc is not None:
            prompt_parts.append(f"  E_xc = {e_xc:.10f} Hartree")
        if virial_ratio is not None:
            prompt_parts.append(f"  Virial Ratio = {virial_ratio:.6f}")
            if abs(virial_ratio - 2.0) < 0.01:
                prompt_parts.append("  (close to 2.0, good calculation quality)")
            else:
                diff = abs(virial_ratio - 2.0)
                prompt_parts.append(f"  (deviates from 2.0 by {diff:.4f}, needs checking)")
        prompt_parts.append("")
        
        # SCF convergence criteria
        thresh_ene = properties.get('scf_conv_thresh_ene')
        thresh_den = properties.get('scf_conv_thresh_den')
        final_deltae = properties.get('final_deltae')
        final_deltad = properties.get('final_deltad')
        scf_iterations = properties.get('scf_iterations')
        scf_iter_when_diis_closed = properties.get('scf_iter_when_diis_closed')
        
        if thresh_ene is not None or thresh_den is not None or final_deltae is not None or final_deltad is not None or scf_iterations is not None:
            prompt_parts.append("**SCF Convergence Criteria and Results**:")
            prompt_parts.append("")
            
            if scf_iterations is not None:
                prompt_parts.append("**SCF Iteration Information**:")
                prompt_parts.append(f"- **SCF iterations**: {scf_iterations} iterations")
                if scf_iter_when_diis_closed is not None:
                    prompt_parts.append(f"- DIIS/VSHIFT closed after iteration {scf_iter_when_diis_closed}")
                    prompt_parts.append(f"- Note: Since DIIS/VSHIFT is closed after convergence, actual calculation used {scf_iterations} iterations")
                prompt_parts.append("")
            
            prompt_parts.append("Convergence criteria (thresholds):")
            prompt_parts.append("- **THRENE**: Energy convergence threshold, energy change must be smaller than this value")
            prompt_parts.append("- **THRDEN**: Density matrix convergence threshold, density matrix RMS change must be smaller than this value")
            prompt_parts.append("")
            
            if thresh_ene is not None:
                prompt_parts.append(f"  THRENE = {thresh_ene:.2e} Hartree")
            if thresh_den is not None:
                prompt_parts.append(f"  THRDEN = {thresh_den:.2e}")
            prompt_parts.append("")
            
            if final_deltae is not None or final_deltad is not None:
                prompt_parts.append("Actual convergence values:")
                if final_deltae is not None:
                    prompt_parts.append(f"  Final DeltaE = {final_deltae:.2e} Hartree")
                if final_deltad is not None:
                    prompt_parts.append(f"  Final DeltaD = {final_deltad:.2e}")
                prompt_parts.append("")
        
        # HOMO-LUMO gap
        homo_lumo_gap = properties.get('homo_lumo_gap')
        homo_alpha = properties.get('homo_alpha')
        lumo_alpha = properties.get('lumo_alpha')
        homo_beta = properties.get('homo_beta')
        lumo_beta = properties.get('lumo_beta')
        
        if homo_lumo_gap or homo_alpha or lumo_alpha or homo_beta or lumo_beta:
            prompt_parts.append("**HOMO-LUMO Orbital Energies**:")
            prompt_parts.append("")
            if homo_alpha or lumo_alpha:
                prompt_parts.append("**Alpha orbitals**:")
                if homo_alpha:
                    prompt_parts.append(f"- **HOMO**: {homo_alpha['au']:.6f} au ({homo_alpha['ev']:.4f} eV)")
                if lumo_alpha:
                    prompt_parts.append(f"- **LUMO**: {lumo_alpha['au']:.6f} au ({lumo_alpha['ev']:.4f} eV)")
                prompt_parts.append("")
            
            if homo_beta or lumo_beta:
                prompt_parts.append("**Beta orbitals**:")
                if homo_beta:
                    prompt_parts.append(f"- **HOMO**: {homo_beta['au']:.6f} au ({homo_beta['ev']:.4f} eV)")
                if lumo_beta:
                    prompt_parts.append(f"- **LUMO**: {lumo_beta['au']:.6f} au ({lumo_beta['ev']:.4f} eV)")
                prompt_parts.append("")
            
            if homo_lumo_gap:
                gap_au = homo_lumo_gap.get('au')
                gap_ev = homo_lumo_gap.get('ev')
                prompt_parts.append(f"**HOMO-LUMO gap**: {gap_au:.6f} au ({gap_ev:.4f} eV)")
                prompt_parts.append("")
                
                # Give suggestions based on gap value
                if gap_ev is not None:
                    if gap_ev < 0.5:
                        prompt_parts.append("⚠️ **Warning**: HOMO-LUMO gap is very small (< 0.5 eV), SCF convergence may be difficult.")
                        prompt_parts.append("")
                        prompt_parts.append("**Improvement suggestions**:")
                        prompt_parts.append("- Add `vshift` keyword in input file to shift virtual orbital energies")
                        prompt_parts.append("- For example: Add `vshift 0.1` or larger value in SCF module")
                        prompt_parts.append("- This helps improve SCF convergence")
                        prompt_parts.append("")
                    elif gap_ev < 1.0:
                        prompt_parts.append("⚠️ **Note**: HOMO-LUMO gap is small (< 1.0 eV), if SCF convergence is difficult, consider:")
                        prompt_parts.append("- Adding `vshift` keyword in input file to shift virtual orbital energies")
                        prompt_parts.append("")
                    else:
                        prompt_parts.append("✓ HOMO-LUMO gap is normal, SCF convergence should not be problematic")
                        prompt_parts.append("")
    
    # Geometry
    geometry = parsed_data.get('geometry', [])
    if geometry:
        prompt_parts.append("**Geometry**:")
        prompt_parts.append(format_geometry_en(geometry))
        prompt_parts.append("")
    
    # Frequencies
    frequencies = parsed_data.get('frequencies', [])
    if frequencies:
        prompt_parts.append("**Vibrational Frequencies**:")
        prompt_parts.append(format_frequencies_en(frequencies))
        prompt_parts.append("")
    
    # TDDFT information
    tddft = parsed_data.get('tddft', [])
    if tddft:
        prompt_parts.append("**TDDFT Calculation Results**:")
        prompt_parts.append(format_tddft_calculations_en(tddft))
    
    # Non-equilibrium solvation correction (cLR)
    solvent_corr = properties.get('solvent_noneq_corrections')
    if solvent_corr:
        prompt_parts.append("")
        prompt_parts.append("**Non-equilibrium Solvation (cLR) Correction**:")
        for corr in solvent_corr:
            st = corr.get("state_index")
            cv = corr.get("corrected_vertical_energy_ev")
            ne = corr.get("noneq_solvation_free_energy_ev")
            eq = corr.get("eq_solvation_free_energy_ev")
            clr = corr.get("excitation_energy_correction_ev")
            prompt_parts.append(f"- State {st}: Corrected vertical absorption = {cv:.4f} eV; "
                                f"Nonequilibrium solvation free energy = {ne:.4f} eV; "
                                f"Equilibrium solvation free energy = {eq:.4f} eV; "
                                f"cLR correction = {clr:.4f} eV")
    
    # Non-equilibrium solvation method note
    noneq_method = properties.get('solvent_noneq_method')
    if noneq_method:
        prompt_parts.append("")
        if noneq_method == "clr_linear_response":
            prompt_parts.append("This calculation uses cLR (linear response) non-equilibrium solvation correction.")
        elif noneq_method == "ptSS_state_specific":
            prompt_parts.append("This calculation uses ptSS (state-specific, resp-based perturbative) non-equilibrium solvation correction.")
        
        # TDDFT JK Memory Information
        if tddft:
            first_calc = tddft[0]  # Get memory info from first block (usually same for all blocks)
            jk_estimated = first_calc.get('jk_estimated_memory_mb')
            jk_max = first_calc.get('jk_max_memory_mb')
            roots_per_pass = first_calc.get('roots_per_pass')
            n_exit = first_calc.get('n_exit')
            
            if jk_estimated is not None or jk_max is not None or roots_per_pass is not None:
                prompt_parts.append("")
                prompt_parts.append("**TDDFT JK Operator Memory Information**:")
                if jk_estimated is not None:
                    prompt_parts.append(f"- Estimated memory for JK operator: {jk_estimated:.3f} MB")
                    prompt_parts.append("  - TDDFT first estimates memory needed to calculate JK operator")
                if jk_max is not None:
                    prompt_parts.append(f"- Maximum memory to calculate JK operator: {jk_max:.3f} MB")
                    prompt_parts.append("  - Maximum memory setting for calculating JK operator")
                if roots_per_pass is not None:
                    prompt_parts.append(f"- Roots per pass: {roots_per_pass}")
                    if first_calc.get('itda') == 1:
                        prompt_parts.append("  - This is TDA calculation. TDA can calculate 2x more roots than RPA")
                    else:
                        prompt_parts.append("  - This is TDDFT calculation")
                if n_exit is not None:
                    prompt_parts.append(f"- Requested roots per irrep: {n_exit}")
                    if roots_per_pass is not None and n_exit > roots_per_pass:
                        prompt_parts.append("  - ⚠️ Requested roots per irrep is greater than roots per pass")
                        prompt_parts.append("  - Recommendation: Use MEMJKOP keyword to increase memory for better efficiency")
                        prompt_parts.append("  - MEMJKOP parameter format: \"int+M\", e.g., 1024M, means 1024 MB per OpenMP thread")
                        prompt_parts.append("  - Actual memory usage = value × number of OpenMP threads")
    
    # Warnings
    warnings = parsed_data.get('warnings', [])
    if warnings:
        prompt_parts.append("**Warning Messages**:")
        for i, warning in enumerate(warnings, 1):
            prompt_parts.append(f"{i}. {warning}")
        prompt_parts.append("")
    
    # Errors
    errors = parsed_data.get('errors', [])
    if errors:
        prompt_parts.append("**Error Messages**:")
        for i, error in enumerate(errors, 1):
            prompt_parts.append(f"{i}. {error}")
        prompt_parts.append("")
    
    # Input file information
    if input_file:
        prompt_parts.append(f"**Input File**: {input_file}\n")
    
    # Error file information
    if error_file:
        prompt_parts.append(f"**Error File**: {error_file}\n")
    
    prompt_parts.append("""
Please provide the following analysis content:

1. **Calculation Summary**: Briefly summarize the calculation results
2. **Energy Analysis**: Analyze the reasonableness and significance of energies
3. **Geometry Analysis** (if applicable): Analyze bond lengths, bond angles, and other structural features
4. **Convergence Analysis**: Assess convergence quality
5. **Vibrational Analysis** (if applicable): Analyze frequencies and thermodynamic properties
6. **TDDFT Analysis** (if applicable): Analyze excited state energies, oscillator strengths, computational methods (TDA vs TDDFT), etc.
7. **Method Assessment**: Evaluate the applicability of computational methods and basis sets
8. **Professional Recommendations**: Provide improvement suggestions and recommendations for further calculations
9. **Expert Insights**: Provide in-depth professional analysis

Please use Markdown format to organize content with clear headings and lists.
""")
    
    return "\n".join(prompt_parts)
