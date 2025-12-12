# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-12 14:29:30

## Calculation Summary

| Item | Value / Comment |
|------|-----------------|
| **Task** | TD‑DFT (spin‑flip, Tamm‑Dancoff Approximation) |
| **Molecule** | CH₂ (C atom + 2 H atoms) – planar/near‑planar geometry |
| **SCF** | Converged in 10 iterations, ΔE = –1.9 × 10⁻¹² Ha, ΔD = 2.97 × 10⁻⁹ |...

## Energy Analysis

** | **E_tot = –39.111 993 Ha** (includes nuclear repulsion) |
| **Electronic SCF energy** | **E_ele = –45.184 636 Ha** |
| **Nuclear‑repulsion energy** | **E_nn = 6.072 642 Ha** |
| **Virial ratio** | 2.0068  →  excellent (non‑relativistic, all‑electron) |
| **HOMO‑LUMO gap** | 0.1309 Ha = **3.56 eV** (reasonable for a neutral CH₂ radical) |
| **Excited‑state calculation** | 3 spin‑flip TDA blocks, 16 roots each, all oscillator strengths = 0 (expected for spin‑flip) |
| **Memory usage** | JK‑operator ≈ 0.14 MB (far below the 512 MB limit) |

Overall the job finished without errors, and all convergence criteria were comfortably satisfied.  
...

## Geometry Analysis

|
| **SCF** | Converged in 10 iterations, ΔE = –1.9 × 10⁻¹² Ha, ΔD = 2.97 × 10⁻⁹ |
| **Total electronic energy** | **E_tot = –39.111 993 Ha** (includes nuclear repulsion) |
| **Electronic SCF energy** | **E_ele = –45.184 636 Ha** |
| **Nuclear‑repulsion energy** | **E_nn = 6.072 642 Ha** |
| **Virial ratio** | 2.0068  →  excellent (non‑relativistic, all‑electron) |
| **HOMO‑LUMO gap** | 0.1309 Ha = **3.56 eV** (reasonable for a neutral CH₂ radical) |
| **Excited‑state calculation** | 3 spin‑flip TDA blocks, 16 roots each, all oscillator strengths = 0 (expected for spin‑flip) |
| **Memory usage** | JK‑operator ≈ 0.14 MB (far below the 512 MB limit) |
...

## Convergence Analysis

criteria were comfortably satisfied.  

---

## Raw Data

### Geometry

**Coordinate Units**: Bohr (atomic units, 1 Bohr ≈ 0.529177 Å)

**Atomic Coordinates**:

| Atom | X | Y | Z |
|------|---|-----|-----|
| C | 0.000000 | 0.000000 | 0.313990 |
| H | 0.000000 | -1.657230 | -0.941970 |
| H | 0.000000 | 1.657230 | -0.941970 |

**Note**:
- Coordinates extracted from 'Atom Cartcoord(Bohr)' section in BDF output
- Units: Bohr (atomic units)
- 1 Bohr = 0.529177 Å

- **Total Energy (E_tot)**: -39.1119938700 Hartree
- **SCF Energy**: -45.1846360100 Hartree
- **Convergence Status**: Converged

### HOMO-LUMO Orbital Energies

**Alpha Orbitals**:
- **HOMO**: -0.242915 au (-6.6101 eV)
- **LUMO**: 0.083411 au (2.2697 eV)

**Beta Orbitals**:
- **HOMO**: -0.384483 au (-10.4623 eV)
- **LUMO**: -0.111996 au (-3.0476 eV)

**HOMO-LUMO gap**: 0.130919 au (3.5625 eV)

✓ HOMO-LUMO gap is normal, SCF convergence should not be problematic


### SCF Energy Component Descriptions

#### Total Energy Relation

- **E_tot**: Total electronic energy in BO approximation, includes nuclear repulsion
- **E_ele**: Electronic energy, excluding nuclear repulsion
- **E_nn**: Nuclear repulsion energy
- **Relation**: E_tot = E_ele + E_nn

  - E_ele = -45.1846360100 Hartree
  - E_nn = 6.0726421400 Hartree
  - E_tot = -39.1119938700 Hartree
  - Verification: E_ele + E_nn = -39.1119938700 Hartree (Difference: 0.00e+00)

