# BDFEasyInput 统一提取接口文档

## 概述

`extraction` 模块提供了统一的接口，用于从 BDF 计算输出中提取结构化的指标数据。该接口设计用于与 BDFAgent 等外部工具集成。

## 快速开始

### 命令行使用

```bash
# 提取指标并输出到控制台
python -m bdfeasyinput.cli extract output.log

# 提取指标并保存到 JSON 文件
python -m bdfeasyinput.cli extract output.log -o metrics.json

# 指定任务类型（可选，默认自动检测）
python -m bdfeasyinput.cli extract output.log --task-type optimize
```

### Python API 使用

```python
from bdfeasyinput.extraction import BDFResultExtractor

# 创建提取器
extractor = BDFResultExtractor()

# 提取指标（自动检测任务类型）
metrics = extractor.extract_metrics("output.log")

# 访问指标
print(f"任务类型: {metrics.task_type}")
if metrics.geometry:
    print(f"总能量: {metrics.geometry.final_energy}")
    print(f"优化收敛: {metrics.geometry.optimization_converged}")

# 转换为字典（用于序列化）
result_dict = metrics.to_dict()
```

## 支持的任务类型

- `single_point`: 单点能计算
- `optimize`: 几何优化
- `frequency`: 频率分析
- `optimize_frequency`: 几何优化 + 频率分析
- `excited`: 激发态计算（TDDFT）

## 指标数据结构

### CalculationMetrics

顶层容器，包含所有指标：

```python
@dataclass
class CalculationMetrics:
    task_type: str
    geometry: Optional[GeometryMetrics] = None
    frequency: Optional[FrequencyMetrics] = None
    excited: Optional[ExcitedStateMetrics] = None
```

### GeometryMetrics

几何优化相关指标：

```python
@dataclass
class GeometryMetrics:
    max_force: Optional[float]           # 最大力
    rms_force: Optional[float]          # RMS 力
    final_energy: Optional[float]       # 最终能量
    scf_converged: Optional[bool]       # SCF 是否收敛
    optimization_converged: Optional[bool]  # 优化是否收敛
    n_iterations: Optional[int]         # 迭代次数
    final_geometry: Optional[List[Dict]]  # 最终几何结构
```

### FrequencyMetrics

频率分析相关指标：

```python
@dataclass
class FrequencyMetrics:
    min_freq: Optional[float]           # 最小频率
    max_freq: Optional[float]           # 最大频率
    imaginary_count: Optional[int]       # 虚频数量
    frequencies: List[float]            # 所有频率
    vibrations: List[float]             # 振动频率
    translations_rotations: List[float]  # 平动/转动频率
```

### ExcitedStateMetrics

激发态计算相关指标：

```python
@dataclass
class ExcitedStateMetrics:
    n_states_converged: Optional[int]   # 收敛的激发态数量
    states: List[Dict]                  # 激发态详细信息
    energies: List[float]               # 激发态能量 (eV)
    oscillator_strengths: List[float]    # 振子强度
    wavelengths: List[float]            # 波长 (nm)
```

## 使用示例

### 示例 1: 单点能计算

```python
from bdfeasyinput.extraction import BDFResultExtractor

extractor = BDFResultExtractor()
metrics = extractor.extract_metrics("h2o_sp.log")

print(f"任务类型: {metrics.task_type}")  # single_point
print(f"总能量: {metrics.geometry.final_energy}")
print(f"SCF 收敛: {metrics.geometry.scf_converged}")
```

### 示例 2: 几何优化

```python
metrics = extractor.extract_metrics("molecule_opt.log")

if metrics.geometry:
    print(f"优化收敛: {metrics.geometry.optimization_converged}")
    print(f"迭代次数: {metrics.geometry.n_iterations}")
    print(f"最大力: {metrics.geometry.max_force}")
    print(f"RMS 力: {metrics.geometry.rms_force}")
```

### 示例 3: 频率分析

```python
metrics = extractor.extract_metrics("molecule_freq.log")

if metrics.frequency:
    print(f"频率数量: {len(metrics.frequency.frequencies)}")
    print(f"虚频数量: {metrics.frequency.imaginary_count}")
    print(f"最小频率: {metrics.frequency.min_freq}")
    print(f"最大频率: {metrics.frequency.max_freq}")
```

### 示例 4: 激发态计算

```python
metrics = extractor.extract_metrics("molecule_tddft.log")

if metrics.excited:
    print(f"激发态数量: {metrics.excited.n_states_converged}")
    for i, energy in enumerate(metrics.excited.energies, 1):
        print(f"状态 {i}: {energy} eV")
```

### 示例 5: 序列化为 JSON

```python
import json

metrics = extractor.extract_metrics("output.log")
result_dict = metrics.to_dict()

# 保存到文件
with open("metrics.json", "w") as f:
    json.dump(result_dict, f, indent=2)

# 或直接使用 JSON 字符串
json_str = json.dumps(result_dict, indent=2)
```

## 任务类型自动检测

如果不指定 `task_type`，系统会自动检测：

1. 检查是否有优化步骤 → `optimize` 或 `optimize_frequency`
2. 检查是否有频率数据 → `frequency` 或 `optimize_frequency`
3. 检查是否有 TDDFT 数据 → `excited`
4. 否则 → `single_point`

## 错误处理

```python
from bdfeasyinput.extraction import BDFResultExtractor

extractor = BDFResultExtractor()

try:
    metrics = extractor.extract_metrics("output.log")
except FileNotFoundError:
    print("输出文件不存在")
except ValueError as e:
    print(f"解析失败: {e}")
```

## 与 BDFAgent 集成

BDFAgent 可以使用此接口提取指标：

```python
from bdfeasyinput.extraction import BDFResultExtractor

extractor = BDFResultExtractor()
metrics = extractor.extract_metrics("bdf_output.log")

# 转换为字典供 BDFAgent 使用
metrics_dict = metrics.to_dict()
```

## 注意事项

1. **数据缺失**: 某些指标可能为 `None`（如果计算中未包含相应内容）
2. **任务类型**: 对于激发态优化，`task_type` 可能为 `optimize`，但会同时提取 `excited` 信息
3. **文件路径**: 输入文件路径可以是相对路径或绝对路径
4. **向后兼容**: 接口设计考虑了 `BDFOutputParser` 的向后兼容性

## 相关文档

- `BDFAgent/docs/BDFEASYINPUT_IMPLEMENTATION_CHECKLIST.md` - 实施检查清单
- `bdfeasyinput/analysis/parser/output_parser.py` - 底层解析器
