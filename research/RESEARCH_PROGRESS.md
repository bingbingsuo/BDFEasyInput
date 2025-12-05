# BDF 输入格式研究进展

## ✅ 已确认的重要信息

### 1. Occupied 关键词 ✅
**确认日期**：2024年

**信息**：
- 指定 RHF 或 RKS 计算时不可约表示的双占据轨道数目
- 采用 D2h 及其子群的对称性
- **默认可以不输入**，BDF 会自动计算
- **如果用户指定了值，直接使用用户输入**

**影响**：
- 简化了实现：不需要计算占据轨道数
- 用户可以选择指定或不指定
- YAML 中作为可选字段：`settings.scf.occupied`

### 2. 大小写敏感性 ✅
**确认日期**：2024年

**信息**：
- **模块名大小写不敏感**：`$COMPASS`、`$compass`、`$Compass` 都可以
- **关键词大小写不敏感**：`Title`、`title`、`TITLE` 都可以
- **BDF 会自动处理**：BDF 会自动标准化大小写

**建议格式**：
- 模块名：使用大写（`$COMPASS`、`$SCF`）
- 关键词：使用首字母大写（`Title`、`Basis`）
- 结束标记：使用大写（`$END`）

**影响**：
- 实现时可以使用标准格式
- 提高生成文件的可读性
- 不需要担心大小写问题

## 📊 研究完成度

### 基础格式 ✅
- [x] 模块化结构理解
- [x] 关键词格式理解
- [x] 坐标格式理解
- [x] 大小写敏感性确认

### 模块分析 ✅
- [x] COMPASS 模块关键词
- [x] XUANYUAN 模块
- [x] SCF 模块关键词
- [x] BDFOPT 模块
- [x] TDDFT 模块关键词
- [x] RESP 模块关键词

### 映射关系 ✅
- [x] 任务类型 → 模块组合
- [x] 方法类型映射（RHF/UHF/RKS/UKS/ROHF/ROKS）
- [x] 基组名称映射
- [x] 坐标格式转换规则
- [x] Occupied 处理规则
- [x] 几何优化模块选择（RESP vs GRAD）
- [x] Spin-adapted TDDFT 支持（SCF 采用 ROHF/ROKS，TDDFT 默认使用 X-TDDFT，IMETHOD 通常省略）

### 待完善 ⏳
- [ ] 更多 DFT 泛函的 BDF 名称
- [ ] 频率计算的完整模块组合
- [ ] SCF 收敛迭代次数关键词
- [ ] 更多高级参数的关键词
- [ ] Spin-adapted TDDFT 的完整参数配置（IRO 等）

### 溶剂化效应支持

### 支持的溶剂模型
- **COSMO**、**CPCM**、**IEFPCM**、**SS(V)PE**、**SMD**、**ddCOSMO**
- 默认模型：IEFPCM
- 所有模型均支持基态和激发态的单点、梯度、Hessian 计算

### 溶剂类型指定
- 预定义溶剂名称：`water`、`methanol`、`acetonitrile`、`dmso` 等（见 `Solvent-Dielectric.rst`）
- 用户指定介电常数：`solvent user` + `dielectric` + `opticalDielectric`（用于非平衡溶剂化）

### 孔穴自定义
- `cavity`：生成孔穴表面的方式（`swig`、`switching`、`ses`、`sphere`）
- `radiusType`：半径类型（`UFF`、`Bondi`）
- `vdWScale`：vdW 半径缩放因子（默认 1.1）
- `radii`：自定义原子半径
- `cavityNGrid` / `cavityPrecision`：格点精度

### 非静电溶剂化能
- `nonels`：开启非静电溶剂化能计算（`dis`、`rep`、`cav`）
- `solventAtoms`、`solventRho`、`solventRadius`：溶剂参数

### TDDFT 溶剂化效应
- **垂直吸收**：`solneqlr`（线性响应非平衡）、`solneqss`（态特定非平衡）、cLR（矫正线性响应）
- **激发态几何优化**：`soleqlr`（平衡溶剂化，在 TDDFT 和 RESP 模块中）
- **垂直发射**：`soleqss`（平衡）+ `emit`（非平衡基态）

### 模块位置
- **SCF 模块**：`solvent`、`solmodel`、`cavity`、`nonels` 等
- **TDDFT 模块**：`solneqlr`、`soleqlr`
- **RESP 模块**：`solneqlr`、`soleqlr`、`solneqss`、`soleqss`

**参考文档**：
- `research/module_organization/SOLVENT_MODELS.md`
- BDF 手册：`Solvent-Model.rst`、`Solvent-Dielectric.rst`

## 新确认信息 ✅
- [x] SAORB 关键词使用规则：
  - 默认不添加，只有在出现 MCSCF 或 TRAINT 模块时才默认添加
  - 如果 COMPASS 中要求使用 RI 基组（RI-J/RI-K/RI-C/CD-RI），则无需添加
  - SAORB 用于要求 XUANYUAN 计算并存储对称匹配轨道的积分，主要用于 MCSCF 和多参考态电子相关计算
- [x] 自旋多重度（SPINMULTI/SPIN）默认行为：
  - SCF 关键词 `spinmul` 用来控制电子态的自旋多重度
  - **AI 分析用户任务时应该提醒用户设置自旋多重度**
  - 如果用户未设置，BDF 将按以下规则处理：
    * 偶数电子数 → 自旋多重度 = 1（闭壳层）
    * 奇数电子数 → 自旋多重度 = 2（开壳层）
  - 强烈建议用户在 YAML 中明确设置自旋多重度
