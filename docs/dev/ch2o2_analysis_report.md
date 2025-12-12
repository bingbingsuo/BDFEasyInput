# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-12 16:29:33

## Calculation Summary

| Item | Value / Comment |
|------|-----------------|
| **Task** | TD‑DFT (linear‑response) on formaldehyde (CH₂O) |
| **Electronic SCF** | Converged in 9 iterations, ΔE = **‑1.66 × 10⁻¹⁰ Ha**, ΔD = **6.99 × 10⁻⁸** |
| **Total electronic energy** | **Eₑₗₑ = –145.6575404100 Ha** |...

## Energy Analysis

** | **Eₑₗₑ = –145.6575404100 Ha** |
| **Nuclear‑repulsion energy** | **Eₙₙ = 31.2516354500 Ha** |
| **Total (BO) energy** | **Eₜₒₜ = –114.4059049600 Ha** |
| **Virial ratio** | **2.0042** (excellent) |
| **HOMO / LUMO** | –0.264558 Ha (‑7.20 eV) / –0.044522 Ha (‑1.21 eV) |
| **HOMO‑LUMO gap** | **0.220 Ha = 5.99 eV** |
| **Excited states (first 3)** | 1) 3.914 eV (316.8 nm), f = 0.000 <br>2) 8.977 eV (138.1 nm), f = 0.0034 <br>3) 9.450 eV (131.2 nm), f = 0.1602 |
| **Solvation** | cLR (linear‑response) non‑equilibrium PCM correction applied |
| **Memory usage** | JK operator ≈ 0.35 MB (well below the 512 MB limit) |
| **Status** | **Success** – no errors reported |...

## Geometry Analysis

Analysis  

Coordinates are given in Bohr (1 Bohr = 0.529177 Å).

| Bond / Angle | Bohr | Å | Comment |
|--------------|------|----|---------|
| **C–O** | 2.30358 | **1.218 Å** | Typical C=O double‑bond length (≈ 1.21 Å). |
| **C–H (both)** | 2.041 Bohr | **1.080 Å** | Standard C–H bond (≈ 1.09 Å). |
| **H–C–H angle** | – | **120.0°** | Exact trigonal planar geometry, as expected for sp² carbon. |
| **O–C–H angles** | – | **120.0°** (by symmetry) | Consistent with a planar CH₂O molecule. |...

## Convergence Analysis

, a physically sensible virial ratio, and a reasonable electronic structure for formaldehyde.

---

## Raw Data

### Geometry

**Coordinate Units**: Bohr (atomic units, 1 Bohr ≈ 0.529177 Å)

**Atomic Coordinates**:

| Atom | X | Y | Z |
|------|---|-----|-----|
| C | 0.000000 | 0.000000 | -1.024232 |
| O | 0.000000 | 0.000000 | 1.279345 |
| H | 0.000000 | 1.766894 | -2.044684 |
| H | 0.000000 | -1.766894 | -2.044684 |

**Note**:
- Coordinates extracted from 'Atom Cartcoord(Bohr)' section in BDF output
- Units: Bohr (atomic units)
- 1 Bohr = 0.529177 Å

- **Total Energy (E_tot)**: -114.4059049600 Hartree
- **SCF Energy**: -145.6575404100 Hartree
- **Convergence Status**: Converged

### HOMO-LUMO Orbital Energies

**Alpha Orbitals**:
- **HOMO**: -0.264558 au (-7.1990 eV)
- **LUMO**: -0.044522 au (-1.2115 eV)

**HOMO-LUMO gap**: 0.220036 au (5.9875 eV)

✓ HOMO-LUMO gap is normal, SCF convergence should not be problematic


### SCF Energy Component Descriptions

#### Total Energy Relation

- **E_tot**: Total electronic energy in BO approximation, includes nuclear repulsion
- **E_ele**: Electronic energy, excluding nuclear repulsion
- **E_nn**: Nuclear repulsion energy
- **Relation**: E_tot = E_ele + E_nn

  - E_ele = -145.6575404100 Hartree
  - E_nn = 31.2516354500 Hartree
  - E_tot = -114.4059049600 Hartree
  - Verification: E_ele + E_nn = -114.4059049600 Hartree (Difference: 0.00e+00)

#### One-Electron Energy Relation

- **E_1e**: One-electron energy
- **E_ne**: Nuclear-electron attraction potential energy
- **E_kin**: Electronic kinetic energy
- **Relation**: E_1e = E_ne + E_kin

  - E_ne = -331.2594548900 Hartree
  - E_kin = 113.9268680100 Hartree
  - E_1e = -217.3325868700 Hartree
  - Verification: E_ne + E_kin = -217.3325868800 Hartree (Difference: 1.00e-08)

#### Two-Electron and Exchange-Correlation Energy

- **E_ee**: Two-electron interaction energy = 83.5330870800 Hartree
  - Includes Coulomb repulsion and electron exchange
- **E_xc**: Exchange-correlation energy = -11.8514749900 Hartree
  - From DFT exchange-correlation functional contribution

#### Virial Ratio

- **Virial Ratio** = 2.004205
  - For non-relativistic all-electron systems, virial ratio should be close to 2.0
  - ✓ Virial ratio close to 2.0 indicates good calculation quality

#### SCF Convergence Criteria and Results

**SCF Iteration Information**:
- **SCF Iterations**: 9 iterations
- DIIS/VSHIFT closed after iteration 8
- Note: Since DIIS/VSHIFT is closed after convergence, actual calculation used 9 iterations

**Convergence Criteria (Thresholds)**:
- **THRENE** (Energy convergence threshold) = 1.00e-08 Hartree
  - Energy change must be smaller than this value
