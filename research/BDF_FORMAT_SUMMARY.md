# BDF 输入格式研究总结

## 📋 研究概述

基于您提供的格式说明和 8 个实际 BDF 输入文件示例，我们已经完成了初步的格式分析。

## ✅ 已确认的格式特点

### 1. 模块化结构
- **格式**：`$MODULE_NAME` ... `$END`
- **主要模块**：
  - `COMPASS`：分子结构、基组、对称性
  - `XUANYUAN`：积分计算
  - `SCF`：HF/DFT 计算
  - `BDFOPT`：几何优化
  - `TDDFT`：含时密度泛函
  - `RESP`：梯度、Hessian、性质
  - `GRAD`：梯度计算

### 2. 关键词格式
- **模式**：关键词在单独一行，值在下一行（或多行）
- **注释**：使用 `#` 符号
- **大小写**：✅ 不敏感，BDF 会自动处理（建议使用首字母大写）

### 3. 坐标格式
- **格式**：`原子符号 X Y Z`（自由格式）
- **单位**：默认 Bohr（可通过 `Unit` 指定）
- **块结构**：`Geometry` ... `End geometry`

### 4. 方法指定
- **HF**：`RHF`（闭壳层）或 `UHF`（开壳层）或 `ROHF`（限制性开壳层，用于 spin-adapted TDDFT 场景）
- **DFT**：`RKS`（闭壳层）或 `UKS`（开壳层）或 `ROKS`（限制性开壳层，用于 spin-adapted TDDFT 场景）+ `dft functional [名称]`
- **TDDFT**（IMETHOD 一般可以省略，由 BDF 自动选择）：
  - `IMETHOD 1`：R-TDDFT（通常对应 RHF/RKS）
  - `IMETHOD 2`：U-TDDFT / X-TDDFT（对应 UHF/UKS 以及 ROHF/ROKS，包含 spin-adapted TDDFT 的默认实现）
  - `IMETHOD 3`：SA-TDDFT（较少使用的 spin-adapted 变体，主要用于程序调试）

## 📊 已建立的映射关系

### 任务类型 → 模块组合

| YAML task.type | BDF 模块组合 |
|----------------|--------------|
| `energy` | `COMPASS` + `XUANYUAN` + `SCF` |
| `optimize` | `COMPASS` + `BDFOPT` + `XUANYUAN` + `SCF` + `RESP` |
| `tddft` | `COMPASS` + `XUANYUAN` + `SCF` + `TDDFT` |

**注意**：
- 几何优化使用 **RESP 模块**而非 GRAD 模块
- **GRAD 模块仅支持 HF 和 MCSCF**，不支持 DFT
- RESP 模块支持所有 SCF 方法（HF 和 DFT）以及 TDDFT

### 方法映射

**SCF 方法映射**：

| YAML | BDF SCF 模块 |
|------|--------------|
| `method.type: hf, multiplicity: 1` | `RHF` |
| `method.type: hf, multiplicity > 1` | `UHF` |
| `method.type: dft, functional: pbe0, multiplicity: 1` | `RKS` + `dft functional PBE0` |
| `method.type: dft, functional: b3lyp, multiplicity > 1` | `UKS` + `dft functional B3lyp` |
| `method.type: hf, spin_adapted: true` | `ROHF`（限制性开壳层） |
| `method.type: dft, spin_adapted: true` | `ROKS`（限制性开壳层） |

**TDDFT 方法映射（概念层面，实际输入中通常省略 IMETHOD）**：

| YAML | BDF TDDFT 模块（默认行为） |
|------|---------------------------|
| `task.type: tddft`（RHF/RKS） | 默认 `IMETHOD=1`（R-TDDFT） |
| `task.type: tddft`（UHF/UKS） | 默认 `IMETHOD=2`（U-TDDFT） |
| `task.type: tddft, spin_adapted: true`（ROHF/ROKS） | 默认 `IMETHOD=2`（X-TDDFT，spin-adapted 方案） |

### 基组映射

| YAML | BDF Basis |
|------|-----------|
| `method.basis: cc-pvdz` | `cc-pvdz` |
| `method.basis: 6-31g*` | `6-31G*` |
| `method.basis: 3-21g` | `3-21G` |

## 📝 关键发现

1. **坐标单位**：BDF 默认使用 **Angstrom**，也可以通过 `Unit` 关键词显式设置为 `Bohr`；我们的 YAML 也默认使用 `angstrom`，因此通常不需要做单位转换（只有在用户明确选择 Bohr 时才需要转换）
2. **方法类型选择**：需要根据 `method.type` 和 `multiplicity` 自动选择 RHF/UHF/RKS/UKS
3. **Occupied 格式**：✅ 已确认
   - 指定 RHF 或 RKS 计算时不可约表示的双占据轨道数目（D2h 及其子群）
   - **默认可以不输入**，BDF 会自动计算
   - **如果用户指定了值，直接使用用户输入**
   - 格式：四个整数，空格分隔（如 `3 0 1 0`）
4. **模块顺序**：模块必须按计算流程顺序排列
5. **Spin-adapted TDDFT**：✅ 已确认
   - 使用 `settings.tddft.spin_adapted: true` 启用
   - SCF 方法自动选择为 **ROHF**（HF）或 **ROKS**（DFT）
   - TDDFT 中推荐省略 `IMETHOD`，由 BDF 自动选择：RHF/RKS→1，ROHF/ROKS/UHF/UKS→2
   - 我们统一默认采用基于 ROHF/ROKS 的 **X-TDDFT（IMETHOD=2）**；SA-TDDFT（IMETHOD=3）仅作为专家/调试选项

## ⚠️ 待确认问题

1. ~~**Occupied 格式**~~：✅ 已确认
   - 指定 RHF 或 RKS 计算时不可约表示的双占据轨道数目
   - 采用 D2h 及其子群
   - 默认可以不输入，如果用户指定则直接使用
2. ~~**大小写敏感性**~~：✅ 已确认
   - 模块名和关键词大小写不敏感
   - BDF 会自动处理大小写
   - 建议使用标准格式（模块名大写，关键词首字母大写）
3. **默认值**：各参数的默认值
4. **频率计算**：频率计算的完整模块组合
5. **更多参数**：SCF 收敛迭代次数等参数的关键词

## 📁 研究文档

- **详细分析**：`research/notes/bdf_format_analysis.md`
- **研究发现**：`research/notes/findings.md`
- **映射表**：
  - `research/mapping_tables/method_mapping.yaml`
  - `research/mapping_tables/basis_mapping.yaml`
  - `research/mapping_tables/keyword_mapping.yaml`

## 🎯 下一步

1. **完善映射表**：补充更多方法和基组
2. **解决待确认问题**：查阅 BDF 文档，测试验证
3. **建立转换规则**：实现坐标转换、方法选择等逻辑
4. **创建模板**：为不同计算类型创建 BDF 输入模板

---

**研究状态**：初步分析完成，映射关系已建立，待进一步完善。

