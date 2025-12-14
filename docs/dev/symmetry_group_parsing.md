# 对称群信息解析功能

## 功能概述

已成功增强BDF的计算结果解析功能，添加了对称群信息的提取和显示。

## 实现内容

### 1. 解析器增强 (`output_parser.py`)

添加了 `extract_symmetry_info()` 方法，可以提取以下对称群信息：

- **BDF自动检测的对称群** (`detected_group`): 从 "Point group name D(6H)" 提取
- **用户设定的对称群** (`user_set_group`): 从 "User set point group as D(6H)" 提取
- **最大阿贝尔子群** (`largest_abelian_subgroup`): 从 "Largest Abelian Subgroup D(2H)" 提取
- **对称操作数** (`noper`): 从 "gsym: D06H, noper= 24" 提取
- **阿贝尔子群操作数** (`abelian_subgroup_noper`): 从最大阿贝尔子群信息中提取
- **对称性检查结果** (`symmetry_check`): 从 "Symmetry check OK" 提取
- **子群判断** (`is_subgroup`): 判断用户设定的群是否是检测到的群的子群

### 2. 报告生成器增强 (`report_generator.py`)

在报告生成器中添加了对称群信息的显示部分，包括：

- BDF自动检测的点群
- 用户设定的点群（如果有）
- 最大阿贝尔子群
- 对称操作数
- 对称性检查结果
- 相关说明信息

### 3. 报告标签增强 (`report_labels.py`)

添加了中英文对称群相关的标签：

- `symmetry_group_info`: 对称群信息
- `detected_point_group`: BDF自动检测的点群
- `user_set_point_group`: 用户设定的点群
- `largest_abelian_subgroup`: 最大阿贝尔子群
- `number_of_operations`: 对称操作数
- 等等...

## 支持的输出格式

解析器可以识别以下BDF输出格式：

```
gsym: D06H, noper=   24
 Exiting zgeomsort....
 Representation generated
  Point group name D(6H)   
  User set point group as D(6H)   
  Largest Abelian Subgroup D(2H)                       8
 Representation generated
 D|6|H|                    6
 Symmetry check OK
```

## 测试

### 单元测试

已创建测试脚本 `test_symmetry_parser.py`，验证解析器功能：

```bash
python test_symmetry_parser.py
```

测试结果：
- ✓ 成功提取所有对称群信息
- ✓ 支持多种格式的点群名称（D06H → D(6H)）
- ✓ 正确判断子群关系

### 测试用例

1. **标准格式**: 包含所有对称群信息
2. **只有检测到的群**: 仅包含BDF自动检测的对称群
3. **用户设定子群**: 用户指定了检测到的群的子群

## 使用示例

### 解析输出文件

```python
from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

parser = BDFOutputParser()
result = parser.parse("output.log")

# 访问对称群信息
symmetry = result.get('properties', {}).get('symmetry')
if symmetry:
    print(f"检测到的对称群: {symmetry.get('detected_group')}")
    print(f"用户设定的对称群: {symmetry.get('user_set_group')}")
    print(f"对称操作数: {symmetry.get('noper')}")
```

### 生成报告

对称群信息会自动包含在分析报告中，位于"原始数据"部分的"对称群信息"小节。

## C6H6测试算例

已创建C6H6（苯）分子的测试算例，包含多个不同对称群的SCF能量计算：

- `test_c6h6_Auto.inp`: 使用BDF自动检测的对称群
- `test_c6h6_D6H.inp`: 使用D(6H)对称群
- `test_c6h6_D2H.inp`: 使用D(2H)子群
- `test_c6h6_C2V.inp`: 使用C(2V)子群

### 运行测试算例

```bash
# 生成测试输入文件
python test_c6h6_symmetry.py

# 运行BDF计算（需要BDF程序）
bdf test_c6h6_D6H.inp > test_c6h6_D6H.out

# 解析和分析
python -m bdfeasyinput.cli analyze test_c6h6_D6H.out
```

## 技术细节

### 点群格式转换

解析器会自动将BDF输出的点群格式转换为标准格式：
- `D06H` → `D(6H)`
- `C2V` → `C(2V)`
- `D2H` → `D(2H)`

### 子群判断

实现了简化的子群判断逻辑：
- 相同群：肯定是子群
- 相同前缀和数字：可能是子群
- 数字是因子关系：可能是子群（如D(2)是D(6)的子群）

注意：完整的子群判断需要群论知识，这里只做基本检查。BDF会在计算时验证子群关系。

## 后续改进建议

1. **更精确的子群判断**: 实现完整的群论子群判断算法
2. **对称操作详情**: 提取具体的对称操作列表
3. **不可约表示**: 提取不可约表示信息（用于TDDFT等计算）
4. **对称性降低**: 记录对称性降低的原因（如果有）

## 相关文件

- `bdfeasyinput/analysis/parser/output_parser.py`: 解析器实现
- `bdfeasyinput/analysis/report/report_generator.py`: 报告生成器
- `bdfeasyinput/analysis/report/report_labels.py`: 报告标签
- `test_symmetry_parser.py`: 单元测试脚本
- `test_c6h6_symmetry.py`: C6H6测试算例生成脚本
