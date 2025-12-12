# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-12 18:49:48

## Calculation Summary

AI analysis failed: Ollama API request failed: HTTPConnectionPool(host='192.168.124.148', port=11434): Read timed out. (read timeout=180)

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

  - E_ne = -331.4060426700 Hartree
  - E_kin = 113.8468908400 Hartree
  - E_1e = -217.5591518300 Hartree
  - Verification: E_ne + E_kin = -217.5591518300 Hartree (Difference: 2.84e-14)

#### Two-Electron and Exchange-Correlation Energy

- **E_ee**: Two-electron interaction energy = 83.7194936600 Hartree
  - Includes Coulomb repulsion and electron exchange
- **E_xc**: Exchange-correlation energy = -11.8570239700 Hartree
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
- **Final Energy Change** = -8.59e-10 Hartree
  - ✓ Meets convergence criteria (|DeltaE| = 8.59e-10 < 1.00e-08)
- **Final Density Matrix Change** = 1.26e-08
  - ✓ Meets convergence criteria (|DeltaD| = 1.26e-08 < 5.00e-06)

#### Dipole Moment

- **X Component**: 0.000000 Debye
- **Y Component**: -0.000000 Debye
- **Z Component**: -2.593400 Debye
- **Total Dipole Moment**: 2.593400 Debye


#### Solvent Effect Information

- Note: Implicit solvent model was used in the calculation

- **Non-equilibrium Solvation Method**: ptSS: state-specific non-equilibrium solvation (resp-based perturbative correction)
- **Solvent Model Method**: IEFPCM
- **Solvent Name**: WATER
- **Dielectric Constant**: 78.355300
- **Optical Dielectric Constant**: 1.776356
- **Method of Tessellation**: SWIG
- **Type of Radius**: Default
- **Accuracy of Mesh**: MEDIUM
- **Number of Tesseraes**: 690

**Note**: Note: Implicit solvent effect was used in SCF calculation


#### Solvent Effect Information - cLR

| State | Corrected Vertical Absorption Energy (eV) | Nonequilibrium Solvation Free Energy (eV) | Equilibrium Solvation Free Energy (eV) | Excitation Energy Correction (cLR: corrected linear response) (eV) |
|------|----------------------|---------------------------|--------------------------|--------------------|
| 1 |   3.9587 |  -0.0590 |  -0.1405 |  -0.0192 |

- **Number of Vibrational Frequencies**: 2

### TDDFT Calculation Results

#### TDDFT Calculation Block 1

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 0.529 MB
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
- **Number of Excited States**: 16

  First 5 Excited States:
    - State 1: Energy = 3.9715 eV, Wavelength = 312.19 nm, Oscillator Strength = 0.000000
    - State 2: Energy = 8.3356 eV, Wavelength = 148.74 nm, Oscillator Strength = 0.107100
    - State 3: Energy = 9.0350 eV, Wavelength = 137.23 nm, Oscillator Strength = 0.000700
    - State 4: Energy = 9.5763 eV, Wavelength = 129.47 nm, Oscillator Strength = 0.021700
    - State 5: Energy = 10.3582 eV, Wavelength = 119.70 nm, Oscillator Strength = 0.000000

#### TDDFT Calculation Block 2

- **Calculation Method**: TDDFT (Time-Dependent Density Functional Theory)
- **Spin-Flip Parameter (ISF)**: 0
- **IALDA Parameter**: 0
- **Method**: R-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 0.529 MB
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
- **Number of Excited States**: 16

  First 5 Excited States:
    - State 1: Energy = 3.9715 eV, Wavelength = 312.19 nm, Oscillator Strength = 0.000000
    - State 2: Energy = 8.3356 eV, Wavelength = 148.74 nm, Oscillator Strength = 0.107100
    - State 3: Energy = 9.0350 eV, Wavelength = 137.23 nm, Oscillator Strength = 0.000700
    - State 4: Energy = 9.5763 eV, Wavelength = 129.47 nm, Oscillator Strength = 0.021700
    - State 5: Energy = 10.3582 eV, Wavelength = 119.70 nm, Oscillator Strength = 0.000000

