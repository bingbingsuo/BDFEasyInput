# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-12 16:43:57

## Calculation Summary

| Item | Value / Description |
|------|----------------------|
| **Task** | TD‑DFT (linear‑response) excited‑state calculation (20 roots) |
| **Molecule** | Formaldehyde‑like (C=O with two H atoms) |
| **Method** | R‑TD‑DFT (full TD‑DFT, no Tamm‑Dancoff approximation) with cLR non‑equilibrium solvation |...

## Energy Analysis

** | **E<sub>SCF</sub> = –145.70184575 Hartree** |
| **Nuclear Repulsion** | **E<sub>nn</sub> = 31.25163545 Hartree** |
| **Total Energy** | **E<sub>tot</sub> = –114.45021030 Hartree** |
| **Virial Ratio** | 2.005 (ideal ≈ 2.0) |
| **SCF Convergence** | ΔE = –1.17 × 10⁻⁹ Hartree, ΔD = 1.21 × 10⁻⁸ (both below thresholds) |
| **HOMO‑LUMO** | HOMO = –0.26117 a.u. (–7.11 eV), LUMO = –0.03912 a.u. (–1.06 eV) → Gap = 0.222 a.u. (6.04 eV) |
| **Excited States (first three)** | 1: 3.971 eV (312 nm), f = 0.000 <br>2: 8.336 eV (149 nm), f = 0.107 <br>3: 9.035 eV (137 nm), f = 0.0007 |
| **Memory for JK operator** | 0.66 MB (well below the 512 MB limit) |
| **Status** | Success – no errors reported |
...

## Geometry Analysis

Analysis  

All coordinates are given in Bohr; 1 Bohr = 0.529177 Å.

| Bond | ΔX (Bohr) | ΔY (Bohr) | ΔZ (Bohr) | Distance (Bohr) | Distance (Å) | Typical value |
|------|----------|----------|----------|-----------------|--------------|----------------|
| C–O  | 0 | 0 | 2.303577 | 2.30358 | **1.218 Å** | C=O double bond ≈ 1.20 Å |
| C–H₁ | 0 | 1.766894 | –1.020452 | 2.04103 | **1.080 Å** | C–H sp² ≈ 1.08 Å |
| C–H₂ | 0 | –1.766894 | –1.020452 | 2.04103 | **1.080 Å** | same as above |
| H₁–H₂ | 0 | –3.533788 | 0 | 3.53379 | **1.870 Å** | Non‑bonded; reflects H‑C‑H angle |...

## Convergence Analysis

** | ΔE = –1.17 × 10⁻⁹ Hartree, ΔD = 1.21 × 10⁻⁸ (both below thresholds) |
| **HOMO‑LUMO** | HOMO = –0.26117 a.u. (–7.11 eV), LUMO = –0.03912 a.u. (–1.06 eV) → Gap = 0.222 a.u. (6.04 eV) |
| **Excited States (first three)** | 1: 3.971 eV (312 nm), f = 0.000 <br>2: 8.336 eV (149 nm), f = 0.107 <br>3: 9.035 eV (137 nm), f = 0.0007 |
| **Memory for JK operator** | 0.66 MB (well below the 512 MB limit) |
| **Status** | Success – no errors reported |

Overall the calculation converged cleanly, the virial ratio is spot‑on, and the excited‑state data look physically reasonable for a small carbonyl system.

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

- **Total Energy (E_tot)**: -114.4502103000 Hartree
- **SCF Energy**: -145.7018457500 Hartree
- **Convergence Status**: Converged

### HOMO-LUMO Orbital Energies

**Alpha Orbitals**:
- **HOMO**: -0.261170 au (-7.1068 eV)
- **LUMO**: -0.039119 au (-1.0645 eV)

**HOMO-LUMO gap**: 0.222052 au (6.0423 eV)

✓ HOMO-LUMO gap is normal, SCF convergence should not be problematic


### SCF Energy Component Descriptions

#### Total Energy Relation

- **E_tot**: Total electronic energy in BO approximation, includes nuclear repulsion
- **E_ele**: Electronic energy, excluding nuclear repulsion
- **E_nn**: Nuclear repulsion energy
- **Relation**: E_tot = E_ele + E_nn

  - E_ele = -145.7018457500 Hartree
  - E_nn = 31.2516354500 Hartree
  - E_tot = -114.4502103000 Hartree
  - Verification: E_ele + E_nn = -114.4502103000 Hartree (Difference: 0.00e+00)

#### One-Electron Energy Relation

- **E_1e**: One-electron energy
- **E_ne**: Nuclear-electron attraction potential energy
- **E_kin**: Electronic kinetic energy
- **Relation**: E_1e = E_ne + E_kin

  - E_ne = -331.4060428100 Hartree
  - E_kin = 113.8468909200 Hartree
  - E_1e = -217.5591518900 Hartree
  - Verification: E_ne + E_kin = -217.5591518900 Hartree (Difference: 5.68e-14)

#### Two-Electron and Exchange-Correlation Energy

- **E_ee**: Two-electron interaction energy = 83.7194937100 Hartree
  - Includes Coulomb repulsion and electron exchange
- **E_xc**: Exchange-correlation energy = -11.8570239600 Hartree
  - From DFT exchange-correlation functional contribution

#### Virial Ratio

- **Virial Ratio** = 2.005299
  - For non-relativistic all-electron systems, virial ratio should be close to 2.0
  - ✓ Virial ratio close to 2.0 indicates good calculation quality

