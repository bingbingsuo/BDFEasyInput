# TDDFT 激发态计算模块编排说明

## 概述

本文档说明如何根据 BDF 手册组织 TDDFT 激发态计算的模块。参考手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/TD.rst`

## TDDFT 计算类型

BDF 支持多种 TDDFT 计算方法：

1. **R-TDDFT**：闭壳层体系（基于 RHF/RKS）
2. **U-TDDFT**：开壳层体系（基于 UHF/UKS）
3. **X-TDDFT（SA-TDDFT）**：自旋匹配 TDDFT，用于开壳层体系（基于 ROHF/ROKS）
4. **Spin-flip TDDFT**：自旋翻转 TDDFT
5. **TDDFT-SOC**：自旋轨道耦合计算
6. **TDA**：Tamm-Dancoff 近似（TDDFT 的简化版本）

## 基本模块编排

### 1. 基本 TDDFT 单点能量计算

**模块顺序**：`COMPASS` → `XUANYUAN` → `SCF` → `TDDFT`

**示例：闭壳层体系 R-TDDFT**

```bdf
$COMPASS
Title
 H2O TDDFT calculation
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
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
$END

$TDDFT
iroot
 1
$END
```

**说明**：
- SCF 模块使用 `RKS`（闭壳层 DFT）
- TDDFT 模块默认使用 R-TDDFT（`IMETHOD` 通常省略，由 BDF 自动选择）
- `iroot 1` 表示每个不可约表示计算 1 个激发态

### 2. 开壳层体系 U-TDDFT

**示例：H2O+ 离子**

```bdf
$COMPASS
Title
 H2O+ TDDFT calculation
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
Group
 C(1)  # Force to use C1 symmetry for open-shell TDDFT
$END

$XUANYUAN
$END

$SCF
UKS
dft functional
 B3lyp
Charge
 1
Spin
 2
$END

$TDDFT
iroot
 4
$END
```

**说明**：
- SCF 模块使用 `UKS`（开壳层 DFT）
- 开壳层 TDDFT 代码不支持非阿贝尔点群，需要强制使用阿贝尔子群（如 `C(1)`）
- TDDFT 模块默认使用 U-TDDFT

### 3. Spin-Adapted TDDFT (X-TDDFT)

**示例：N2+ 分子**

```bdf
$COMPASS
Title
 N2+ X-TDDFT calculation
Basis
 aug-cc-pvtz
Geometry
 N  0.00  0.00  0.00
 N  0.00  0.00  1.1164
End geometry
Group
 D(2h)  # Force to use D2h symmetry
$END

$XUANYUAN
$END

$SCF
ROKS  # Restricted open-shell Kohn-Sham
dft functional
 B3lyp
Charge
 1
Spin
 2
$END

$TDDFT
iroot
 5
$END
```

**说明**：
- SCF 模块使用 `ROKS`（限制性开壳层 Kohn-Sham）
- TDDFT 模块默认使用 X-TDDFT（自旋匹配 TDDFT）
- X-TDDFT 可以有效解决开壳层体系激发态的自旋污染问题

## 多步 TDDFT 计算

### 1. Singlet + Triplet TDDFT

**模块顺序**：`COMPASS` → `XUANYUAN` → `SCF` → `TDDFT` (singlet) → `TDDFT` (triplet)

**示例：同时计算单重态和三重态**

```bdf
$COMPASS
Title
 H2O TDDFT singlet and triplet
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
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
$END

# First TDDFT: Singlet states (ISF=0, default)
$TDDFT
iroot
 4
$END

# Second TDDFT: Triplet states (ISF=1)
$TDDFT
isf
 1
iroot
 4
$END
```

**说明**：
- 第一次 TDDFT 计算：默认 `ISF=0`，计算单重态
- 第二次 TDDFT 计算：显式设置 `ISF 1`，计算三重态
- 两次计算独立进行，分别输出结果

### 2. TDDFT + SOC（自旋轨道耦合）

**模块顺序**：`COMPASS` → `XUANYUAN` → `SCF` → `TDDFT` (singlet, `istore 1`) → `TDDFT` (triplet, `istore 2`) → `TDDFT` (SOC, `isoc 2`)

**示例：CH2S 分子的 sf-X2C/TDDFT-SOC 计算**

```bdf
$COMPASS
Title
 CH2S TDDFT-SOC
Basis
 cc-pVDZ-DK  # Relativistic basis set
Geometry
 C       0.000000    0.000000   -1.039839
 S       0.000000    0.000000    0.593284
 H       0.000000    0.932612   -1.626759
 H       0.000000   -0.932612   -1.626759
