# YAML 到 BDF 转换示例

## 示例 1：单点能计算（RHF）

### YAML 输入

```yaml
task:
  type: energy

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: hf
  basis: cc-pvdz
```

### 转换后的 BDF 输入

```bdf
$COMPASS 
Title
 H2O single point energy calculation
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.2217
 H     0.0000    1.4304   -0.8863
 H     0.0000   -1.4304   -0.8863
End geometry
Unit
 Bohr
Check
SAORB
$END

$XUANYUAN
$END

$SCF
RHF
$END
```

**注意**：
- 使用标准格式：模块名大写（`$COMPASS`），关键词首字母大写（`Title`、`Basis`）
- 虽然 BDF 大小写不敏感，但标准格式提高可读性
- `Occupied` 未输出（用户未指定，让 BDF 自动计算）

**转换说明**：
- 坐标从 Angstrom 转换为 Bohr（×1.8897259886）
- `method.type: hf` + `multiplicity: 1` → `RHF`
- `method.basis: cc-pvdz` → `Basis cc-pvdz`
- `Occupied` 值：如果用户在 YAML 中指定了 `settings.scf.occupied`，则使用用户值；否则不输出（让 BDF 自动计算）
- 格式：使用标准格式（模块名大写，关键词首字母大写）

---

## 示例 2：单点能计算（DFT - PBE0）

### YAML 输入

```yaml
task:
  type: energy

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: pbe0
  basis: cc-pvdz
```

### 转换后的 BDF 输入

```bdf
$COMPASS 
Title
 H2O single point energy calculation, PBE0
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.2217
 H     0.0000    1.4304   -0.8863
 H     0.0000   -1.4304   -0.8863
End geometry
Unit
 Bohr
Check
SAORB
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 PBE0
$END
```

**转换说明**：
- `method.type: dft` + `multiplicity: 1` → `RKS`
- `method.functional: pbe0` → `dft functional PBE0`

---

## 示例 2b：单点能计算（DFT - 组合泛函 PBE LYP）

### YAML 输入

```yaml
task:
  type: energy

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: "PBE LYP"  # 组合泛函：PBE 交换 + LYP 相关
  basis: cc-pvdz
```

**或者使用结构化形式**：
```yaml
method:
  type: dft
  functional:
    x: PBE
    c: LYP
  basis: cc-pvdz
```

### 转换后的 BDF 输入

```bdf
$COMPASS 
Title
 H2O single point energy calculation, PBE LYP
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.2217
 H     0.0000    1.4304   -0.8863
 H     0.0000   -1.4304   -0.8863
End geometry
Unit
 Bohr
Check
SAORB
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 PBE LYP
$END
```

**转换说明**：
- `method.type: dft` + `multiplicity: 1` → `RKS`
- `method.functional: "PBE LYP"` → `dft functional PBE LYP`（原样传递）
- BDF 会直接在 libxc 中匹配 "PBE LYP" 组合

---

## 示例 3：几何优化（DFT - B3LYP）

### YAML 输入

```yaml
task:
  type: optimize

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g*

settings:
  geometry_optimization:
    solver: 1
```

### 转换后的 BDF 输入

```bdf
$COMPASS 
Title
 H2O geometry optimization, B3LYP
Basis
 6-31G*
Geometry
 O     0.0000    0.0000    0.2217
 H     0.0000    1.4304   -0.8863
 H     0.0000   -1.4304   -0.8863
End geometry
Unit
 Bohr
Check
SAORB
$END

$BDFOPT
solver
1
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
$END

$resp
geom
norder
1
method
1
$end
```

**转换说明**：
- `task.type: optimize` → 添加 `BDFOPT` 和 `RESP` 模块
- 模块顺序：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`
- `settings.geometry_optimization.solver` → `BDFOPT solver 1`（BDF 自带优化器）
- 使用 RESP 模块计算梯度（GRAD 模块仅支持 HF 和 MCSCF，不支持 DFT）
- RESP 模块参数：`geom`、`norder 1`（梯度）、`method 1`（SCF 梯度）
- 结构优化是迭代过程：BDFOPT 会反复调用 COMPASS、XUANYUAN、SCF、RESP 模块计算能量和梯度
- 输出文件：`.out`（BDFOPT 输出）、`.out.tmp`（SCF 详细信息）、`.optgeom`（优化后的结构，单位 Bohr）

---

## 示例 3b：结构优化 + 频率计算（opt+freq，hess final）

### YAML 输入

```yaml
task:
  type: optimize
  description: "H2O geometry optimization + frequency calculation"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  geometry_optimization:
    solver: 1
    hessian:
      mode: final  # Calculate Hessian after optimization
    thermochemistry:
      temperature: 298.15
      pressure: 1.0
      scale_factor: 1.0
