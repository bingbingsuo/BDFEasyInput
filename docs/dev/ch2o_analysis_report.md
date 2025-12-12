# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-12 15:23:55

## Calculation Summary

| Item | Value / Comment |
|------|-----------------|
| **Task** | SCF (ground‑state) + single‑point TD‑DFT (4 excited states) |
| **Total electronic energy (E<sub>tot</sub>)** | **‑114.40590496 Hartree** (includes nuclear repulsion) |
| **Electronic energy (E<sub>ele</sub>)** | **‑145.65754041 Hartree** |...

## Energy Analysis

(E<sub>tot</sub>)** | **‑114.40590496 Hartree** (includes nuclear repulsion) |
| **Electronic energy (E<sub>ele</sub>)** | **‑145.65754041 Hartree** |
| **Nuclear‑repulsion energy (E<sub>nn</sub>)** | **+31.25163545 Hartree** |
| **SCF convergence** | Converged in 9 iterations (ΔE = –2.46 × 10⁻¹⁰ Hartree, ΔD = 6.69 × 10⁻⁸) |
| **Virial ratio** | **2.004** (ideal ≈ 2.0 → high‑quality wavefunction) |
| **HOMO / LUMO** | –0.264558 au (‑7.20 eV) / –0.044522 au (‑1.21 eV) |
| **HOMO‑LUMO gap** | **0.220 au = 5.99 eV** |
| **Geometry (Bohr)** | C (0,0,‑1.024232) – O (0,0, 1.279345) – H (0, ±1.766894, ‑2.044684) |
| **TD‑DFT (R‑TD‑DFT) – 4 roots** | State 1: 3.92 eV (316 nm, f = 0.000)  <br>State 2: 8.99 eV (138 nm, f = 0.0033)  <br>State 3: 9.54 eV (130 nm, f = 0.1457)  <br>State 4: not listed |
| **Memory for JK operator** | 0.177 MB (well below the 512 MB limit) |...

## Geometry Analysis

(Bohr)** | C (0,0,‑1.024232) – O (0,0, 1.279345) – H (0, ±1.766894, ‑2.044684) |
| **TD‑DFT (R‑TD‑DFT) – 4 roots** | State 1: 3.92 eV (316 nm, f = 0.000)  <br>State 2: 8.99 eV (138 nm, f = 0.0033)  <br>State 3: 9.54 eV (130 nm, f = 0.1457)  <br>State 4: not listed |
| **Memory for JK operator** | 0.177 MB (well below the 512 MB limit) |

Overall the calculation finished **successfully** with tight SCF convergence, a physically reasonable virial ratio, and a sensible electronic structure for formaldehyde (CH₂O).

---

## Convergence Analysis

** | Converged in 9 iterations (ΔE = –2.46 × 10⁻¹⁰ Hartree, ΔD = 6.69 × 10⁻⁸) |
| **Virial ratio** | **2.004** (ideal ≈ 2.0 → high‑quality wavefunction) |
| **HOMO / LUMO** | –0.264558 au (‑7.20 eV) / –0.044522 au (‑1.21 eV) |
| **HOMO‑LUMO gap** | **0.220 au = 5.99 eV** |
| **Geometry (Bohr)** | C (0,0,‑1.024232) – O (0,0, 1.279345) – H (0, ±1.766894, ‑2.044684) |
| **TD‑DFT (R‑TD‑DFT) – 4 roots** | State 1: 3.92 eV (316 nm, f = 0.000)  <br>State 2: 8.99 eV (138 nm, f = 0.0033)  <br>State 3: 9.54 eV (130 nm, f = 0.1457)  <br>State 4: not listed |
| **Memory for JK operator** | 0.177 MB (well below the 512 MB limit) |

Overall the calculation finished **successfully** with tight SCF convergence, a physically reasonable virial ratio, and a sensible electronic structure for formaldehyde (CH₂O).
...

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

  - E_ne = -331.2594554800 Hartree
  - E_kin = 113.9268682400 Hartree
  - E_1e = -217.3325872300 Hartree
  - Verification: E_ne + E_kin = -217.3325872400 Hartree (Difference: 1.00e-08)

#### Two-Electron and Exchange-Correlation Energy

- **E_ee**: Two-electron interaction energy = 83.5330874200 Hartree
  - Includes Coulomb repulsion and electron exchange
- **E_xc**: Exchange-correlation energy = -11.8514749800 Hartree
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
- **Final Energy Change** = -2.46e-10 Hartree
  - ✓ Meets convergence criteria (|DeltaE| = 2.46e-10 < 1.00e-08)
- **Final Density Matrix Change** = 6.69e-08
  - ✓ Meets convergence criteria (|DeltaD| = 6.69e-08 < 5.00e-06)

