# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-13 22:53:31

## Calculation Summary

| Item | Value / Comment |
|------|-----------------|
| **Task** | Geometry optimisation of phenol (C₆H₅OH) followed by TD‑DFT excited‑state calculations |
| **Final SCF energy** | **Eₑₗₑ = –577.490 186 Ha** (electronic) |
| **Total energy (incl. nuclear repulsion)** | **Eₜₒₜ = –307.388 458 Ha** |...

## Energy Analysis

** | **Eₑₗₑ = –577.490 186 Ha** (electronic) |
| **Total energy (incl. nuclear repulsion)** | **Eₜₒₜ = –307.388 458 Ha** |
| **Virial ratio** | **2.005 ≈ 2.0** (excellent for a non‑relativistic DFT calculation) |
| **SCF convergence** | ΔE = 3.4 × 10⁻¹⁰ Ha, ΔD = 1.1 × 10⁻⁷ (both far below the thresholds) |
| **HOMO‑LUMO gap** | **6.58 eV** (0.242 au) |
| **Geometry** | Planar aromatic ring, C–C ≈ 1.40 Å, C–O ≈ 1.39 Å, O–H ≈ 0.97 Å – chemically sensible for phenol |
| **TD‑DFT (R‑TD‑DFT) – 18 blocks** | First excited state converges to **≈ 4.89 eV (λ ≈ 253 nm)** with **f ≈ 0.08**; second state ≈ 5.87 eV (f ≈ 0.10); third state ≈ 6.47 eV (f ≈ 0.80) |
| **Warnings** | “input orbital file not found” and repeated “Deviation is too large. Orthogonality is LOST !!!” messages |

Overall the single‑point SCF part of the calculation is **well converged and reliable**. The geometry is chemically reasonable. The TD‑DFT results show a clear, reproducible set of low‑lying π→π* transitions typical for phenol. The only red flag is the series of orthogonality‑loss warnings, which we discuss below....

## Geometry Analysis

optimisation of phenol (C₆H₅OH) followed by TD‑DFT excited‑state calculations |
| **Final SCF energy** | **Eₑₗₑ = –577.490 186 Ha** (electronic) |
| **Total energy (incl. nuclear repulsion)** | **Eₜₒₜ = –307.388 458 Ha** |
| **Virial ratio** | **2.005 ≈ 2.0** (excellent for a non‑relativistic DFT calculation) |
| **SCF convergence** | ΔE = 3.4 × 10⁻¹⁰ Ha, ΔD = 1.1 × 10⁻⁷ (both far below the thresholds) |
| **HOMO‑LUMO gap** | **6.58 eV** (0.242 au) |
| **Geometry** | Planar aromatic ring, C–C ≈ 1.40 Å, C–O ≈ 1.39 Å, O–H ≈ 0.97 Å – chemically sensible for phenol |
| **TD‑DFT (R‑TD‑DFT) – 18 blocks** | First excited state converges to **≈ 4.89 eV (λ ≈ 253 nm)** with **f ≈ 0.08**; second state ≈ 5.87 eV (f ≈ 0.10); third state ≈ 6.47 eV (f ≈ 0.80) |
| **Warnings** | “input orbital file not found” and repeated “Deviation is too large. Orthogonality is LOST !!!” messages |
...

## Convergence Analysis

** | ΔE = 3.4 × 10⁻¹⁰ Ha, ΔD = 1.1 × 10⁻⁷ (both far below the thresholds) |
| **HOMO‑LUMO gap** | **6.58 eV** (0.242 au) |
| **Geometry** | Planar aromatic ring, C–C ≈ 1.40 Å, C–O ≈ 1.39 Å, O–H ≈ 0.97 Å – chemically sensible for phenol |
| **TD‑DFT (R‑TD‑DFT) – 18 blocks** | First excited state converges to **≈ 4.89 eV (λ ≈ 253 nm)** with **f ≈ 0.08**; second state ≈ 5.87 eV (f ≈ 0.10); third state ≈ 6.47 eV (f ≈ 0.80) |
| **Warnings** | “input orbital file not found” and repeated “Deviation is too large. Orthogonality is LOST !!!” messages |