```

### 转换后的 BDF 输入

```bdf
$COMPASS
Title
 H2O geometry optimization + frequency calculation
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
Check
$END

$BDFOPT
solver
 1
hess
 final
temp
 298.15
press
 1.0
scale
 1.0
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
Charge
 0
Spin
 1
$END

$RESP
geom
norder
 2
method
 1
$END
```

**转换说明**：
- `settings.geometry_optimization.hessian.mode: final` → `BDFOPT` 模块中的 `hess final`
- `hess final` 表示在结构优化成功结束后才进行数值 Hessian 计算
- 若结构优化不收敛，程序直接报错退出，不进行 Hessian 及频率计算
- RESP 模块中 `norder 2` 表示计算二阶导数（Hessian 矩阵）
- 可以在同一个 BDF 任务里依次实现结构优化与频率分析，无需单独编写两个输入文件
- 详细说明参见：`research/module_organization/GEOMETRY_OPTIMIZATION.md`

---

## 示例 4：频率计算（Frequency Calculation）

### YAML 输入

```yaml
task:
  type: frequency
  description: "H2O ground state frequency calculation with B3LYP/cc-pVDZ"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    convergence: 1e-6
    max_iterations: 100
  geometry_optimization:
    thermochemistry:
      temperature: 298.15
      pressure: 1.0
      scale_factor: 1.0
      electronic_degeneracy: 1
```

### 转换后的 BDF 输入

```bdf
$COMPASS
Title
 Water
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
$END

$BDFOPT
hess
 only
temp
 298.15
press
 1.0
scale
 1.0
ndeg
 1
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
Charge
 0
Spin
 1
$END

$RESP
geom
norder
 2
method
 1
$END
```

**转换说明**：
- `task.type: frequency` → 频率计算，模块顺序：COMPASS → BDFOPT（`hess only`）→ XUANYUAN → SCF → RESP（`norder 2`）
- `hess only` 表示只进行频率计算而不做几何结构优化
- `norder 2` 表示计算二阶导数（Hessian 矩阵）
- 热化学量设置（`temp`、`press`、`scale`、`ndeg`）用于计算热力学量
- 对于基态 DFT 计算，程序进行解析 Hessian 计算
- 对于 TDDFT 等暂不支持解析 Hessian 的理论级别，程序将自动改为数值 Hessian 计算
- 详细说明参见：`research/module_organization/GEOMETRY_OPTIMIZATION.md`

---

## 示例 5：溶剂化效应计算（SMD 模型）

### YAML 输入

```yaml
task:
  type: energy
  description: "Formaldehyde in water solution, SMD model"

molecule:
  name: "Formaldehyde"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.00000000  -0.54200000
    - O  0.00000000  0.00000000   0.67700000
    - H  0.00000000  0.93500000  -1.08200000
    - H  0.00000000  -0.93500000  -1.08200000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g

settings:
  scf:
    solvent:
      name: water
      model: smd
```

### 转换后的 BDF 输入

```bdf
$COMPASS
Title
 Formaldehyde single point energy calculation, SMD
Basis
 6-31g
Geometry
 C     0.0000    0.0000   -1.0240
 O     0.0000    0.0000    1.2790
 H     0.0000    1.7670   -2.0440
 H     0.0000   -1.7670   -2.0440
End geometry
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
Charge
 0
Spin
 1
solvent
 water
solmodel
 smd
$END
```

**转换说明**：
- `settings.scf.solvent.name` → `solvent [name]`
- `settings.scf.solvent.model` → `solmodel [model]`
- BDF 支持多种溶剂模型：`cosmo`、`cpcm`、`iefpcm`、`ssvpe`、`smd`、`ddcosmo`
- 默认模型为 IEFPCM（如果未指定）
- 详细说明参见：`research/module_organization/SOLVENT_MODELS.md`

---

## 示例 5：TDDFT 非平衡溶剂化效应计算

### YAML 输入

```yaml
task:
  type: tddft
  description: "Formaldehyde TDDFT with non-equilibrium solvation"