- [x] COMPASS 模块点群（Group）和 NoSymm 关键词：
  - **Group 关键词**：
    - 有效值：D(2h), D(2), C(2v), C(2h), C(s), C(2), C(1)
    - 用户设置的值必须在此列表中
    - 大小写不敏感（如 'c2v' 和 'C(2v)' 等价）
    - 如果用户忘记加括号，转换器会自动补上括号（如 'C2v' → 'C(2v)'）
    - 如果用户设置了此关键词且值有效，则在 COMPASS 模块中添加 Group 关键词
  - **NoSymm 关键词**：
    - 强制计算不使用点群对称性
    - **与 group 关键词互斥**：只能出现一个
    - **nosymm 优先**：如果同时设置了 group 和 nosymm，nosymm 优先，group 将被忽略

## 📝 关键发现总结

1. **模块化设计**：BDF 使用模块化输入，每个模块独立
2. **关键词+值模式**：值在关键词下一行
3. **坐标单位**：BDF 默认使用 **Angstrom**，也可以通过 `Unit` 关键词显式改为 Bohr；我们的 YAML 同样默认使用 angstrom
4. **方法选择**：根据 type 和 multiplicity 自动选择
5. **Occupied**：可选，默认不输出，用户指定则使用
6. **大小写**：不敏感，但建议使用标准格式
7. **几何优化**：使用 RESP 模块而非 GRAD 模块（GRAD 仅支持 HF/MCSCF）
8. **Spin-adapted TDDFT**：
   - 使用 `settings.tddft.spin_adapted: true` 启用
   - SCF 方法自动选择为 ROHF（HF）或 ROKS（DFT）
   - TDDFT 部分推荐省略 `IMETHOD`，由 BDF 根据 SCF 自动选择：RHF/RKS→1，ROHF/ROKS/UHF/UKS→2（X-TDDFT）
   - 我们统一默认采用基于 ROHF/ROKS 的 **X-TDDFT（IMETHOD=2）**，而不使用 SA-TDDFT（IMETHOD=3，少量调试场景）
9. **SAORB 关键词**：
   - 默认不添加，只有在出现 MCSCF 或 TRAINT 模块时才默认添加
   - 如果 COMPASS 中要求使用 RI 基组（RI-J/RI-K/RI-C/CD-RI），则无需添加
   - SAORB 用于要求 XUANYUAN 计算并存储对称匹配轨道的积分，主要用于 MCSCF 和多参考态电子相关计算
10. **COMPASS 模块点群（Group）和 NoSymm 关键词**：
    - **Group 关键词**：
      - 有效值：D(2h), D(2), C(2v), C(2h), C(s), C(2), C(1)
      - 用户设置的值必须在此列表中，转换器会验证
      - 大小写不敏感（如 'c2v' 和 'C(2v)' 等价）
      - 如果用户忘记加括号，转换器会自动补上括号（如 'C2v' → 'C(2v)'）
      - 如果用户设置了此关键词且值有效，则在 COMPASS 模块中添加 Group 关键词
    - **NoSymm 关键词**：
      - 强制计算不使用点群对称性
      - BDF 关键词使用 "NoSymm"（可读性更强，而非 "NOSY"）
      - **与 group 关键词互斥**：只能出现一个
      - **nosymm 优先**：如果同时设置了 group 和 nosymm，nosymm 优先，group 将被忽略
11. **电荷（CHARGE）和自旋多重度（SPINMULTI/SPIN）**：
    - **必需字段**：`molecule.charge` 和 `molecule.multiplicity` 必须在 YAML 中显式设置
    - **直接复制**：转换器会直接将这两个值复制到 SCF 模块的 `Charge` 和 `Spin` 关键词
    - **无论值是多少**：即使 `charge=0` 或 `multiplicity=1`，也会添加到 SCF 模块中
    - **目的**：确保用户清楚地知道自己在计算什么体系（电荷和电子态）
    - **验证**：如果 YAML 中缺少这两个字段，转换器会抛出 `ValueError`
    - **AI 提醒**：AI 分析用户任务时必须提醒用户设置这两个字段

## 🎯 下一步

### 短期目标（1-2 周）
1. **频率计算支持**：实现 `task.type: frequency` 的处理
2. **输入验证增强**：实现 YAML Schema 验证，添加参数检查
3. **代码重构**：拆分 `converter.py` 为多个模块，改进代码组织

### 中期目标（1-2 月）
1. **扩展计算类型**：MP2、MCSCF、NMR 等
2. **AI 模块实现**：AI 客户端、任务规划器、结果分析器
3. **执行模块**：BDFAutotest 集成

### 长期目标（3-6 月）
1. **完整工作流**：从任务规划到结果分析的端到端流程
2. **用户界面**：命令行工具完善、可能的 GUI
3. **文档完善**：用户指南、API 文档

---

**研究状态**：✅ 核心格式已理解，关键问题已确认，转换器基本实现完成。

**当前进度**：约 60% 完成（核心转换器 70%，关键词映射 90%，文档 85%）

**详细进度**：参见 [WORK_PROGRESS.md](../WORK_PROGRESS.md)