Overall the single‑point SCF part of the calculation is **well converged and reliable**. The geometry is chemically reasonable. The TD‑DFT results show a clear, reproducible set of low‑lying π→π* transitions typical for phenol. The only red flag is the series of orthogonality‑loss warnings, which we discuss below.

---

## Raw Data

### Geometry

**Coordinate Units**: Bohr (atomic units, 1 Bohr ≈ 0.529177 Å)

**Atomic Coordinates**:

| Atom | X | Y | Z |
|------|---|-----|-----|
| C | 2.184565 | -0.037018 | 2.282526 |
| C | 3.508889 | -0.075759 | 0.000000 |
| C | 2.184565 | -0.037018 | -2.282526 |
| C | -0.452494 | 0.029491 | -2.289692 |
| C | -1.765645 | 0.053131 | 0.000000 |
| C | -0.452494 | 0.029491 | 2.289692 |
| H | 3.205049 | -0.054507 | 4.065317 |
| H | 5.561624 | -0.125066 | 0.000000 |
| H | 3.205049 | -0.054507 | -4.065317 |
| H | -1.513621 | 0.079296 | -4.045992 |
| H | -1.513621 | 0.079296 | 4.045992 |
| O | -4.387312 | 0.221558 | 0.000000 |
| H | -5.090301 | -1.470887 | 0.000000 |

**Note**:
- Coordinates extracted from 'Atom Cartcoord(Bohr)' section in BDF output
- Units: Bohr (atomic units)
- 1 Bohr = 0.529177 Å

- **Total Energy (E_tot)**: -307.3884575700 Hartree
- **SCF Energy**: -577.4901860600 Hartree
- **Convergence Status**: Converged

### HOMO-LUMO Orbital Energies

**Alpha Orbitals**:
- **HOMO**: -0.245586 au (-6.6827 eV)
- **LUMO**: -0.003881 au (-0.1056 eV)

**HOMO-LUMO gap**: 0.241705 au (6.5771 eV)

✓ HOMO-LUMO gap is normal, SCF convergence should not be problematic


### SCF Energy Component Descriptions

#### Total Energy Relation

- **E_tot**: Total electronic energy in BO approximation, includes nuclear repulsion
- **E_ele**: Electronic energy, excluding nuclear repulsion
- **E_nn**: Nuclear repulsion energy
- **Relation**: E_tot = E_ele + E_nn

  - E_ele = -577.4901860600 Hartree
  - E_nn = 270.1017284900 Hartree
  - E_tot = -307.3884575700 Hartree
  - Verification: E_ele + E_nn = -307.3884575700 Hartree (Difference: 0.00e+00)

#### One-Electron Energy Relation

- **E_1e**: One-electron energy
- **E_ne**: Nuclear-electron attraction potential energy
- **E_kin**: Electronic kinetic energy
- **Relation**: E_1e = E_ne + E_kin

  - E_ne = -1256.4510229100 Hartree
  - E_kin = 305.7732452100 Hartree
  - E_1e = -950.6777776900 Hartree
  - Verification: E_ne + E_kin = -950.6777777000 Hartree (Difference: 1.00e-08)

#### Two-Electron and Exchange-Correlation Energy

- **E_ee**: Two-electron interaction energy = 408.3214204400 Hartree
  - Includes Coulomb repulsion and electron exchange
- **E_xc**: Exchange-correlation energy = -35.1256312500 Hartree
  - From DFT exchange-correlation functional contribution

#### Virial Ratio

- **Virial Ratio** = 2.005282
  - For non-relativistic all-electron systems, virial ratio should be close to 2.0
  - ✓ Virial ratio close to 2.0 indicates good calculation quality

#### SCF Convergence Criteria and Results

**SCF Iteration Information**:
- **SCF Iterations**: 11 iterations
- DIIS/VSHIFT closed after iteration 10
- Note: Since DIIS/VSHIFT is closed after convergence, actual calculation used 11 iterations

**Convergence Criteria (Thresholds)**:
- **THRENE** (Energy convergence threshold) = 1.00e-08 Hartree
  - Energy change must be smaller than this value
- **THRDEN** (Density matrix convergence threshold) = 5.00e-06
  - Density matrix RMS change must be smaller than this value