End geometry
$END

$XUANYUAN
heff  # Ask for sf-X2C Hamiltonian
 3
hsoc  # Set SOC integral as 1e+mf-2e
 2
$END

$SCF
RKS
dft functional
 PBE0
Charge
 0
Spin
 1
$END

# 1st TDDFT: R-TDDFT, calculate singlets
$TDDFT
isf
 0
idiag
 1  # Davidson method
iroot
 10
itda
 0  # Full TDDFT (not TDA)
istore  # Save TDDFT wave function in the 1st scratch file
 1
$END

# 2nd TDDFT: Spin-flip TDDFT, calculate triplets
$TDDFT
isf  # Ask for spin-flip up calculation
 1
itda
 0
idiag
 1
iroot
 10
istore  # Save TDDFT wave function in the 2nd scratch file
 2
$END

# 3rd TDDFT: TDDFT-SOC calculation
$TDDFT
isoc
 2
nprt  # Print level
 10
nfiles
 2  # Read from files 1 and 2
ifgs  # Whether to include the ground state in the SOC treatment
 1
imatsoc
 8
 0 0 0 2 1 1
 0 0 0 2 2 1
 0 0 0 2 3 1
 0 0 0 2 4 1
 1 1 1 2 1 1
 1 1 1 2 2 1
 1 1 1 2 3 1
 1 1 1 2 4 1
imatrso
 6
 1 1
 1 2
 1 3
 1 4
 1 5
 1 6
idiag  # Full diagonalization of SO Hamiltonian
 2
$END
```

**说明**：
- **第一次 TDDFT**：计算单重态，使用 `istore 1` 保存波函数
- **第二次 TDDFT**：计算三重态，使用 `istore 2` 保存波函数
- **第三次 TDDFT**：SOC 后处理，使用 `isoc 2`、`nfiles 2` 读取前两次的波函数
- **重要**：计算必须按照 `isf=0, isf=1` 的顺序进行
- 需要使用相对论基组（如 `cc-pVDZ-DK`）和相对论哈密顿（`heff 3` 表示 sf-X2C）

## TDDFT 结构优化

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `TDDFT` → `RESP`

**示例：丁二烯第一激发态结构优化**

```bdf
$COMPASS
Title
 C4H6 TDDFT optimization
Basis
 CC-PVDZ
Geometry
 C   -1.85874726   -0.13257980    0.00000000
 H   -1.95342119   -1.19838319    0.00000000
 H   -2.73563916    0.48057645    0.00000000
 C   -0.63203020    0.44338226    0.00000000
 H   -0.53735627    1.50918564    0.00000000
 C    0.63203020   -0.44338226    0.00000000
 H    0.53735627   -1.50918564    0.00000000
 C    1.85874726    0.13257980    0.00000000
 H    1.95342119    1.19838319    0.00000000
 H    2.73563916   -0.48057645    0.00000000
End Geometry
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
Charge
 0
Spin
 1
$END

$TDDFT
nroot
 0 0 0 1  # Calculate 1Bu state (for C(2h) group: Ag, Au, Bg, Bu)
istore
 1
# TDDFT gradient requires tighter TDDFT convergence criteria
crit_vec
 1.d-6  # default 1.d-5
crit_e
 1.d-8  # default 1.d-7
$END

$RESP
geom
norder
 1  # First-order nuclear derivative (gradient)
method
 2  # TDDFT response properties
nfiles
 1  # Must be the same number as istore in $TDDFT
iroot
 1  # Calculate the gradient of the first root
