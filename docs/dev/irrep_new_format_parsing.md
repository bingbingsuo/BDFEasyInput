# 不可约表示新格式解析功能总结

## 功能概述

已成功更新BDF输出文件中不可约表示信息的解析功能，支持新的输出格式。

## 新格式说明

BDF在compass输出中使用新的格式，三行信息在一起：

```
         Symmetry adapted orbital                   

  Total number of basis functions:     114     114

  Number of irreps:   8
  Irrep :   Ag        B1g       B2g       B3g       Au        B1u       B2u       B3u     
  Norb  :     24        18         9         6         6         9        18        24
```

### 格式特点

1. **第一行**: `Number of irreps:   8` - 给出不可约表示数目
2. **第二行**: `Irrep :   Ag        B1g       B2g       ...` - 所有不可约表示标记在同一行
3. **第三行**: `Norb  :     24        18         9         ...` - 所有轨道数在同一行

### 与旧格式的区别

**旧格式**（每个不可约表示单独列出）：
```
  Irrep :     A
  Norb  :     22
  Irrep :     B1
  Norb  :     10
```

**新格式**（所有信息集中在一起）：
```
  Number of irreps:   8
  Irrep :   Ag        B1g       B2g       B3g       Au        B1u       B2u       B3u     
  Norb  :     24        18         9         6         6         9        18        24
```

## 实现内容

### 1. 解析器增强 (`output_parser.py`)

更新了 `extract_irrep_info()` 方法，支持新格式：

- **提取不可约表示数目**: 从 "Number of irreps: 8" 提取
- **提取不可约表示标记**: 从 "Irrep : Ag B1g ..." 行提取所有标记
- **提取轨道数**: 从 "Norb : 24 18 ..." 行提取所有数字
- **匹配验证**: 确保不可约表示数量与轨道数数量一致
- **向后兼容**: 如果新格式没找到，自动尝试旧格式

### 2. 报告生成器增强 (`report_generator.py`)

在报告中添加了不可约表示数目的显示：

- 显示不可约表示数目（如果可用）
- 显示总基函数数
- 显示总轨道数
- 显示不可约表示分布表

### 3. 报告标签增强 (`report_labels.py`)

添加了中英文不可约表示数目相关的标签：

- `number_of_irreps`: 不可约表示数目

## 测试结果

### 单元测试

已创建测试脚本 `test_irrep_new_format.py`，验证解析器功能：

```bash
python test_irrep_new_format.py
```

测试结果：
- ✓ 成功提取不可约表示数目（8）
- ✓ 成功提取所有8个不可约表示标记
- ✓ 成功提取所有8个轨道数
- ✓ 正确匹配不可约表示和轨道数
- ✓ 所有验证通过

### c6h6.out 测试

**输出文件**: `debug/c6h6.out`

**解析结果**:
- ✓ 总基函数数: 114
- ✓ 不可约表示数目: 8
- ✓ 总轨道数: 114
- ✓ 所有8个不可约表示都正确提取：
  - Ag: 24 个轨道
  - B1g: 18 个轨道
  - B2g: 9 个轨道
  - B3g: 6 个轨道
  - Au: 6 个轨道
  - B1u: 9 个轨道
  - B2u: 18 个轨道
  - B3u: 24 个轨道

## 解析逻辑

### 新格式解析流程

1. **提取不可约表示数目**:
   ```python
   Number of irreps:   8
   ```

2. **查找 "Irrep :" 行**:
   - 使用正则表达式提取所有不可约表示标记
   - 过滤掉常见英文单词（for, iden, irep, norb等）
   - 只保留长度1-5字符的标记

3. **查找下一行的 "Norb :" 行**:
   - 提取所有数字作为轨道数
   - 验证数量是否与不可约表示数量一致

4. **匹配和存储**:
   - 将不可约表示标记和轨道数一一对应
   - 存储到irreps列表中

### 向后兼容

如果新格式没找到，自动尝试旧格式：
- 查找每个 "Irrep : A" 和对应的 "Norb : 22"
- 逐个提取和匹配

## 使用示例

### 解析输出文件

```python
from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

parser = BDFOutputParser()
result = parser.parse("output.log")

# 访问不可约表示信息
irreps = result.get('properties', {}).get('irreps')
if irreps:
    print(f"不可约表示数目: {irreps.get('number_of_irreps')}")
    print(f"总基函数数: {irreps.get('total_basis_functions')}")
    print(f"总轨道数: {irreps.get('total_orbitals')}")
    for irrep_data in irreps.get('irreps', []):
        print(f"{irrep_data.get('irrep')}: {irrep_data.get('norb')} 个轨道")
```

### 生成报告

不可约表示信息会自动包含在分析报告中，包括：
- 不可约表示数目
- 总基函数数
- 总轨道数
- 不可约表示分布表

## 相关文件

- `bdfeasyinput/analysis/parser/output_parser.py`: 解析器实现（`extract_irrep_info`方法）
- `bdfeasyinput/analysis/report/report_generator.py`: 报告生成器（不可约表示显示部分）
- `bdfeasyinput/analysis/report/report_labels.py`: 报告标签
- `test_irrep_new_format.py`: 新格式测试脚本
- `docs/dev/c6h6_out_final_report.md`: 生成的完整报告

## 验证结果

从c6h6.out的解析结果验证：
- ✓ 不可约表示数目: 8（正确）
- ✓ 总基函数数: 114（正确）
- ✓ 总轨道数: 114（正确，等于所有不可约表示轨道数之和：24+18+9+6+6+9+18+24=114）
- ✓ 所有8个不可约表示都正确提取和匹配

## 后续改进建议

1. **格式检测**: 自动检测使用的是新格式还是旧格式
2. **错误处理**: 如果不可约表示数量与轨道数数量不一致，提供更详细的错误信息
3. **验证**: 验证总轨道数是否等于总基函数数（对于闭壳层系统）