**Actual Convergence Values**:
- **Final Energy Change** = 3.41e-10 Hartree
  - ✓ Meets convergence criteria (|DeltaE| = 3.41e-10 < 1.00e-08)
- **Final Density Matrix Change** = 1.07e-07
  - ✓ Meets convergence criteria (|DeltaD| = 1.07e-07 < 5.00e-06)

#### Dipole Moment

- **X Component**: -0.019700 Debye
- **Y Component**: 0.777200 Debye
- **Z Component**: 2.085700 Debye
- **Total Dipole Moment**: 2.225900 Debye


#### Solvent Effect Information

- Note: Implicit solvent model was used in the calculation

- **Solvent Model Method**: IEFPCM
- **Solvent Name**: WATER
- **Dielectric Constant**: 78.355300
- **Optical Dielectric Constant**: 1.776356
- **Method of Tessellation**: SWIG
- **Type of Radius**: Default
- **Accuracy of Mesh**: MEDIUM
- **Number of Tesseraes**: 1709

**Note**: Note: Implicit solvent effect was used in SCF calculation


### TDDFT Calculation Results

#### TDDFT Calculation Block 1

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 5.5069 eV, Wavelength = 225.14 nm, Oscillator Strength = 0.013600
    - State 2: Energy = 6.2923 eV, Wavelength = 197.04 nm, Oscillator Strength = 0.044200
    - State 3: Energy = 6.7519 eV, Wavelength = 183.63 nm, Oscillator Strength = 0.005900
    - State 4: Energy = 6.8149 eV, Wavelength = 181.93 nm, Oscillator Strength = 0.015200
    - State 5: Energy = 6.8969 eV, Wavelength = 179.77 nm, Oscillator Strength = 0.883700

#### TDDFT Calculation Block 2

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 5.1608 eV, Wavelength = 240.24 nm, Oscillator Strength = 0.016900
    - State 2: Energy = 5.9432 eV, Wavelength = 208.61 nm, Oscillator Strength = 0.063900
    - State 3: Energy = 6.5024 eV, Wavelength = 190.68 nm, Oscillator Strength = 0.024200
    - State 4: Energy = 6.5163 eV, Wavelength = 190.27 nm, Oscillator Strength = 0.745200
    - State 5: Energy = 6.5508 eV, Wavelength = 189.27 nm, Oscillator Strength = 0.720000

#### TDDFT Calculation Block 3

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 5.1575 eV, Wavelength = 240.40 nm, Oscillator Strength = 0.019600
    - State 2: Energy = 5.9467 eV, Wavelength = 208.49 nm, Oscillator Strength = 0.061700
    - State 3: Energy = 6.5058 eV, Wavelength = 190.57 nm, Oscillator Strength = 0.625500
    - State 4: Energy = 6.5122 eV, Wavelength = 190.39 nm, Oscillator Strength = 0.054400
    - State 5: Energy = 6.5528 eV, Wavelength = 189.21 nm, Oscillator Strength = 0.194000

#### TDDFT Calculation Block 4

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 5.1517 eV, Wavelength = 240.67 nm, Oscillator Strength = 0.021100
    - State 2: Energy = 5.9431 eV, Wavelength = 208.62 nm, Oscillator Strength = 0.062700
    - State 3: Energy = 6.4929 eV, Wavelength = 190.95 nm, Oscillator Strength = 0.568900
    - State 4: Energy = 6.5137 eV, Wavelength = 190.34 nm, Oscillator Strength = 0.087300
    - State 5: Energy = 6.5489 eV, Wavelength = 189.32 nm, Oscillator Strength = 0.255300

#### TDDFT Calculation Block 5

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 5.1472 eV, Wavelength = 240.88 nm, Oscillator Strength = 0.021800
    - State 2: Energy = 5.9366 eV, Wavelength = 208.85 nm, Oscillator Strength = 0.065600
    - State 3: Energy = 6.4798 eV, Wavelength = 191.34 nm, Oscillator Strength = 0.538600
    - State 4: Energy = 6.5063 eV, Wavelength = 190.56 nm, Oscillator Strength = 0.212500
    - State 5: Energy = 6.5595 eV, Wavelength = 189.01 nm, Oscillator Strength = 0.317200