$END
```

**说明**：
- `BDFOPT` 模块用于结构优化
- `TDDFT` 模块需要设置 `istore` 保存波函数
- TDDFT 梯度计算需要更严格的收敛标准（`crit_vec`、`crit_e`）
- `RESP` 模块用于计算 TDDFT 梯度：
  - `method 2`：TDDFT 响应性质
  - `nfiles` 必须与 `TDDFT` 中的 `istore` 相同
  - `iroot` 指定计算第几个激发态的梯度（注意：这里的 `iroot` 与 `TDDFT` 模块中的 `iroot` 意义不同）

## TDDFT 关键词说明

### 激发态数目控制

1. **`iroot`**：每个不可约表示计算的根数
   - `iroot 1`：每个不可约表示计算 1 个激发态
   - `iroot 4`：每个不可约表示计算 4 个激发态
   - `iroot -4`：计算最低的 4 个激发态（不限定不可约表示）

2. **`nroot`**：为每个不可约表示分别指定根数
   - `nroot 0 0 1 1`：对于 C(2v) 点群（A1, A2, B1, B2），只计算 B1 和 B2 各 1 个激发态

3. **`iwindow`**：指定能量窗口
   - `iwindow 300 800 nm`：计算 300-800 nm 范围内的激发态
   - `iwindow 275 285`：计算 275-285 eV 范围内的激发态（默认单位 eV）

### 方法选择

1. **`isf`**：自旋翻转
   - `isf 0`：计算与参考态自旋相同的激发态（默认，singlet）
   - `isf 1`：计算自旋多重度比基态大 2 的态（triplet，spin-flip up）
   - `isf -1`：计算自旋多重度比基态小 2 的态（spin-flip down）

2. **`itda`**：Tamm-Dancoff 近似
   - `itda 0`：Full TDDFT（默认）
   - `itda 1`：TDA 近似

3. **`idiag`**：对角化方法
   - `idiag 1`：Davidson 方法（默认）
   - `idiag 2`：完全对角化（用于 SOC）
   - `idiag 3`：iVI 方法（用于高能激发态，如 XAS）

4. **`imethod`**：TDDFT 方法类型（通常省略，由 BDF 自动选择）
   - `imethod 1`：R-TDDFT（RHF/RKS）
   - `imethod 2`：U-TDDFT / X-TDDFT（UHF/UKS / ROHF/ROKS）
   - `imethod 3`：SA-TDDFT（较少使用，主要用于调试）

### 波函数存储和读取

1. **`istore`**：存储 TDDFT 波函数
   - `istore 1`：存储到第 1 个临时文件
   - `istore 2`：存储到第 2 个临时文件
   - 用于后续的 SOC 计算或梯度计算

2. **`nfiles`**：读取的波函数文件数（用于 SOC 计算）
   - `nfiles 2`：读取文件 1 和文件 2

### SOC 相关关键词

1. **`isoc`**：SOC 计算标志
   - `isoc 2`：进行 TDDFT-SOC 计算

2. **`ifgs`**：是否在 SOC 处理中包含基态
   - `ifgs 0`：不包括基态
   - `ifgs 1`：包括基态

3. **`imatsoc`**：指定要打印的 SOC 矩阵元
   - 格式：`imatsoc N` 后跟 N 行，每行格式为 `fileA symA stateA fileB symB stateB`

4. **`imatrso`**：指定要计算的跃迁偶极矩
   - 格式：`imatrso N` 后跟 N 行，每行格式为 `I J`

### 收敛控制

1. **`crit_e`**：能量收敛阈值（默认 `1.d-7`）
   - TDDFT 梯度计算建议使用 `1.d-8`

2. **`crit_vec`**：向量收敛阈值（默认 `1.d-5`）
   - TDDFT 梯度计算建议使用 `1.d-6`

3. **`gridtol`**：XC 格点生成容差（用于开壳层分子，减少数值误差）
   - 建议值：`1.d-7`

## 特殊计算方法

### 1. iVI 方法（用于高能激发态）

**用途**：计算高能激发态（如 XAS）时，无需计算所有低能激发态

**示例：乙烯的碳 K-edge XAS**

```bdf
$TDDFT
imethod
 1  # R-TDDFT
idiag
 3  # iVI method
iwindow
 275 285  # Energy range in eV (default unit)
$END
```

### 2. sTDA/sTDDFT（快速近似方法）

**用途**：大体系快速计算，精度略低（误差约 0.2 eV）

**示例**：

```bdf
$TDDFT
iwindow
 300 700 nm
grimmestd  # Use sTDDFT method
$END
```

### 3. TDA 方法

**用途**：Tamm-Dancoff 近似，计算速度更快，但精度略低

**示例**：

```bdf
$TDDFT
itda
 1  # Use TDA
iroot
 10