molecule:
  name: "Formaldehyde"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.00000000  -0.54200000
    - O  0.00000000  0.00000000   0.67700000
    - H  0.00000000  0.93500000  -1.08200000
    - H  0.00000000  -0.93500000  -1.08200000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g

settings:
  scf:
    solvent:
      name: user
      dielectric: 78.3553
      optical_dielectric: 1.7778
      model: iefpcm
  tddft:
    n_states: 8
    linear_response_non_equilibrium: true
```

### 转换后的 BDF 输入

```bdf
$COMPASS
Title
 Formaldehyde TDDFT with non-equilibrium solvation
Basis
 6-31g
Geometry
 C     0.0000    0.0000   -1.0240
 O     0.0000    0.0000    1.2790
 H     0.0000    1.7670   -2.0440
 H     0.0000   -1.7670   -2.0440
End geometry
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
Charge
 0
Spin
 1
solvent
 user
dielectric
 78.3553
opticalDielectric
 1.7778
solmodel
 iefpcm
$END

$TDDFT
iroot
 8
solneqlr
$END
```

**转换说明**：
- `settings.scf.solvent.name: user` → `solvent user`，需要指定 `dielectric` 和 `opticalDielectric`
- `settings.tddft.linear_response_non_equilibrium: true` → `TDDFT` 模块中的 `solneqlr` 关键词
- 计算非平衡溶剂化效应时，如果溶剂为用户指定的，需要设置光介电常数
- 详细说明参见：`research/module_organization/SOLVENT_MODELS.md`

---

## 示例 7：TDDFT 计算

### YAML 输入

```yaml
task:
  type: tddft

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.0000 1.3970 0.0000
    - C  1.2098 0.6985 0.0000
    - C  1.2098 -0.6985 0.0000
    - C  0.0000 -1.3970 0.0000
    - C -1.2098 -0.6985 0.0000
    - C -1.2098 0.6985 0.0000
    - H  0.0000 2.4810 0.0000
    - H  2.1490 1.2415 0.0000
    - H  2.1490 -1.2415 0.0000
    - H  0.0000 -2.4810 0.0000
    - H -2.1490 -1.2415 0.0000
    - H -2.1490 1.2415 0.0000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz
```

### 转换后的 BDF 输入

```bdf
$COMPASS 
Title
 C6H6 TDDFT calculation
Basis
 cc-pvdz
Geometry
 C     0.0000    2.6394    0.0000
 C     2.2860    1.3197    0.0000
 C     2.2860   -1.3197    0.0000
 C     0.0000   -2.6394    0.0000
 C    -2.2860   -1.3197    0.0000
 C    -2.2860    1.3197    0.0000
 H     0.0000    4.6864    0.0000
 H     4.0614    2.3432    0.0000
 H     4.0614   -2.3432    0.0000
 H     0.0000   -4.6864    0.0000
 H    -4.0614   -2.3432    0.0000
 H    -4.0614    2.3432    0.0000
End geometry
Unit
 Bohr
Check
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
$END

$TDDFT
imethod
 1
isf
 0
itda
 0
idiag
 1
iprint
 3
Nexit
 0 0 0 1
istore
1
lefteig
crit_vec
1.d-4
crit_e
1.d-6
$END
```

**转换说明**：
- `task.type: tddft` → 添加 `TDDFT` 模块
- TDDFT 参数使用默认值

---

## 示例 5：Spin-Adapted TDDFT 计算

### YAML 输入

```yaml
task:
  type: tddft

molecule:
  charge: 0
  multiplicity: 2  # 开壳层体系
  coordinates:
    - O  0.0000 0.0000 0.0000
    - H  0.9572 0.0000 0.0000
    - H -0.2398 0.9266 0.0000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  tddft:
    spin_adapted: true  # 启用 spin-adapted TDDFT
```

### 转换后的 BDF 输入

```bdf
$COMPASS 
Title
 H2O+ spin-adapted TDDFT calculation
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.0000
 H     1.8084    0.0000    0.0000
 H    -0.4528    1.7494    0.0000