#### TDDFT Calculation Block 6

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.9037 eV, Wavelength = 252.84 nm, Oscillator Strength = 0.061400
    - State 2: Energy = 5.7735 eV, Wavelength = 214.75 nm, Oscillator Strength = 0.104000
    - State 3: Energy = 6.3399 eV, Wavelength = 195.56 nm, Oscillator Strength = 0.639500
    - State 4: Energy = 6.4778 eV, Wavelength = 191.40 nm, Oscillator Strength = 0.472600
    - State 5: Energy = 6.9294 eV, Wavelength = 178.93 nm, Oscillator Strength = 0.162700

#### TDDFT Calculation Block 7

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8606 eV, Wavelength = 255.08 nm, Oscillator Strength = 0.073300
    - State 2: Energy = 5.8029 eV, Wavelength = 213.66 nm, Oscillator Strength = 0.091900
    - State 3: Energy = 6.3678 eV, Wavelength = 194.71 nm, Oscillator Strength = 0.698800
    - State 4: Energy = 6.5523 eV, Wavelength = 189.22 nm, Oscillator Strength = 0.502700
    - State 5: Energy = 7.1458 eV, Wavelength = 173.51 nm, Oscillator Strength = 0.058700

#### TDDFT Calculation Block 8

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.9333 eV, Wavelength = 251.32 nm, Oscillator Strength = 0.069100
    - State 2: Energy = 5.8585 eV, Wavelength = 211.63 nm, Oscillator Strength = 0.111100
    - State 3: Energy = 6.4827 eV, Wavelength = 191.25 nm, Oscillator Strength = 0.783300
    - State 4: Energy = 6.5969 eV, Wavelength = 187.94 nm, Oscillator Strength = 0.567000
    - State 5: Energy = 7.0168 eV, Wavelength = 176.70 nm, Oscillator Strength = 0.002700

#### TDDFT Calculation Block 9

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8460 eV, Wavelength = 255.85 nm, Oscillator Strength = 0.085200
    - State 2: Energy = 5.8733 eV, Wavelength = 211.10 nm, Oscillator Strength = 0.078800
    - State 3: Energy = 6.4320 eV, Wavelength = 192.76 nm, Oscillator Strength = 0.793200
    - State 4: Energy = 6.6682 eV, Wavelength = 185.93 nm, Oscillator Strength = 0.539300
    - State 5: Energy = 6.9716 eV, Wavelength = 177.84 nm, Oscillator Strength = 0.008000

#### TDDFT Calculation Block 10

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.9190 eV, Wavelength = 252.05 nm, Oscillator Strength = 0.069900
    - State 2: Energy = 5.8435 eV, Wavelength = 212.17 nm, Oscillator Strength = 0.110000
    - State 3: Energy = 6.4562 eV, Wavelength = 192.04 nm, Oscillator Strength = 0.772000
    - State 4: Energy = 6.5801 eV, Wavelength = 188.42 nm, Oscillator Strength = 0.545700
    - State 5: Energy = 7.0493 eV, Wavelength = 175.88 nm, Oscillator Strength = 0.025200

#### TDDFT Calculation Block 11

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8933 eV, Wavelength = 253.38 nm, Oscillator Strength = 0.078300
    - State 2: Energy = 5.8654 eV, Wavelength = 211.38 nm, Oscillator Strength = 0.100700
    - State 3: Energy = 6.4699 eV, Wavelength = 191.63 nm, Oscillator Strength = 0.801200
    - State 4: Energy = 6.6354 eV, Wavelength = 186.85 nm, Oscillator Strength = 0.561400
    - State 5: Energy = 6.9866 eV, Wavelength = 177.46 nm, Oscillator Strength = 0.001300

#### TDDFT Calculation Block 12

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8925 eV, Wavelength = 253.42 nm, Oscillator Strength = 0.078900
    - State 2: Energy = 5.8672 eV, Wavelength = 211.32 nm, Oscillator Strength = 0.099900
    - State 3: Energy = 6.4713 eV, Wavelength = 191.59 nm, Oscillator Strength = 0.802200
    - State 4: Energy = 6.6400 eV, Wavelength = 186.72 nm, Oscillator Strength = 0.562300
    - State 5: Energy = 6.9868 eV, Wavelength = 177.45 nm, Oscillator Strength = 0.000900