#### One-Electron Energy Relation

- **E_1e**: One-electron energy
- **E_ne**: Nuclear-electron attraction potential energy
- **E_kin**: Electronic kinetic energy
- **Relation**: E_1e = E_ne + E_kin

  - E_ne = -102.6331369800 Hartree
  - E_kin = 38.8481160600 Hartree
  - E_1e = -63.7850209300 Hartree
  - Verification: E_ne + E_kin = -63.7850209200 Hartree (Difference: 1.00e-08)

#### Two-Electron and Exchange-Correlation Energy

- **E_ee**: Two-electron interaction energy = 23.4844638100 Hartree
  - Includes Coulomb repulsion and electron exchange
- **E_xc**: Exchange-correlation energy = -4.8840788900 Hartree
  - From DFT exchange-correlation functional contribution

#### Virial Ratio

- **Virial Ratio** = 2.006793
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
- **Final Energy Change** = -1.93e-12 Hartree
  - ✓ Meets convergence criteria (|DeltaE| = 1.93e-12 < 1.00e-08)
- **Final Density Matrix Change** = 2.97e-09
  - ✓ Meets convergence criteria (|DeltaD| = 2.97e-09 < 5.00e-06)

#### Dipole Moment

- **X Component**: -0.000000 Debye
- **Y Component**: 0.000000 Debye
- **Z Component**: -0.711600 Debye
- **Total Dipole Moment**: 0.711600 Debye

#### Mulliken Population Analysis

| Atom | Charge | Spin Density |
|------|------|----------|
| 1C |  -0.1309 |   2.0149 |
| 2H |   0.0654 |  -0.0075 |
| 3H |   0.0654 |  -0.0075 |

**Note**: Mulliken population analysis based on atomic orbital overlap matrix assignment method

#### Lowdin Population Analysis

| Atom | Charge | Spin Density |
|------|------|----------|
| 1C |  -0.0189 |   1.9349 |
| 2H |   0.0094 |   0.0326 |
| 3H |   0.0094 |   0.0326 |

**Note**: Lowdin population analysis based on symmetric orthogonalized atomic orbital assignment method


### TDDFT Calculation Results

#### TDDFT Calculation Block 1

- **Calculation Method**: TDA (Tamm–Dancoff Approximation)
- **ITDA Parameter**: 1
  - Note: Using TDA approximation (Tamm–Dancoff Approximation)
- **Spin-Flip Direction (ISF)**: -1 (down)
  - ⚠️ **Spin-Flip Calculation**: This is a spin-flip TDDFT calculation
  - Note: When ISF ≠ 0, this TDDFT block is a spin-flip calculation
  - Feature: The excited state has a flipped spin relative to the reference state
  - **Important**: Oscillator strengths in spin-flip calculations are necessarily zero (normal physical phenomenon)
    - Reason: Electric dipole operator does not involve spin, so spin-flip transition oscillator strengths are theoretically zero
    - If oscillator strength is 0, this is expected, not a calculation error
- **IALDA Parameter**: 0
- **Method**: U-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 0.141 MB
    - Note: TDDFT first estimates memory needed to calculate JK operator
  - **Maximum Memory to Calculate JK Operator**: 512.000 MB
    - Note: Maximum memory setting for calculating JK operator
  - **Roots per Pass for RPA**: 2
    - Note: For TDDFT calculation, maximum roots per integral calculation pass
  - **Roots per Pass for TDA**: 4
    - Note: For TDA calculation, maximum roots per integral calculation pass. TDA can calculate 2x more roots than RPA
  - **Roots per Pass** (current calculation): 4
  - **Requested Roots per Irrep**: 4

  - ✓ Requested roots are within roots per pass limit, calculation efficiency is good
