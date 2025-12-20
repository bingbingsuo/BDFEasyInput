# Schema 集成功能测试生成文件

## 📋 概述

本目录包含 BDFEasyInput 与 bdfeasyinput_schema 集成后的功能测试生成文件。

**生成日期**: 2025年1月  
**测试脚本**: `tests/test_schema_integration_generation.py`

## 📁 生成的文件

### 1. 水分子单点能计算 (PBE0)

- **YAML**: `h2o_energy_pbe0.yaml`
- **BDF**: `h2o_energy_pbe0.inp`
- **描述**: 水分子单点能计算，使用 PBE0 泛函和 cc-pVDZ 基组
- **任务类型**: energy

### 2. 水分子几何优化 (B3LYP)

- **YAML**: `h2o_optimize_b3lyp.yaml`
- **BDF**: `h2o_optimize_b3lyp.inp`
- **描述**: 水分子几何优化，使用 B3LYP 泛函和 6-31G* 基组
- **任务类型**: optimize

### 3. 水分子频率计算 (PBE0)

- **YAML**: `h2o_frequency_pbe0.yaml`
- **BDF**: `h2o_frequency_pbe0.inp`
- **描述**: 水分子频率计算，使用 PBE0 泛函和 cc-pVDZ 基组
- **任务类型**: frequency
- **⚠️ 警告**: 频率计算通常应在优化后的几何结构上进行

### 4. 水分子 TDDFT 激发态计算 (PBE0)

- **YAML**: `h2o_tddft_pbe0.yaml`
- **BDF**: `h2o_tddft_pbe0.inp`
- **描述**: 水分子 TDDFT 激发态计算，计算 10 个单重态激发态
- **任务类型**: tddft

### 5. 甲醛分子单点能计算 (HF)

- **YAML**: `ch2o_energy_hf.yaml`
- **BDF**: `ch2o_energy_hf.inp`
- **描述**: 甲醛分子单点能计算，使用 Hartree-Fock 方法和 6-31G* 基组
- **任务类型**: energy
- **方法类型**: hf

### 6. 苯分子几何优化 (PBE0)

- **YAML**: `c6h6_optimize_pbe0.yaml`
- **BDF**: `c6h6_optimize_pbe0.inp`
- **描述**: 苯分子几何优化，使用 PBE0 泛函和 cc-pVDZ 基组
- **任务类型**: optimize
- **分子**: 12 个原子（6 个 C，6 个 H）

## 🔍 审查要点

### YAML 文件审查

1. **结构完整性**
   - 检查 task, molecule, method, settings 块是否完整
   - 检查必需字段是否存在

2. **数据正确性**
   - 坐标格式是否正确
   - 电荷和自旋多重度是否合理
   - 方法和基组是否正确

3. **Schema 兼容性**
   - 是否符合 bdfeasyinput_schema 规范
   - 字段类型是否正确

### BDF 输入文件审查

1. **模块顺序**
   - COMPASS → XUANYUAN → SCF (单点能)
   - COMPASS → BDFOPT → XUANYUAN → SCF → RESP (优化)
   - COMPASS → BDFOPT → XUANYUAN → SCF → RESP (频率)
   - COMPASS → XUANYUAN → SCF → TDDFT (激发态)

2. **关键词正确性**
   - 泛函名称是否正确
   - 基组名称是否正确
   - 其他关键词是否正确

3. **坐标格式**
   - 坐标是否正确转换
   - 单位是否正确

## 📊 测试统计

- **总测试数**: 6
- **成功**: 6
- **失败**: 0
- **警告**: 1 (频率计算建议使用优化后的几何结构)

## 🎯 验证项目

- ✅ Schema 验证通过
- ✅ YAML 生成正常
- ✅ BDF 转换正常
- ✅ 所有任务类型支持
- ✅ 多种方法类型支持 (HF, DFT)
- ✅ 多种泛函支持 (PBE0, B3LYP)

## 📝 使用说明

### 查看文件

```bash
# 查看 YAML 文件
cat test_outputs/schema_integration/h2o_energy_pbe0.yaml

# 查看 BDF 文件
cat test_outputs/schema_integration/h2o_energy_pbe0.inp
```

### 重新生成

```bash
cd /Users/bsuo/bdf
source venv_bdf/bin/activate
python BDFEasyInput/tests/test_schema_integration_generation.py
```

## ✅ 审查清单

- [ ] YAML 文件格式正确
- [ ] BDF 文件格式正确
- [ ] 模块顺序正确
- [ ] 关键词正确
- [ ] 坐标正确
- [ ] 方法设置正确
- [ ] 基组设置正确
- [ ] 任务类型正确

---

**生成脚本**: `tests/test_schema_integration_generation.py`  
**输出目录**: `test_outputs/schema_integration/`