$END
```

## 注意事项

1. **点群对称性**：
   - 开壳层 TDDFT 不支持非阿贝尔点群，需要强制使用阿贝尔子群（如 `C(1)`）
   - SOC 计算必须使用阿贝尔点群

2. **基组选择**：
   - 相对论计算需要使用相对论基组（如 `cc-pVDZ-DK`、`cc-pVDZ-X2C`）
   - SOC 计算需要使用相对论基组或 SOECP 基组

3. **收敛标准**：
   - TDDFT 梯度计算需要更严格的收敛标准
   - 开壳层分子建议使用 `gridtol` 减少数值误差

4. **SCAN 泛函警告**：
   - 所有 SCAN 家族泛函（如 SCAN0、r2SCAN）都存在"三重态不稳定"问题
   - 不要用于 TDDFT 自旋翻转计算（如对闭壳层体系计算三重激发态）
   - 推荐使用 TDA

5. **SOC 计算顺序**：
   - 必须按照 `isf=0, isf=1` 的顺序进行
   - 当 `ifgs=0` 时，计算的激发态数越多，结果越准
   - 当 `ifgs=1` 时，`iroot` 太多反倒会令精度降低，一般以几十为宜

6. **态跟踪（透热态）**：
   - 在结构优化中，可以使用透热态跟踪（将 `RESP` 模块的 `iroot` 设为负值）
   - 例如：`iroot -2` 表示第一步跟踪第 2 个激发态，之后根据重叠积分自动跟踪

## YAML 输入示例

### 基本 TDDFT 计算

```yaml
task:
  type: tddft
  description: "H2O TDDFT calculation"

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
  tddft:
    n_states: 4  # Calculate 4 excited states
    # iroot will be automatically set based on point group
```

### Singlet + Triplet TDDFT

```yaml
task:
  type: tddft
  description: "H2O TDDFT singlet and triplet"

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
  tddft:
    singlet:
      n_states: 4
    triplet:
      n_states: 4
```

### Spin-Adapted TDDFT

```yaml
task:
  type: tddft
  description: "N2+ X-TDDFT calculation"

molecule:
  name: "N2+"
  charge: 1
  multiplicity: 2
  coordinates:
    - N  0.00  0.00  0.00
    - N  0.00  0.00  1.1164
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: aug-cc-pvtz

settings:
  tddft:
    spin_adapted: true  # Use X-TDDFT
    n_states: 5
  compass:
    symmetry:
      group: D(2h)  # Force to use D2h symmetry
```

### TDDFT-SOC

```yaml
task:
  type: tddft
  description: "CH2S TDDFT-SOC calculation"

molecule:
  name: "CH2S"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.000000  0.000000  -1.039839
    - S  0.000000  0.000000   0.593284
    - H  0.000000  0.932612  -1.626759
    - H  0.000000 -0.932612  -1.626759
  units: angstrom

method:
  type: dft
  functional: pbe0
  basis: cc-pVDZ-DK  # Relativistic basis set

settings:
  tddft:
    singlet:
      n_states: 10
      store_wavefunction: 1
    triplet:
      n_states: 10
      store_wavefunction: 2
    soc:
      enabled: true
      include_ground_state: true
      nfiles: 2
  xuanyuan:
    heff: 3  # sf-X2C Hamiltonian
    hsoc: 2  # SOC integral
```

## 实现建议

### 转换器中的处理

1. **基本 TDDFT 计算**：
   ```python
   if task_type == 'tddft':
       blocks.append(self.generate_compass_block(config))
       blocks.append(self.generate_xuanyuan_block(config))
       blocks.append(self.generate_scf_block(config))
       blocks.append(self.generate_tddft_block(config))
   ```

2. **多步 TDDFT 计算**：
   ```python
   tddft_settings = settings.get('tddft', {})
   if tddft_settings.get('singlet') and tddft_settings.get('triplet'):
       # Generate two TDDFT blocks
       blocks.append(self.generate_tddft_block(config, isf=0))
       blocks.append(self.generate_tddft_block(config, isf=1))
   elif tddft_settings.get('soc', {}).get('enabled'):
       # Generate three TDDFT blocks
       blocks.append(self.generate_tddft_block(config, isf=0, istore=1))
       blocks.append(self.generate_tddft_block(config, isf=1, istore=2))
       blocks.append(self.generate_tddft_soc_block(config))
   ```

3. **TDDFT 结构优化**：
   ```python
   if task_type == 'tddft_optimize':
       blocks.append(self.generate_compass_block(config))
       blocks.append(self.generate_bdfopt_block(config))
       blocks.append(self.generate_xuanyuan_block(config))
       blocks.append(self.generate_scf_block(config))
       blocks.append(self.generate_tddft_block(config, istore=1))
       blocks.append(self.generate_resp_block(config, method=2, nfiles=1))
   ```

## 参考文档

- BDF TDDFT 手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/TD.rst`
- BDF 溶剂化模型手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Solvent-Model.rst`
- TDDFT 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (tddft 部分)
- SCF 单点能量计算：`research/module_organization/SCF_ENERGY.md`
- 溶剂化模型：`research/module_organization/SOLVENT_MODELS.md`