- **Number of Excited States**: 16

  First 5 Excited States:
    - State 1: Energy = 0.0462 eV, Wavelength = 26857.33 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 2: Energy = 0.1400 eV, Wavelength = 8854.22 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 3: Energy = 1.6262 eV, Wavelength = 762.43 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 4: Energy = 4.3484 eV, Wavelength = 285.12 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 5: Energy = 5.3334 eV, Wavelength = 232.47 nm, Oscillator Strength = 0.000000 (spin-flip, normal)

  **Note**: All excited states have oscillator strengths of 0, which is a normal result of spin-flip calculations.
  - Spin-flip excitations involve spin reversal, electric dipole transitions are forbidden
  - These excited states are usually observed through magnetic dipole or electric quadrupole transitions

#### TDDFT Calculation Block 2

- **Calculation Method**: TDA (Tamm–Dancoff Approximation)
- **ITDA Parameter**: 1
  - Note: Using TDA approximation (Tamm–Dancoff Approximation)
- **Spin-Flip Direction (ISF)**: 1 (up)
  - ⚠️ **Spin-Flip Calculation**: This is a spin-flip TDDFT calculation
  - Note: When ISF ≠ 0, this TDDFT block is a spin-flip calculation
  - Feature: The excited state has a flipped spin relative to the reference state
  - **Important**: Oscillator strengths in spin-flip calculations are necessarily zero (normal physical phenomenon)
    - Reason: Electric dipole operator does not involve spin, so spin-flip transition oscillator strengths are theoretically zero
    - If oscillator strength is 0, this is expected, not a calculation error
- **IALDA Parameter**: 0
- **Method**: U-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 0.141 MB
    - Note: TDDFT first estimates memory needed to calculate JK operator
  - **Maximum Memory to Calculate JK Operator**: 512.000 MB
    - Note: Maximum memory setting for calculating JK operator
  - **Roots per Pass for RPA**: 2
    - Note: For TDDFT calculation, maximum roots per integral calculation pass
  - **Roots per Pass for TDA**: 4
    - Note: For TDA calculation, maximum roots per integral calculation pass. TDA can calculate 2x more roots than RPA
  - **Roots per Pass** (current calculation): 4
  - **Requested Roots per Irrep**: 4

  - ✓ Requested roots are within roots per pass limit, calculation efficiency is good
- **Number of Excited States**: 16

  First 5 Excited States:
    - State 1: Energy = 10.7005 eV, Wavelength = 115.87 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 2: Energy = 11.8116 eV, Wavelength = 104.97 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 3: Energy = 16.6104 eV, Wavelength = 74.64 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 4: Energy = 17.9479 eV, Wavelength = 69.08 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 5: Energy = 19.1786 eV, Wavelength = 64.65 nm, Oscillator Strength = 0.000000 (spin-flip, normal)

  **Note**: All excited states have oscillator strengths of 0, which is a normal result of spin-flip calculations.
  - Spin-flip excitations involve spin reversal, electric dipole transitions are forbidden
  - These excited states are usually observed through magnetic dipole or electric quadrupole transitions

#### TDDFT Calculation Block 3

- **Calculation Method**: TDA (Tamm–Dancoff Approximation)
- **ITDA Parameter**: 1
  - Note: Using TDA approximation (Tamm–Dancoff Approximation)
- **Spin-Flip Direction (ISF)**: 1 (up)
  - ⚠️ **Spin-Flip Calculation**: This is a spin-flip TDDFT calculation
  - Note: When ISF ≠ 0, this TDDFT block is a spin-flip calculation
  - Feature: The excited state has a flipped spin relative to the reference state
  - **Important**: Oscillator strengths in spin-flip calculations are necessarily zero (normal physical phenomenon)
    - Reason: Electric dipole operator does not involve spin, so spin-flip transition oscillator strengths are theoretically zero
    - If oscillator strength is 0, this is expected, not a calculation error
- **IALDA Parameter**: 2
- **Method**: U-TD-DFT

- **JK Operator Memory Information**:
  - **Estimated Memory for JK Operator**: 0.141 MB
    - Note: TDDFT first estimates memory needed to calculate JK operator
  - **Maximum Memory to Calculate JK Operator**: 512.000 MB
    - Note: Maximum memory setting for calculating JK operator
  - **Roots per Pass for RPA**: 2
    - Note: For TDDFT calculation, maximum roots per integral calculation pass
  - **Roots per Pass for TDA**: 4
    - Note: For TDA calculation, maximum roots per integral calculation pass. TDA can calculate 2x more roots than RPA
  - **Roots per Pass** (current calculation): 4
  - **Requested Roots per Irrep**: 4

  - ✓ Requested roots are within roots per pass limit, calculation efficiency is good
