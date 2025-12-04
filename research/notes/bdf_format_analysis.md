# BDF 输入格式详细分析

**分析日期**：2024年  
**基于示例**：test001.inp, test002.inp, test003.inp, test004.inp, test006.inp, test064.inp, test073.inp

## 1. 基本格式规则

### 1.1 模块结构
- **模块开始**：`$MODULE_NAME`（如 `$COMPASS`、`$SCF`）
- **模块结束**：`$END` 或 `$end`（大小写不敏感）
- **模块顺序**：按计算流程顺序排列

### 1.2 关键词格式
- **关键词位置**：单独一行
- **值的位置**：关键词的下一行（或多行）
- **注释**：使用 `#` 符号，可以在行首或行尾
- **大小写**：模块名和关键词大小写可能不敏感（需要验证）

### 1.3 文件结构
```
# 文件头注释（可选）
$MODULE1
Keyword1
  value1
Keyword2
  value2
$END

$MODULE2
Keyword1
  value1
$END
```

**大小写敏感性**：
- ✅ **模块名大小写不敏感**：`$COMPASS`、`$compass`、`$Compass` 都可以
- ✅ **关键词大小写不敏感**：`Title`、`title`、`TITLE` 都可以
- ✅ **BDF 会自动处理**：BDF 会自动标准化大小写
- 💡 **建议**：为了可读性和一致性，建议使用标准格式（模块名大写，关键词首字母大写）

## 2. COMPASS 模块分析

### 2.1 功能
- 读取分子结构
- 读取基组
- 判断分子对称性
- 产生对称匹配的轨道
- 存储为二进制文件

### 2.2 关键词列表

| 关键词 | 值格式 | 说明 | 示例 |
|--------|--------|------|------|
| `Title` | 单行文本 | 计算标题 | `CH2 Molecule test run` |
| `Basis` | 单行文本 | 基组名称 | `cc-pvqz`, `6-31G`, `3-21G` |
| `Geometry` | 多行坐标 | 分子坐标块开始 | - |
| `End geometry` / `End Geometry` | 无值 | 坐标块结束 | - |
| `Unit` / `UNIT` | 单行文本 | 坐标单位 | `Angstrom`（默认），可改为 `Bohr` |
| `Check` | 无值 | 检查选项 | - |
| `SAORB` | 无值 | 对称匹配轨道 | - |
| `Skeleton` | 无值 | 骨架选项 | - |
| `Group` | 单行文本 | 对称群 | `D(6h)`, `C(2v)`, `C(1)` |

### 2.3 坐标格式

**格式**：`原子符号 X坐标 Y坐标 Z坐标`

**示例**：
```
Geometry
 C     0.000000        0.00000        0.31399
 H     0.000000       -1.65723       -0.94197
 H     0.000000        1.65723       -0.94197
End geometry
```

**特点**：
- 自由格式（空格分隔）
- 坐标值可以是整数或浮点数
- 单位通过 `Unit` 关键词指定（**默认 Angstrom**；显式写 `Bohr` 时使用原子单位）
- 坐标块在 `Geometry` 和 `End geometry` 之间

### 2.4 COMPASS 模块示例

```bdf
$COMPASS 
Title
 CH2 Molecule test run, cc-pvqz 
Basis
 cc-pvqz
Geometry
 C     0.000000        0.00000        0.31399
 H     0.000000       -1.65723       -0.94197
 H     0.000000        1.65723       -0.94197
End geometry
UNIT
 Bohr
SAORB
Check
$END
```

## 3. XUANYUAN 模块分析

### 3.1 功能
- 计算单、双电子积分

### 3.2 关键词
- 在简单情况下可以为空（只有 `$XUANYUAN` 和 `$END`）
- 可能有 `direct`、`schwarz` 等选项（见 test073.inp）

### 3.3 示例
```bdf
$XUANYUAN
$END
```

或：
```bdf
$XUANYUAN
direct
schwarz
$END
```

## 4. SCF 模块分析

### 4.1 功能
- 执行 Hartree-Fock 或 DFT 计算

### 4.2 方法类型

| 关键词 | 说明 | 适用体系 |
|--------|------|----------|
| `RHF` | 限制性 Hartree-Fock | 闭壳层 |
| `UHF` | 非限制性 Hartree-Fock | 开壳层 |
| `RKS` | 限制性 Kohn-Sham (DFT) | 闭壳层 |
| `UKS` | 非限制性 Kohn-Sham (DFT) | 开壳层 |

### 4.3 关键词列表

| 关键词 | 值格式 | 说明 | 示例 |
|--------|--------|------|------|
| `RHF` / `UHF` / `RKS` / `UKS` | 无值 | 方法类型 | - |
| `Occupied` | 多值（空格分隔） | 占据轨道（RHF） | `3 0 1 0` |
| `Alpha` | 整数 | Alpha 轨道数（UHF） | `12` |
| `Beta` | 整数 | Beta 轨道数（UHF） | `12` |
| `dft functional` | 单行文本 | DFT 泛函名称 | `B3lyp`, `GB3LYP` |
| `charge` | 整数 | 分子电荷 | `0` |
| `spin` | 整数 | 自旋多重度 | `2` |
| `ThreshConverg` | 两个值（空格分隔） | 收敛阈值 | `1.D-10 1.D-6` |