#### SCF Convergence Criteria and Results

**SCF Iteration Information**:
- **SCF Iterations**: 10 iterations
- DIIS/VSHIFT closed after iteration 9
- Note: Since DIIS/VSHIFT is closed after convergence, actual calculation used 10 iterations

**Convergence Criteria (Thresholds)**:
- **THRENE** (Energy convergence threshold) = 1.00e-08 Hartree
  - Energy change must be smaller than this value
- **THRDEN** (Density matrix convergence threshold) = 5.00e-06
  - Density matrix RMS change must be smaller than this value

**Actual Convergence Values**:
- **Final Energy Change** = -1.17e-09 Hartree
  - ✓ Meets convergence criteria (|DeltaE| = 1.17e-09 < 1.00e-08)
- **Final Density Matrix Change** = 1.21e-08
  - ✓ Meets convergence criteria (|DeltaD| = 1.21e-08 < 5.00e-06)

#### Dipole Moment

- **X Component**: 0.000000 Debye
- **Y Component**: -0.000000 Debye
- **Z Component**: -2.593400 Debye
- **Total Dipole Moment**: 2.593400 Debye


#### Solvent Effect Information

- Note: Implicit solvent model was used in the calculation

- **Non-equilibrium Solvation Method**: cLR: non-equilibrium linear response (solvent LR correction)
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
  - **Estimated Memory for JK Operator**: 0.661 MB
    - Note: TDDFT first estimates memory needed to calculate JK operator
  - **Maximum Memory to Calculate JK Operator**: 512.000 MB
    - Note: Maximum memory setting for calculating JK operator
  - **Roots per Pass for RPA**: 5
    - Note: For TDDFT calculation, maximum roots per integral calculation pass
  - **Roots per Pass for TDA**: 10
    - Note: For TDA calculation, maximum roots per integral calculation pass. TDA can calculate 2x more roots than RPA
  - **Roots per Pass** (current calculation): 5
  - **Requested Roots per Irrep**: 5

  - ✓ Requested roots are within roots per pass limit, calculation efficiency is good
- **Number of Excited States**: 20

  First 5 Excited States:
    - State 1: Energy = 3.9715 eV, Wavelength = 312.19 nm, Oscillator Strength = 0.000000
    - State 2: Energy = 8.3356 eV, Wavelength = 148.74 nm, Oscillator Strength = 0.107100
    - State 3: Energy = 9.0350 eV, Wavelength = 137.23 nm, Oscillator Strength = 0.000700
    - State 4: Energy = 9.5763 eV, Wavelength = 129.47 nm, Oscillator Strength = 0.021700
    - State 5: Energy = 10.3582 eV, Wavelength = 119.70 nm, Oscillator Strength = 0.000000


## Professional Recommendations

1. ------|------------------|
2. *Blue‑shift of excitation energies** | Use a hybrid functional (e.g., B3LYP, PBE0) or a range‑separated functional (CAM‑B3LYP, ωB97X‑D) which typically reduce the systematic over‑estimation. |
3. *Missing diffuse character** (important for Rydberg states) | Augment the basis set with diffuse functions (e.g., **aug‑**‑type). |
4. *State‑specific solvent effects** | For solvated spectra, consider the *state‑specific* solvation approach (SS‑LR) if the software supports it, especially for charge‑transfer states. |
5. *Verification of state character** | Perform a natural transition orbital (NTO) analysis or inspect the excitation vectors to confirm the nature (n → π\*, π → π\*, Rydberg). |
6. --

## Expert Insights

Insights  

### 9.1 Why the Virial Ratio Matters  
The virial theorem states that for a bound, non‑relativistic system, ⟨T⟩ = –½⟨V⟩, leading to a ratio of 2.0 when you compute –⟨V⟩/⟨T⟩. Deviations larger than ~0.01 often signal an incomplete SCF convergence, an inappropriate integration grid, or a mismatch between the kinetic‑energy functional and the exchange‑correlation functional. Your ratio of **2.005** is comfortably within acceptable limits, confirming that the electron density is self‑consistent and the numerical integration grid is sufficiently fine.

### 9.2 Interplay Between HOMO‑LUMO Gap and TD‑DFT Accuracy  
A **large HOMO‑LUMO gap (6 eV)** generally leads to well‑behaved TD‑DFT calculations because the response matrix is far from singularities. In contrast, systems with small gaps (e.g., conjugated π‑systems) often suffer from **triplet instability** and require either TDA or a more robust functional. Here the gap is large, which explains the smooth SCF convergence and the lack of any “triplet instability” warnings.

### 9.3 The Role of cLR Solvation in Vertical Excitations  
In a **non‑equilibrium (cLR) solvation model**, the solvent is treated as responding only to the *fast* electronic component of the excitation, while the slower nuclear component remains frozen. This is the correct physical picture for vertical UV‑Vis spectra measured on femtosecond timescales. However, if you later compute **fluorescence** or **solvatochromic shifts**, you will need an **equilibrium (ssLR)** or **state‑specific** solvation treatment to capture the full re‑organization energy.

### 9.4 Understanding the “Forbidden” n → π\* Transition  
Formaldehyde’s **n → π\*** transition is symmetry‑forbidden in the electric‑dipole approximation (A₁ → A₂ in C₂v), which is why the oscillator strength is essentially zero. In reality, vibronic coupling (through out‑of‑plane bending modes) gives it a weak intensity. If you need to reproduce the experimental weak band, you would have