#### Dipole Moment

- **X Component**: -0.000000 Debye
- **Y Component**: -0.000000 Debye
- **Z Component**: -2.917200 Debye
- **Total Dipole Moment**: 2.917200 Debye


#### Solvent Effect Information

- Note: Implicit solvent model was used in the calculation

- **Solvent Model Method**: IEFPCM
- **Solvent Name**: WATER
- **Dielectric Constant**: 78.355300
- **Optical Dielectric Constant**: 1.776356
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
  - **Estimated Memory for JK Operator**: 0.177 MB
    - Note: TDDFT first estimates memory needed to calculate JK operator
  - **Maximum Memory to Calculate JK Operator**: 512.000 MB
    - Note: Maximum memory setting for calculating JK operator
  - **Roots per Pass for RPA**: 4
    - Note: For TDDFT calculation, maximum roots per integral calculation pass
  - **Roots per Pass for TDA**: 8
    - Note: For TDA calculation, maximum roots per integral calculation pass. TDA can calculate 2x more roots than RPA
  - **Roots per Pass** (current calculation): 4
  - **Requested Roots per Irrep**: 4

  - ✓ Requested roots are within roots per pass limit, calculation efficiency is good
- **Number of Excited States**: 4

  First 5 Excited States:
    - State 1: Energy = 3.9191 eV, Wavelength = 316.36 nm, Oscillator Strength = 0.000000
    - State 2: Energy = 8.9933 eV, Wavelength = 137.86 nm, Oscillator Strength = 0.003300
    - State 3: Energy = 9.5406 eV, Wavelength = 129.95 nm, Oscillator Strength = 0.145700
    - State 4: Energy = 10.5387 eV, Wavelength = 117.65 nm, Oscillator Strength = 0.000000


## Professional Recommendations

1. ------|----------------|
2. *Basis set adequacy** | For accurate excitation energies, especially Rydberg/valence states, **add diffuse functions** (e.g., aug‑cc‑pVTZ or 6‑31+G\*) to capture the more delocalised excited‑state electron density. |
3. *Functional choice** | Hybrid functionals (B3LYP, PBE0) give reasonable valence excitations, but **range‑separated hybrids** (CAM‑B3LYP, ωB97X‑D) improve charge‑transfer/Rydberg states. |
4. *TDA vs full TDDFT** | TDA often stabilises convergence for triplet states and reduces triplet instability; for singlet valence excitations of formaldehyde, full TDDFT is fine, but testing TDA can be a useful sanity check. |
5. *Solvent effects** | If experimental spectra are measured in solution, consider a **PCM** or **COSMO** solvation model to account for solvato‑chromic shifts. |
6. *State tracking** | Verify that the state ordering matches the expected symmetry (A₁, B₁, …). For C₂ᵥ, the *n → π\** transition is A₂, while *π → π\** is B₁. Checking the irrep labels helps avoid mis‑assignment. |
7. --

## Expert Insights

Insights  

- **Virial Ratio as a Diagnostic:** The virial ratio of 2.004 is a very sensitive indicator of SCF quality. Values deviating by more than 0.02 often signal incomplete convergence, basis‑set incompleteness, or numerical integration errors. Here the ratio is spot‑on, confirming that the electron density is self‑consistent.

- **HOMO‑LUMO Gap vs. Excited‑State Energies:** The vertical HOMO‑LUMO gap (≈ 6 eV) is **larger** than the first excited‑state energy (3.9 eV). This is expected because the *n → π\** transition involves a **non‑bonding orbital** (largely oxygen lone‑pair) that lies **below** the HOMO (π) in many DFT orbital orderings. Hence, the excitation energy can be lower than the HOMO‑LUMO gap.

- **Role of Diffuse Functions:** For formaldehyde, the *n → π\** transition is fairly localized, but the higher‑energy states (≈ 9 eV) have significant Rydberg character. Diffuse functions expand the orbital space, allowing the electron to occupy a more spatially extended orbital, which **lowers** the calculated excitation energy and **increases** oscillator strengths, bringing theory closer to experiment.

- **TDDFT vs. CIS/CC2:** While TDDFT provides a good balance of cost and accuracy for valence excitations, it can **underestimate** charge‑transfer and Rydberg states. If you need sub‑0.1 eV accuracy for the UV region, consider **higher‑level wavefunction methods** (e.g., CC2, ADC(2), or EOM‑CCSD) on a smaller basis for benchmarking.

- **Symmetry Utilisation:** The C₂ᵥ symmetry reduces the computational cost by block‑diagonalising the Fock matrix and TDDFT response matrix. Ensure that the input file explicitly declares the symmetry (e.g., `SYMMETRY=C2V`) to take full advantage of this reduction, especially for larger systems.

---

### Bottom Line  ...