### 4.4 SCF 模块示例

**RHF 示例**：
```bdf
$SCF
RHF
Occupied
3  0  1  0
$END
```

**UHF 示例**：
```bdf
$SCF
UHF
Alpha
12
Beta
12
$END
```

**DFT 示例**：
```bdf
$SCF
RKS
dft functional
 B3lyp
$END
```

**UKS 示例**：
```bdf
$SCF
UKS
dft functional
 GB3LYP
charge
 0
spin
 2
ThreshConverg
 1.D-10 1.D-6
$END
```

### 4.5 Occupied 格式说明

`Occupied` 关键词的值格式：`a b c d`（四个整数，空格分隔）

**含义**：
- 指定 RHF 或 RKS 计算时不可约表示的双占据轨道数目
- 采用 D2h 及其子群的对称性
- 四个整数分别对应不同不可约表示的双占据轨道数

**使用规则**：
- **默认可以不输入**：如果用户不指定，BDF 会自动计算
- **用户输入优先**：如果用户在 YAML 中指定了值，直接使用用户输入
- **仅用于 RHF/RKS**：UHF/UKS 使用 `Alpha` 和 `Beta` 而不是 `Occupied`

**示例**：
```bdf
$SCF
RHF
Occupied
3 0 1 0
$END
```
表示：第一个不可约表示 3 个双占据轨道，第三个不可约表示 1 个双占据轨道，其他为 0。

## 5. BDFOPT 模块分析

### 5.1 功能
- 几何优化

### 5.2 关键词

| 关键词 | 值格式 | 说明 | 示例 |
|--------|--------|------|------|
| `solver` | 整数 | 求解器类型 | `1` |

### 5.3 示例
```bdf
$BDFOPT
solver
1
$END
```

## 6. TDDFT 模块分析

### 6.1 功能
- 执行含时密度泛函
- 基于含时密度泛函的自旋轨道耦合等计算

### 6.2 关键词列表

| 关键词 | 值格式 | 说明 | 示例 |
|--------|--------|------|------|
| `imethod` | 整数 | 方法类型 | `1` (R-TDDFT), `2` (U-TDDFT) |
| `isf` | 整数 | 自旋标志 | `0` (自旋守恒) |
| `itda` | 整数 | TDA 近似 | `0` (关闭), `1` (开启) |
| `idiag` | 整数 | 对角化方法 | `1` |
| `iprint` | 整数 | 打印级别 | `3` |
| `Nexit` | 四个整数 | 退出状态 | `0 0 0 1` |
| `istore` | 整数 | 存储选项 | `1` |
| `lefteig` | 无值 | 左本征向量 | - |
| `crit_vec` | 浮点数 | 向量收敛标准 | `1.d-4` |
| `crit_e` | 浮点数 | 能量收敛标准 | `1.d-6` |
| `gridtol` | 浮点数 | 网格容差 | `1.d-7` |

### 6.3 示例
```bdf
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

## 7. RESP 模块分析

### 7.1 功能
- 执行分子能量梯度（SCF 和 TDDFT）
- Hessian 计算
- TDDFT 的激发态梯度
- 非绝热耦合向量
- 分子性质（极化率、超极化率等）

**重要**：
- **RESP 模块是几何优化的推荐选择**（而非 GRAD 模块）
- GRAD 模块仅支持 HF 和 MCSCF，不支持 DFT
- RESP 模块支持所有 SCF 方法（HF 和 DFT）以及 TDDFT

### 7.2 关键词列表

| 关键词 | 值格式 | 说明 | 示例 |
|--------|--------|------|------|
| `geom` | 无值 | 几何优化 | - |
| `norder` | 整数 | 导数阶数 | `1` (梯度) |
| `method` | 整数 | 方法类型 | `2` (TDDFT 梯度) |
| `nfiles` | 整数 | 文件数 | `1` |
| `reusez` | 整数 | 重用选项 | `2` |
| `ignore` | 整数 | 忽略选项 | `1` |
| `iroot` | 整数 | 根状态 | `1` (第1个激发态) |

### 7.3 示例
```bdf
$resp
geom
norder
1
method
2
nfiles
1
reusez
2
ignore
1
$end
```

## 8. 其他模块

### 8.1 GRAD 模块
- **仅支持 Hartree-Fock 和 MCSCF**
- 不支持 DFT 方法
- **注意**：几何优化通常使用 RESP 模块而非 GRAD 模块
- 可以为空（只有 `$GRAD` 和 `$END`）

### 8.2 RESP 模块（推荐用于几何优化）
- **支持 SCF（HF/DFT）梯度**：`method 1`
- **支持 TDDFT 梯度**：`method 2`
- **支持 Hessian 计算**：`norder 2`
- 用于几何优化、频率计算、性质计算

### 8.2 MCSCF 模块
- 多组态自洽场计算
- 包含 `core`、`close`、`active`、`actel`、`spin`、`symmtry`、`maciter`、`Roots`、`quasi`、`guga` 等关键词

## 9. 典型计算流程

### 9.1 单点能计算（RHF）
```
$COMPASS
  [分子结构和基组]
