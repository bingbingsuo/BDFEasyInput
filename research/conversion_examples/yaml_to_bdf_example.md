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
- `settings.geometry_optimization.solver` → `BDFOPT solver 1`
- 使用 RESP 模块计算梯度（GRAD 模块仅支持 HF 和 MCSCF，不支持 DFT）
- RESP 模块参数：`geom`、`norder 1`（梯度）、`method 1`（SCF 梯度）

---

## 示例 4：TDDFT 计算

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
SAORB
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
    1. 第一次：`ISF=0`，计算 singlet TDDFT（如 `IMETHOD 1, ITDA 1, IEXIT 10, ISTORE 1`）。
    2. 第二次：`ISF=1`，计算 triplet TDDFT（同样设置 `IMETHOD/ITDA/IDIAG/IEXIT/ISTORE 2`）。
    3. 第三次：不开新的 TDDFT 能量计算，而是设置 `ISOC`/`NFILES`/`IMATSOC`/`IMATRSO` 等，基于前两次存储的 TDDFT 波函数做 SOC 后处理，并可用 `IDIAG 2` 对 SOC 修正的哈密顿量做精确对角化。  
       - 示例参见 BDF 自带算例：`/Users/bsuo/bdf/bdf-pkg-full/tests/input/test109.inp`（CH2S LC-BLYP/def2-QZVP TDDFT-SOC 计算）。

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

