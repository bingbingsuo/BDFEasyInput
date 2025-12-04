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

## 🎯 下一步

1. **完善映射表**：补充更多方法和基组
2. **实现转换器**：基于已确认的规则开始实现
3. **测试验证**：使用实际 BDF 输入文件验证转换结果

---

**研究状态**：核心格式已理解，关键问题已确认，可以开始实现转换器。

