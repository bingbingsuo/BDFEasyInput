# BDF Calculation Results Analysis Report

**Generated Time**: 2025-12-17 14:08:15

## Raw Data

### Geometry

**Coordinate Units**: Angstrom (Å)

**Atomic Coordinates**:

| Atom | X | Y | Z |
|------|---|-----|-----|
| C | 0.000000 | -0.000000 | -0.491339 |
| O | -0.000000 | 0.000000 | 0.750533 |
| H | -0.934471 | 0.000000 | -1.069097 |
| H | 0.934471 | -0.000000 | -1.069097 |

**Note**:
- Coordinates extracted from 'Atom Cartcoord(Bohr)' section in BDF output
- Units: Bohr (atomic units)
- 1 Bohr = 0.529177 Å

- **Total Energy (E_tot)**: -114.3703663100 Hartree
- **SCF Energy**: 0.0000000000 Hartree
- **Convergence Status**: Converged

### SCF Energy Component Descriptions

#### Total Energy Relation

- **E_tot**: Total electronic energy in BO approximation, includes nuclear repulsion
- **E_ele**: Electronic energy, excluding nuclear repulsion
- **E_nn**: Nuclear repulsion energy
- **Relation**: E_tot = E_ele + E_nn

  - E_tot = -114.3703663100 Hartree


### Symmetry Group Information

**Detected Point Group**: C(2V)
  - Note: Point group automatically detected by BDF based on molecular geometry

**User-Set Point Group**: C(2V)
  - Note: Point group specified by user via Group keyword in compass module
  - **Is Subgroup**: Yes
    - Note: User-specified group must be a subgroup of the detected group, otherwise calculation will fail

**Largest Abelian Subgroup**: C(2V)
  - **Abelian Subgroup Operations**: 4
  - Note: Largest Abelian subgroup is used for simplified symmetry in certain calculations

**Number of Symmetry Operations**: 4

**Symmetry Check**: OK

**Note**: BDF automatically detects the molecular symmetry group. Users can specify a subgroup of the detected group for calculation using the Group keyword in the compass module.


### Irreducible Representation Information

**Total Number of Basis Functions**: 22
  - Note: Total number of basis functions is the total number of basis set expansion functions

**Number of Irreducible Representations**: 4

**Total Number of Molecular Orbitals**: 22
  - Note: Total number of molecular orbitals equals the sum of orbitals in all irreps

**Irrep Distribution Table**:

| Irreducible Representation | Orbitals per Irrep |
|------|------|
| A1 | 12 |
| A2 | 0 |
| B1 | 6 |
| B2 | 4 |

**Note**: Irreducible representations (Irrep) are symmetry labels for molecular orbitals. Each irrep corresponds to a set of symmetry-adapted molecular orbitals.


#### Solvent Effect Information

- Note: Implicit solvent model was used in the calculation

- **Solvent Model Method**: smd
- **Solvent Name**: water

**Note**: Note: Implicit solvent effect was used in SCF calculation

- **Number of Vibrational Frequencies**: 12