- **Number of Excited States**: 16

  First 5 Excited States:
    - State 1: Energy = 10.6044 eV, Wavelength = 116.92 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 2: Energy = 11.5621 eV, Wavelength = 107.23 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 3: Energy = 16.5732 eV, Wavelength = 74.81 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 4: Energy = 17.8281 eV, Wavelength = 69.54 nm, Oscillator Strength = 0.000000 (spin-flip, normal)
    - State 5: Energy = 19.0424 eV, Wavelength = 65.11 nm, Oscillator Strength = 0.000000 (spin-flip, normal)

  **Note**: All excited states have oscillator strengths of 0, which is a normal result of spin-flip calculations.
  - Spin-flip excitations involve spin reversal, electric dipole transitions are forbidden
  - These excited states are usually observed through magnetic dipole or electric quadrupole transitions


## Professional Recommendations

1. ------|----------------|------------------|
2. *Underestimated singlet–doublet gap** (Block 1) | Affects any property that depends on the correct ordering of low‑lying states (e.g., photochemistry, spin‑orbit coupling). | Use a **range‑separated hybrid functional** (e.g., ωB97X‑D, CAM‑B3LYP) in the SF‑TDDFT framework, or switch to a **spin‑adapted multireference method** (CASSCF/NEVPT2) for benchmarking. |
3. *Zero oscillator strengths** | Expected for pure spin‑flip; however, if you need simulated UV‑Vis spectra you must perform a *regular* TDDFT calculation on the singlet manifold. | Run a **standard TDDFT (RPA) calculation** on the singlet reference (or on the doublet and request “spin‑conserving” excitations). |
4. *Basis set** (not shown) | Small basis sets miss diffuse functions, leading to poor description of Rydberg/charge‑transfer states (the high‑energy block). | Add **aug‑type diffuse functions** (e.g., aug‑cc‑pVTZ) especially when studying UV excitations. |
5. *Number of roots** | 16 roots per block may be insufficient to capture all states of interest for larger systems. | Increase **NROOT** if you need higher‑lying states or a denser spectrum. |
6. --

## Expert Insights

Insights  

- **Why spin‑flip TDDFT?**  
  The CH₂ radical has a **doublet ground state** (X ²B₁) and low‑lying **singlet states** (¹A₁, ¹B₁) that are *multireference* in nature. Conventional TDDFT from a doublet reference can miss these states or give wildly inaccurate energies because the excitation involves a change in spin multiplicity. SF‑TDDFT circumvents this by treating the singlet as a *spin‑flipped* excitation, yielding a qualitatively correct ordering even with modest functionals.  

- **Interpretation of the very low‑energy SF states**  
  The near‑zero excitation energies (0.05–0.14 eV) are an artifact of the *adiabatic* approximation combined with a semi‑local functional: the exchange‑correlation kernel does not provide enough “restoring force” for the spin‑flip transition, so the calculated singlet–doublet gap collapses. This is why experimental singlet–doublet gaps for CH₂ (~2.4 eV) are not reproduced. The remedy is to employ a kernel with **exact exchange** (range‑separated hybrids) or to go beyond the adiabatic approximation (e.g., **TDDFT with a frequency‑dependent kernel**).  

- **Virial ratio as a quality metric**  
  The virial ratio of 2.0068 is a powerful sanity check. Deviations > 0.02 usually signal problems such as incomplete SCF convergence, missing terms (e.g., frozen core), or an inconsistent use of the exchange‑correlation functional. Here the ratio is spot‑on, confirming that the SCF density is internally consistent.  

- **Memory usage**  
  The JK‑operator memory estimate (0.14 MB) shows that the calculation is far from any hardware limit. This means you can safely increase the basis set size or request more roots without worrying about memory bottlenecks.  

- **Future directions**  ...