#### TDDFT Calculation Block 13

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8935 eV, Wavelength = 253.36 nm, Oscillator Strength = 0.078900
    - State 2: Energy = 5.8675 eV, Wavelength = 211.31 nm, Oscillator Strength = 0.100600
    - State 3: Energy = 6.4729 eV, Wavelength = 191.54 nm, Oscillator Strength = 0.802300
    - State 4: Energy = 6.6408 eV, Wavelength = 186.70 nm, Oscillator Strength = 0.563000
    - State 5: Energy = 6.9858 eV, Wavelength = 177.48 nm, Oscillator Strength = 0.000800

#### TDDFT Calculation Block 14

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8940 eV, Wavelength = 253.34 nm, Oscillator Strength = 0.079000
    - State 2: Energy = 5.8679 eV, Wavelength = 211.29 nm, Oscillator Strength = 0.100800
    - State 3: Energy = 6.4739 eV, Wavelength = 191.51 nm, Oscillator Strength = 0.802500
    - State 4: Energy = 6.6420 eV, Wavelength = 186.67 nm, Oscillator Strength = 0.563500
    - State 5: Energy = 6.9851 eV, Wavelength = 177.50 nm, Oscillator Strength = 0.000600

#### TDDFT Calculation Block 15

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8946 eV, Wavelength = 253.31 nm, Oscillator Strength = 0.079000
    - State 2: Energy = 5.8681 eV, Wavelength = 211.28 nm, Oscillator Strength = 0.100900
    - State 3: Energy = 6.4744 eV, Wavelength = 191.50 nm, Oscillator Strength = 0.802600
    - State 4: Energy = 6.6423 eV, Wavelength = 186.66 nm, Oscillator Strength = 0.563900
    - State 5: Energy = 6.9846 eV, Wavelength = 177.51 nm, Oscillator Strength = 0.000300

#### TDDFT Calculation Block 16

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8948 eV, Wavelength = 253.30 nm, Oscillator Strength = 0.079000
    - State 2: Energy = 5.8684 eV, Wavelength = 211.28 nm, Oscillator Strength = 0.100900
    - State 3: Energy = 6.4746 eV, Wavelength = 191.49 nm, Oscillator Strength = 0.802600
    - State 4: Energy = 6.6427 eV, Wavelength = 186.65 nm, Oscillator Strength = 0.564100
    - State 5: Energy = 6.9845 eV, Wavelength = 177.51 nm, Oscillator Strength = 0.000100

#### TDDFT Calculation Block 17

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8949 eV, Wavelength = 253.29 nm, Oscillator Strength = 0.078900
    - State 2: Energy = 5.8684 eV, Wavelength = 211.27 nm, Oscillator Strength = 0.100900
    - State 3: Energy = 6.4745 eV, Wavelength = 191.50 nm, Oscillator Strength = 0.802700
    - State 4: Energy = 6.6425 eV, Wavelength = 186.65 nm, Oscillator Strength = 0.564200
    - State 5: Energy = 6.9850 eV, Wavelength = 177.50 nm, Oscillator Strength = 0.000000

#### TDDFT Calculation Block 18

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 2.575 MB
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
- **Number of Excited States**: 5

  First 5 Excited States:
    - State 1: Energy = 4.8950 eV, Wavelength = 253.29 nm, Oscillator Strength = 0.078900
    - State 2: Energy = 5.8684 eV, Wavelength = 211.28 nm, Oscillator Strength = 0.100900
    - State 3: Energy = 6.4747 eV, Wavelength = 191.49 nm, Oscillator Strength = 0.802700
    - State 4: Energy = 6.6425 eV, Wavelength = 186.65 nm, Oscillator Strength = 0.564300
    - State 5: Energy = 6.9850 eV, Wavelength = 177.50 nm, Oscillator Strength = 0.000000


### RESP Module Excited-State Gradient Calculation Information

- **Primary Excited State Root**: Root 1 (the lowest-energy excited state)
- **Calculated Excited State Roots**: Root 1
- **Gradient Iteration Counts**:
  - Root 1: 18 iterations
- **Total Gradient Calculations**: 18 gradient calculations