End geometry
Unit
 Bohr
Check
SAORB
$END

$XUANYUAN
$END

$SCF
ROKS
dft functional
 B3lyp
$END

$TDDFT
# 对于 TDDFT（包括 spin-adapted TDDFT），通常可以省略 IMETHOD，
# 让 BDF 根据 SCF 自动选择：
#   RHF/RKS           → IMETHOD=1（R-TDDFT）
#   ROHF/ROKS/UHF/UKS → IMETHOD=2（X-TDDFT，包含 spin-adapted TDDFT 的默认方案）
isf
 0
itda
 0
idiag
 1
iprint
 3
Nexit
 0 0 0 1
istore
1
lefteig
crit_vec
1.d-4
crit_e
1.d-6
$END
```

**转换说明**：
- `settings.tddft.spin_adapted: true` → 使用 **spin-adapted TDDFT**（在 SCF 中采用 ROHF/ROKS）
- SCF 方法自动选择为 **ROKS**（限制性开壳层 Kohn-Sham），而不是 UKS；若 `method.type: hf` 则为 **ROHF**
- TDDFT 部分不再显式写 `IMETHOD`，而是交由 BDF 根据 SCF 自动选择：
  - 对于 ROHF/ROKS（spin-adapted 场景），默认得到 **X-TDDFT（IMETHOD=2）**

**重要说明**：
- **Spin-adapted TDDFT** 适用于开壳层体系（`multiplicity > 1`）
- 使用 **ROHF/ROKS** 而非 UHF/UKS，可以更好地处理自旋对称性
- Spin-adapted TDDFT 在 BDF 中有两种实现：X-TDDFT（IMETHOD=2，推荐，默认）和 SA-TDDFT（IMETHOD=3，仅专家/调试时使用）

---

## 转换规则总结

### 0. 格式规范
- **模块名**：使用大写（如 `$COMPASS`、`$SCF`）
- **关键词**：使用首字母大写（如 `Title`、`Basis`、`Geometry`）
- **大小写不敏感**：虽然 BDF 不敏感，但使用标准格式提高可读性

### 1. 坐标转换
- **输入**：YAML 坐标（Angstrom）
- **输出**：BDF 坐标（Bohr）
- **转换**：乘以 1.8897259886

### 2. 方法类型选择

**SCF 方法选择规则**：
- **如果 `settings.tddft.spin_adapted == true`（用于 spin-adapted TDDFT）**：
  - `method.type == 'hf'` → `ROHF`（限制性开壳层 Hartree-Fock）
  - `method.type == 'dft'` → `ROKS`（限制性开壳层 Kohn-Sham）
- **否则（常规情况）**：
  - `hf` + `multiplicity == 1` → `RHF`
  - `hf` + `multiplicity > 1` → `UHF`
  - `dft` + `multiplicity == 1` → `RKS` + `dft functional`
  - `dft` + `multiplicity > 1` → `UKS` + `dft functional`

**TDDFT 方法选择规则**：
- **推荐做法**：在输入中省略 `IMETHOD`，让 BDF TDDFT 模块根据 SCF 自动选择：
  - RHF/RKS → 默认 `IMETHOD=1`（R-TDDFT）
  - ROHF/ROKS/UHF/UKS → 默认 `IMETHOD=2`（U-/X-TDDFT，其中 ROHF/ROKS 情况下即为 spin-adapted X-TDDFT）
- **高级/专家模式**：
  - 如需显式使用 SA-TDDFT，可在 `settings.tddft.method.imethod` 中设置 `3`（SA-TDDFT），目前主要用于程序调试

**泛函处理**：
- **单一泛函**：`functional: B3LYP` → `dft functional B3LYP`（原样传递）
- **组合泛函**：`functional: "PBE LYP"` → `dft functional PBE LYP`（原样传递）
- **结构化输入**：`functional: {x: PBE, c: LYP}` → `dft functional PBE LYP`
- **重要**：BDF 直接匹配 libxc，不做映射或重命名

### 3. 模块组合
- `energy` → `COMPASS` + `XUANYUAN` + `SCF`
- `optimize` → `COMPASS` + `BDFOPT` + `XUANYUAN` + `SCF` + `RESP`
- `tddft` → `COMPASS` + `XUANYUAN` + `SCF` + `TDDFT`（**一个或多个 TDDFT 块**）
- `frequency` → `COMPASS` + `BDFOPT`（`hess only`）+ `XUANYUAN` + `SCF` + `RESP`（`norder 2`）

**注意**：
- 结构优化是迭代过程，BDFOPT 会反复调用 COMPASS、XUANYUAN、SCF、RESP 模块
- 详细说明参见：`research/module_organization/GEOMETRY_OPTIMIZATION.md`

**注意**：
- 几何优化使用 **RESP 模块**而非 GRAD 模块  
  - GRAD 模块仅支持 HF 和 MCSCF，不支持 DFT，推荐只在 MCSCF 结构优化时使用  
  - RESP 模块支持 HF/DFT 以及 TDDFT 梯度/性质（不支持 MCSCF）
- 对于 TDDFT：
  - **只算 singlet**：执行一次 `$TDDFT` 计算即可（不需要设置 `ISF`，等价于 `ISF=0`）  
  - **同时算 singlet + triplet**：需要连续执行两次 `$TDDFT` 计算：
    1. 第一次：默认 `ISF=0`，计算 singlet 激发态  
    2. 第二次：显式设置 `ISF 1`，计算 triplet 激发态  
  - 示例参见 `research/bdf_examples/tddft/h2o_ST.inp`（水分子的 singlet / triplet TDDFT 能量计算）
  - **TDDFT + SOC（自旋轨道耦合）**：典型流程是执行 **三次** `$TDDFT`：
    1. 第一次：`ISF=0`，计算 singlet TDDFT，使用 `ISTORE 1` 保存波函数
    2. 第二次：`ISF=1`，计算 triplet TDDFT，使用 `ISTORE 2` 保存波函数
    3. 第三次：设置 `ISOC 2`、`NFILES 2` 等，基于前两次存储的 TDDFT 波函数做 SOC 后处理，并可用 `IDIAG 2` 对 SOC 修正的哈密顿量做精确对角化。  
       - 示例参见 BDF 自带算例：`/Users/bsuo/bdf/bdf-pkg-full/tests/input/test109.inp`（CH2S LC-BLYP/def2-QZVP TDDFT-SOC 计算）
       - 详细说明参见：`research/module_organization/TDDFT.md`

### 4. 基组名称
- 直接映射（可能需要大小写调整）
- `cc-pvdz` → `cc-pvdz`
- `6-31g*` → `6-31G*`

### 5. 参数格式
- 浮点数使用科学计数法（如 `1.d-6`）
- 整数直接使用
- 多值用空格分隔

---

## 待实现的转换函数

1. **坐标转换函数**
   ```python
   def convert_coordinates(coords_angstrom, units):
       if units == "angstrom":
           return [convert_to_bohr(coord) for coord in coords_angstrom]
       return coords_angstrom
   ```

2. **方法类型选择函数**
   ```python
   def select_scf_method(method_type, functional, multiplicity, spin_adapted=False):
       if spin_adapted:
           # Spin-adapted TDDFT 使用限制性开壳层方法
           return "ROHF" if method_type == "hf" else "ROKS"
       else:
           # 常规方法选择
           if method_type == "hf":
               return "RHF" if multiplicity == 1 else "UHF"
           else:  # dft
               return "RKS" if multiplicity == 1 else "UKS"
   
   def select_tddft_imethod(scf_method, spin_adapted=False):
       if spin_adapted:
           return 3  # S-TDDFT
       else:
           # 自动推断
           if scf_method in ["RHF", "RKS"]:
               return 1  # R-TDDFT
           elif scf_method in ["UHF", "UKS"]:
               return 2  # U-TDDFT
           elif scf_method in ["ROHF", "ROKS"]:
               return 3  # S-TDDFT
           else:
               return 1  # 默认
   ```

3. **模块组合函数**
   ```python
   def get_modules_for_task(task_type):
       module_map = {
           "energy": ["COMPASS", "XUANYUAN", "SCF"],
           "optimize": ["COMPASS", "BDFOPT", "XUANYUAN", "SCF", "RESP"],
           "tddft": ["COMPASS", "XUANYUAN", "SCF", "TDDFT"]
       }
       return module_map.get(task_type, [])
   ```

