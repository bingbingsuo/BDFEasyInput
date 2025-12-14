# 分子轨道占据信息解析功能总结

## 功能概述

已成功实现BDF输出文件中SCF计算分子轨道占据信息的解析和显示功能。

## 实现内容

### 1. 解析器增强 (`output_parser.py`)

添加了 `extract_occupation_info()` 方法，可以提取以下信息：

- **不可约表示列表** (`irreps`): 从 "Irreps: Ag B1g B2g ..." 提取
- **Alpha轨道占据数** (`alpha_occupation`): 从 "Alpha 6.00 3.00 ..." 提取
- **Beta轨道占据数** (`beta_occupation`): 从 "Beta 6.00 3.00 ..." 提取，或对于RHF/RKS计算自动等于Alpha占据数
- **Alpha电子总数** (`total_alpha_electrons`): 自动计算
- **Beta电子总数** (`total_beta_electrons`): 自动计算
- **总电子数** (`total_electrons`): 自动计算
- **是否为RHF/RKS** (`is_rhf_rks`): 自动判断（当只有Alpha输出时）
- **基态波函数对称性** (`ground_state_irrep`): 第一个不可约表示（全对称表示）

### 2. 支持的输出格式

解析器可以识别以下BDF输出格式：

```
[Final occupation pattern: ]

 Irreps:        Ag      B1g     B2g     B3g     Au      B1u     B2u     B3u 

 detailed occupation for iden/irep:      1   1
    1.00 1.00 1.00 1.00 1.00 1.00 0.00 0.00 0.00 0.00
    ...
 detailed occupation for iden/irep:      1   2
    ...
 Alpha       6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00
```

### 3. 报告生成器增强 (`report_generator.py`)

在报告生成器中添加了轨道占据信息的显示部分，包括：

- Alpha/Beta电子总数
- 总电子数
- 基态波函数对称性
- 轨道占据分布表（表格格式，显示每个不可约表示的占据数）
- 相关说明信息

### 4. 报告标签增强 (`report_labels.py`)

添加了中英文轨道占据相关的标签：

- `orbital_occupation_info`: 分子轨道占据信息
- `alpha_occupation`: Alpha轨道占据数
- `beta_occupation`: Beta轨道占据数
- `total_alpha_electrons`: Alpha电子总数
- `total_beta_electrons`: Beta电子总数
- `total_electrons`: 总电子数
- `ground_state_irrep`: 基态波函数对称性
- `occupation_table`: 轨道占据分布表
- 等等...

## 测试结果

### 单元测试

已创建测试脚本 `test_occupation_parser.py`，验证解析器功能：

```bash
python test_occupation_parser.py
```

测试结果：
- ✓ 成功提取不可约表示列表（8个：Ag, B1g, B2g, B3g, Au, B1u, B2u, B3u）
- ✓ 成功提取Alpha轨道占据数（8个值：6.00, 3.00, 1.00, 1.00, 0.00, 1.00, 4.00, 5.00）
- ✓ 自动识别RHF/RKS计算（Beta占据数等于Alpha占据数）
- ✓ 正确计算总电子数（42.00）
- ✓ 正确识别基态波函数对称性（Ag，第一个不可约表示）
- ✓ 成功生成分析报告

## 使用示例

### 解析输出文件

```python
from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

parser = BDFOutputParser()
result = parser.parse("output.log")

# 访问轨道占据信息
occupation = result.get('properties', {}).get('occupation')
if occupation:
    print(f"不可约表示: {occupation.get('irreps', [])}")
    print(f"Alpha占据数: {occupation.get('alpha_occupation', [])}")
    print(f"总电子数: {occupation.get('total_electrons', 'N/A')}")
    print(f"基态波函数对称性: {occupation.get('ground_state_irrep', 'N/A')}")
```

### 生成报告

轨道占据信息会自动包含在分析报告中，位于"原始数据"部分的"分子轨道占据信息"小节。

## 技术细节

### 解析逻辑

1. **查找占据模式部分**：
   - 匹配 `[Final occupation pattern: ]` 标记
   - 提取后续5000字符作为相关区域

2. **提取不可约表示**：
   - 匹配 `Irreps: Ag B1g ...` 行
   - 使用正则表达式提取不可约表示标记
   - 过滤掉常见英文单词（如"for", "iden", "irep"）
   - 只保留长度1-5字符的标记

3. **提取占据数**：
   - 匹配 `Alpha 6.00 3.00 ...` 行
   - 提取所有浮点数作为Alpha占据数
   - 如果存在 `Beta` 行，提取Beta占据数
   - 如果只有Alpha，自动设置Beta=Alpha（RHF/RKS计算）

4. **计算总电子数**：
   - Alpha电子总数 = sum(alpha_occupation)
   - Beta电子总数 = sum(beta_occupation)
   - 总电子数 = Alpha总数 + Beta总数

5. **基态波函数对称性**：
   - 对于闭壳层电子态，基态波函数的对称性总是第一个不可约表示
   - 第一个不可约表示通常是全对称表示（如Ag, A1, A等）

### 验证

- 验证不可约表示数量与占据数数量是否一致
- 如果不一致，记录警告但不失败

### 注意事项

1. **RHF/RKS计算**：
   - 对于RHF/RKS计算，BDF只输出Alpha轨道占据数
   - 解析器自动设置Beta占据数等于Alpha占据数
   - 标记 `is_rhf_rks = True`

2. **开壳层计算**：
   - 对于开壳层计算（UKS等），BDF会分别输出Alpha和Beta占据数
   - 解析器会分别提取两者

3. **基态对称性**：
   - 对于闭壳层电子态，基态波函数的对称性总是第一个不可约表示（全对称表示）
   - 这是群论的基本结果

## 相关文件

- `bdfeasyinput/analysis/parser/output_parser.py`: 解析器实现（`extract_occupation_info`方法）
- `bdfeasyinput/analysis/report/report_generator.py`: 报告生成器（轨道占据信息显示部分）
- `bdfeasyinput/analysis/report/report_labels.py`: 报告标签
- `test_occupation_parser.py`: 单元测试脚本
- `docs/dev/occupation_test_report.md`: 生成的测试报告

## 后续改进建议

1. **详细占据信息**: 提取 `detailed occupation for iden/irep` 部分的详细占据模式
2. **轨道能量关联**: 将占据信息与轨道能量信息关联
3. **占据数验证**: 验证占据数总和是否等于总电子数
4. **开壳层支持**: 增强对开壳层计算的支持和显示