$END

$XUANYUAN
$END

$SCF
  RHF
  Occupied
    [占据轨道]
$END
```

### 9.2 单点能计算（DFT）
```
$COMPASS
  [分子结构和基组]
$END

$XUANYUAN
$END

$SCF
  RKS
  dft functional
    [泛函名称]
$END
```

### 9.3 几何优化
```
$COMPASS
  [初始几何结构]
$END

$BDFOPT
  solver
    1
$END

$XUANYUAN
$END

$SCF
  [SCF 设置]
$END

$resp
  geom
  norder
    1
  method
    1  # 1=SCF梯度, 2=TDDFT梯度
$end
```

**注意**：
- 几何优化使用 **RESP 模块**计算梯度
- **GRAD 模块仅支持 Hartree-Fock 和 MCSCF**，不支持 DFT
- RESP 模块支持 SCF（HF/DFT）梯度和 TDDFT 梯度

### 9.4 TDDFT 计算
```
$COMPASS
  [分子结构和基组]
$END

$XUANYUAN
$END

$SCF
  [SCF 设置]
$END

$TDDFT
  [TDDFT 参数]
$END
```

### 9.5 TDDFT 几何优化
```
$COMPASS
  [初始几何结构]
$END

$BDFOPT
  solver
    1
$END

$XUANYUAN
$END

$SCF
  [SCF 设置]
$END

$TDDFT
  [TDDFT 参数]
$END

$resp
  geom
  norder
    1
  method
    2
  [其他参数]
$end
```

## 10. 重要发现

### 10.1 格式特点
1. **模块化设计**：每个模块独立，有自己的关键词
2. **关键词+值模式**：值在关键词下一行
3. **自由格式**：坐标等数据使用自由格式
4. **大小写**：模块名和关键词可能不敏感（`$SCF` 和 `$scf` 都出现）

### 10.2 坐标单位
- 默认单位是 **Bohr**
- 可以通过 `Unit` / `UNIT` 关键词指定（大小写不敏感）
- 我们的 YAML 使用 Angstrom，需要转换

### 10.3 大小写敏感性 ✅ 已确认
- **模块名大小写不敏感**：`$COMPASS`、`$compass`、`$Compass` 都可以
- **关键词大小写不敏感**：`Title`、`title`、`TITLE` 都可以
- **BDF 会自动处理**：BDF 会自动标准化大小写
- **建议格式**：为了可读性，使用标准格式（模块名大写，关键词首字母大写）

### 10.3 基组名称
- 直接使用基组名称（如 `cc-pvqz`、`6-31G`、`3-21G`）
- 大小写可能不敏感（`CC-PVDZ` 和 `cc-pvdz` 都出现）

### 10.4 DFT 泛函
- 通过 `dft functional` 关键词指定
- 泛函名称可能有变体（`B3lyp` vs `GB3LYP`）

## 11. 待确认问题

1. ~~**Occupied 格式**~~：✅ 已确认
   - 指定 RHF 或 RKS 计算时不可约表示的双占据轨道数目（D2h 及其子群）
   - 默认可以不输入，BDF 会自动计算
   - 如果用户指定了值，直接使用用户输入
2. ~~**大小写敏感性**~~：✅ 已确认
   - 模块名和关键词大小写不敏感
   - BDF 会自动处理大小写
   - 建议使用标准格式（模块名大写，关键词首字母大写）以提高可读性
3. **默认值**：哪些参数有默认值？
4. **单位**：除了坐标单位，其他参数的单位是什么？
5. **对称性**：Group 关键词的格式和选项
6. **更多模块**：是否还有其他常用模块？

## 12. 映射关系初步建立

### 12.1 任务类型映射

| YAML task.type | BDF 模块组合 |
|----------------|--------------|
| `energy` | `COMPASS` + `XUANYUAN` + `SCF` |
| `optimize` | `COMPASS` + `BDFOPT` + `XUANYUAN` + `SCF` + `GRAD` |
| `frequency` | 待确认 |
| `tddft` | `COMPASS` + `XUANYUAN` + `SCF` + `TDDFT` |

### 12.2 方法映射

| YAML method.functional | BDF SCF 关键词 |
|------------------------|----------------|
| `hf` | `RHF` 或 `UHF` |
| `pbe0` | `RKS` + `dft functional PBE0` |
| `b3lyp` | `RKS` + `dft functional B3lyp` |

### 12.3 基组映射

| YAML method.basis | BDF Basis 值 |
|-------------------|--------------|
| `cc-pvdz` | `cc-pvdz` 或 `CC-PVDZ` |
| `6-31g*` | `6-31G*` |
| `3-21g` | `3-21G` |

---

**下一步**：需要更多示例来完善映射关系，特别是频率计算和其他高级功能。

