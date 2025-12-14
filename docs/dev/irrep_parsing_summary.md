# 不可约表示（Irrep）解析功能总结

## 功能概述

已成功实现BDF输出文件中不可约表示（Irreducible Representation）信息的解析和显示功能。

## 实现内容

### 1. 解析器增强 (`output_parser.py`)

添加了 `extract_irrep_info()` 方法，可以提取以下信息：

- **总基函数数目** (`total_basis_functions`): 从 "Total number of basis functions: 22 22" 提取
- **不可约表示列表** (`irreps`): 每个不可约表示包含：
  - `irrep`: 不可约表示标记（如 A, A1, B1, E1G等）
  - `norb`: 该不可约表示的分子轨道数目
- **总分子轨道数** (`total_orbitals`): 所有不可约表示的轨道数之和

### 2. 支持的输出格式

解析器可以识别以下BDF输出格式：

#### 格式1：行格式（标准格式）
```
Total number of basis functions:      22      22

  Irrep :     A
  Norb  :     22
```

#### 格式2：多个不可约表示
```
Total number of basis functions:      108     108

  Irrep :     A1G
  Norb  :     18
  Irrep :     A2G
  Norb  :     12
  Irrep :     E1G
  Norb  :     24
```

#### 格式3：表格格式
```
Total number of basis functions:      30      30

  Irrep    Norb
    A       15
    B1      10
    B2       5
```

### 3. 报告生成器增强 (`report_generator.py`)

在报告生成器中添加了不可约表示信息的显示部分，包括：

- 总基函数数目
- 总分子轨道数
- 不可约表示分布表（表格格式）
- 相关说明信息

### 4. 报告标签增强 (`report_labels.py`)

添加了中英文不可约表示相关的标签：

- `irrep_info`: 不可约表示信息
- `total_basis_functions`: 总基函数数目
- `total_orbitals`: 总分子轨道数
- `irrep`: 不可约表示
- `orbitals_per_irrep`: 每个不可约表示的轨道数
- `irrep_table`: 不可约表示分布表
- 等等...

## 测试结果

### 单元测试

已创建测试脚本 `test_irrep_parser.py`，验证解析器功能：

```bash
python test_irrep_parser.py
```

测试结果：
- ✓ 成功提取单个不可约表示
- ✓ 成功提取多个不可约表示
- ✓ 支持表格格式
- ✓ 正确计算总轨道数

### test006.inp 测试

已创建测试脚本 `test_test006_irrep.py`，使用模拟输出测试：

```bash
python test_test006_irrep.py
```

测试结果：
- ✓ 成功提取对称群信息
- ✓ 成功提取不可约表示信息
- ✓ 正确计算总基函数数和总轨道数
- ✓ 成功生成分析报告

## 使用示例

### 解析输出文件

```python
from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

parser = BDFOutputParser()
result = parser.parse("output.log")

# 访问不可约表示信息
irreps = result.get('properties', {}).get('irreps')
if irreps:
    print(f"总基函数数: {irreps.get('total_basis_functions')}")
    print(f"总轨道数: {irreps.get('total_orbitals')}")
    for irrep_data in irreps.get('irreps', []):
        print(f"{irrep_data.get('irrep')}: {irrep_data.get('norb')} 个轨道")
```

### 生成报告

不可约表示信息会自动包含在分析报告中，位于"原始数据"部分的"不可约表示信息"小节。

## test006.inp 分析

test006.inp 包含多个C6H6分子的SCF能量计算，使用不同的对称群：

1. **自动检测对称群**（无Group关键词）
2. **D(6H)** - 完整对称群
3. **D(3H)** - 子群
4. **C(6V)** - 子群
5. **D(3D)** - 子群
6. **D(2H)** - 子群
7. **C(2V)** - 子群（两次，一次带SAORB）
8. **C(1)** - 最低对称群

每个计算任务都会输出：
- 对称群信息（检测到的群、用户设定的群）
- 不可约表示信息（总基函数数、各不可约表示的轨道数）

## 技术细节

### 解析逻辑

1. **总基函数数提取**：
   - 匹配 "Total number of basis functions: X Y" 格式
   - 支持开壳层计算（两个数字：alpha和beta）

2. **不可约表示提取**：
   - 支持行格式：`Irrep : A` 和 `Norb : 22` 分开两行
   - 支持表格格式：`Irrep Norb` 表头后跟数据行
   - 自动去重，避免重复提取

3. **总轨道数计算**：
   - 自动计算所有不可约表示的轨道数之和
   - 验证：总轨道数应该等于总基函数数（对于闭壳层）

### 注意事项

1. **多个计算任务**：
   - test006.inp包含多个计算任务，输出文件会包含多个计算的结果
   - 当前解析器会提取所有找到的不可约表示信息
   - 如果需要分别处理每个计算任务，需要按计算任务分割输出文件

2. **不可约表示标记**：
   - 不同对称群使用不同的不可约表示标记
   - D(6H)使用：A1G, A2G, E1G, E2G, A1U, A2U, E1U, E2U等
   - D(3H)使用：A1', A2', E', A1'', A2'', E''等
   - C(2V)使用：A1, A2, B1, B2等

## 相关文件

- `bdfeasyinput/analysis/parser/output_parser.py`: 解析器实现（`extract_irrep_info`方法）
- `bdfeasyinput/analysis/report/report_generator.py`: 报告生成器（不可约表示显示部分）
- `bdfeasyinput/analysis/report/report_labels.py`: 报告标签
- `test_irrep_parser.py`: 单元测试脚本
- `test_test006_irrep.py`: test006测试脚本
- `docs/dev/test006_irrep_test_report.md`: 生成的测试报告

## 后续改进建议

1. **多计算任务支持**: 改进解析器以支持分别处理多个计算任务的结果
2. **不可约表示验证**: 验证总轨道数是否等于总基函数数
3. **对称群与不可约表示关联**: 将不可约表示信息与对应的对称群信息关联
4. **轨道能量提取**: 提取每个不可约表示的轨道能量信息（如果有）