- **THRDEN** (Density matrix convergence threshold) = 5.00e-06
  - Density matrix RMS change must be smaller than this value

**Actual Convergence Values**:
- **Final Energy Change** = -1.66e-10 Hartree
  - ✓ Meets convergence criteria (|DeltaE| = 1.66e-10 < 1.00e-08)
- **Final Density Matrix Change** = 6.99e-08
  - ✓ Meets convergence criteria (|DeltaD| = 6.99e-08 < 5.00e-06)

#### Dipole Moment

- **X Component**: -0.000000 Debye
- **Y Component**: -0.000000 Debye
- **Z Component**: -2.917200 Debye
- **Total Dipole Moment**: 2.917200 Debye


#### Solvent Effect Information

- Note: Implicit solvent model was used in the calculation

- **Non-equilibrium Solvation Method**: cLR: non-equilibrium linear response (solvent LR correction)
- **Solvent Model Method**: IEFPCM
- **Solvent Name**: User
- **Dielectric Constant**: 78.355300
- **Optical Dielectric Constant**: 1.777800
- **Method of Tessellation**: SWIG
- **Type of Radius**: Default
- **Accuracy of Mesh**: MEDIUM
- **Number of Tesseraes**: 690

**Note**: Note: Implicit solvent effect was used in SCF calculation


### TDDFT Calculation Results

#### TDDFT Calculation Block 1

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 0.354 MB
    - Note: TDDFT first estimates memory needed to calculate JK operator
  - **Maximum Memory to Calculate JK Operator**: 512.000 MB
    - Note: Maximum memory setting for calculating JK operator
  - **Roots per Pass for RPA**: 8
    - Note: For TDDFT calculation, maximum roots per integral calculation pass
  - **Roots per Pass for TDA**: 16
    - Note: For TDA calculation, maximum roots per integral calculation pass. TDA can calculate 2x more roots than RPA
  - **Roots per Pass** (current calculation): 8
  - **Requested Roots per Irrep**: 8

  - ✓ Requested roots are within roots per pass limit, calculation efficiency is good
- **Number of Excited States**: 8

  First 5 Excited States:
    - State 1: Energy = 3.9143 eV, Wavelength = 316.75 nm, Oscillator Strength = 0.000000
    - State 2: Energy = 8.9765 eV, Wavelength = 138.12 nm, Oscillator Strength = 0.003400
    - State 3: Energy = 9.4502 eV, Wavelength = 131.20 nm, Oscillator Strength = 0.160200
    - State 4: Energy = 9.9393 eV, Wavelength = 124.74 nm, Oscillator Strength = 0.085900
    - State 5: Energy = 10.5316 eV, Wavelength = 117.73 nm, Oscillator Strength = 0.000000


## Professional Recommendations

1. ------|-------------------|
2. *Systematic blue‑shift of π → π\*** | Use a **range‑separated hybrid** (e.g., CAM‑B3LYP, ωB97X‑D) or a **global hybrid with higher exact‑exchange** (e.g., PBE0). |
3. *Rydberg/charge‑transfer states** | Add **diffuse functions** (aug‑type basis, e.g., aug‑cc‑pVTZ) to describe the loosely bound electron. |
4. *Solvent model** | Verify the PCM parameters (dielectric constant, cavity) match the experimental solvent; consider **state‑specific PCM** if large solvatochromic shifts are expected. |
5. *Number of roots** | For a complete UV‑Vis spectrum, request **≥ 20–30 excited states** (or up to 6 eV above the highest experimental band). |
6. *Triplet states** | Run a separate **triplet TDDFT** calculation (or use TDA) to obtain intersystem crossing energies. |
7. --

## Expert Insights

Insights  

- **Virial Ratio as a Quality Metric** – The virial ratio of 2.004 is an often‑overlooked sanity check. Values deviating by > 0.05 usually signal an incomplete SCF or a problem with the integration grid. Here the ratio is spot‑on, confirming that the kinetic and potential contributions are balanced.  

- **HOMO‑LUMO Gap vs. Excitation Energies** – The computed gap (5.99 eV) is smaller than the first bright π → π\* transition (≈ 9.45 eV) because the lowest singlet excited state is *n → π\** and is essentially forbidden (f ≈ 0). This illustrates why the HOMO‑LUMO gap is not a reliable predictor of UV‑Vis absorption maxima for molecules with non‑bonding orbitals.  

- **Effect of Solvent on n → π\*** – In polar solvents, the n → π\* transition often experiences a **blue‑shift** due to stabilization of the π\* orbital relative to the non‑bonding n orbital. The cLR approach used here treats the solvent as frozen during the electronic transition, which is appropriate for vertical excitation but may underestimate solvent relaxation effects. For a more realistic solvatochromic shift, a **state‑specific PCM** or **explicit solvent shell** could be employed.  

- **Memory Footprint and Scaling** – The reported JK‑operator memory (0.354 MB) indicates the calculation is using a **density‑fitting (RI) or Cholesky‑decomposed** Coulomb algorithm, which scales as O(N²) rather than O(N³). This is why a modest workstation can handle TDDFT on a small molecule with virtually no memory pressure. When moving to larger systems, the same algorithm will keep the memory manageable, but the **CPU time** will still increase roughly with the cube of the basis size.  

- **Future Directions** – For high‑accuracy vertical excitation energies (chemical accuracy ≈ 0.1 eV), consider **EOM‑CCSD** or **ADC(2)** methods on top of a DFT‑optimized geometry. These wave‑function methods are more expensive but provide a systematic benchmark for assessing the performance of the chosen TDDFT func