**Description**: Calculated the gradient of TDDFT excited state 1 (the lowest-energy excited state). Performed 18 gradient calculation iterations.

**Note**: The marker "<Now following: Root    N>" or "Root    N" indicates that the gradient of the Nth excited state (Root 1 is the lowest-energy excited state) is being calculated. Since gradient calculations involve multiple iterations, each target excited state's gradient calculation may contain multiple such markers.

## Professional Recommendations

1. *Address the orthogonality warnings**  
2. Ensure the orbital file from the previous step is written (`WRITEORBITALS` keyword) and supplied to the next TD‑DFT block.  
3. Switch to **TDA** for the excited‑state optimisation (`TDDFT(TDA)`) – it is numerically more stable and eliminates the “orthogonality lost” problem.  
4. If full TD‑DFT is required, increase the **subspace orthogonalisation frequency** (`ORTHOG=EVERY`) or use a more robust linear‑solver (e.g., **ADIIS**).  
5. *Run a frequency calculation** at the final geometry  
6. Confirms that the structure is a true minimum (no imaginary frequencies).  
7. Provides ZPE, thermal corrections, and entropy for reliable thermochemistry.  
8. *Upgrade the electronic‑structure model**  
9. Use a **hybrid functional** (B3LYP, PBE0) for a more realistic HOMO‑LUMO gap and excitation energies.  
10. Add **dispersion correction** (e.g., `-D3BJ`) to improve the C–O bond description.  
11. *Enlarge the basis set**  
12. At least a **triple‑ζ valence plus polarisation** (def2‑TZVP or 6‑311+G(d,p)).  
13. Include **diffuse functions** (aug‑type) if you are interested in Rydberg or charge‑transfer states (the higher TD‑DFT states).  
14. *Check the input file** (`c6h6_tdopt.inp`) for the following:  
15. Correct path to the orbital file (`READORBITALS`).  
16. Reasonable convergence thresholds for the TD‑DFT response (`TDTHRESH`).  ...

## Warnings

1. input orbital file not found
2. Deviation is too large. Orthogonality is LOST !!!
3. Deviation is too large. Orthogonality is LOST !!!
4. Deviation is too large. Orthogonality is LOST !!!
5. Deviation is too large. Orthogonality is LOST !!!
6. Deviation is too large. Orthogonality is LOST !!!
7. Deviation is too large. Orthogonality is LOST !!!
8. Deviation is too large. Orthogonality is LOST !!!
9. Deviation is too large. Orthogonality is LOST !!!
10. Deviation is too large. Orthogonality is LOST !!!
11. Deviation is too large. Orthogonality is LOST !!!
12. Deviation is too large. Orthogonality is LOST !!!
13. Deviation is too large. Orthogonality is LOST !!!

## Expert Insights

Insights  

### 7.1 Why the orthogonality warnings appear  

During the **linear‑response TD‑DFT** procedure BDF builds a **Krylov subspace** of trial vectors that must stay mutually orthogonal. When the subspace grows (as it does across many optimisation steps) and the underlying SCF orbitals are *re‑initialised* (because the orbital file is missing), the overlap matrix can become ill‑conditioned, leading to the “Deviation is too large. Orthogonality is LOST !!!” message. The algorithm typically *re‑orthogonalises* automatically, which explains why the final excitation energies are still sensible. However, the repeated loss of orthogonality can:

* Slow down convergence dramatically (many more TD‑DFT blocks than necessary).  
* Potentially introduce **numerical noise** into the transition dipole vectors, affecting the computed oscillator strengths.  

**Bottom‑line:** The electronic ground‑state is fine; the *response* part needs a more stable starting point.

### 7.2 Physical interpretation of the strong S₃ transition  

The third excited state (~ 6.47 eV, f ≈ 0.80) carries an unusually large oscillator strength. In phenol, the **π→π\*** transition around 200 nm (the so‑called “C‑band”) is known to be intense. The calculated wavelength (≈ 191 nm) and high f value match this experimental observation. The large intensity arises from a **collective excitation** involving several benzene π‑orbitals, which is well captured by R‑TD‑DFT but can be over‑estimated if the functional lacks exact exchange. Using a **range‑separated hybrid** would likely lower the energy slightly and keep the oscillator strength realistic.
...
