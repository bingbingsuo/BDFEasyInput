# 数据标准化使用示例

## 1. 基本使用

### 1.1 自动标准化

在分析结果时，自动生成标准化数据：

```python
from bdfeasyinput.analysis import QuantumChemistryAnalyzer
from bdfeasyinput.analysis.standardizer import AnalysisStandardizer

# 执行分析
analyzer = QuantumChemistryAnalyzer(ai_client)
analysis_result = analyzer.analyze("output.out", "input.inp")

# 自动标准化
standardizer = AnalysisStandardizer()
standardized = standardizer.standardize(
    input_data=input_data,
    execution_result=execution_result,
    raw_results=raw_results,
    analysis_result=analysis_result,
    ai_metadata={"provider": "ollama", "model": "llama3"}
)

# 保存标准化数据
standardizer.export_json(standardized, "results/standardized/calc_001.json")
```

### 1.2 命令行使用

```bash
# 分析并自动标准化
bdfeasyinput analyze output.out \
  --input input.inp \
  --standardize \
  --output-dir ./standardized_data

# 只标准化已有结果
bdfeasyinput standardize analysis_result.json -o standardized.json
```

## 2. 训练数据准备

### 2.1 准备任务规划训练数据

```python
from bdfeasyinput.analysis.standardizer import (
    AnalysisStandardizer,
    prepare_planning_training_data
)

# 加载多个标准化数据
import json
from pathlib import Path

data_list = []
for file in Path("results/standardized").glob("*.json"):
    with open(file) as f:
        data_list.append(json.load(f))

# 准备训练数据
training_data = prepare_planning_training_data(data_list)

# 导出为 JSONL 格式
standardizer = AnalysisStandardizer()
standardizer.export_training_data(
    training_data,
    "data/training/planning_data.jsonl",
    format="jsonl"
)
```

### 2.2 准备结果分析训练数据

```python
from bdfeasyinput.analysis.standardizer import (
    prepare_analysis_training_data
)

# 准备分析训练数据
training_data = prepare_analysis_training_data(data_list)

# 导出
standardizer.export_training_data(
    training_data,
    "data/training/analysis_data.jsonl",
    format="jsonl"
)
```

## 3. 批量处理

### 3.1 批量标准化

```python
from bdfeasyinput.analysis.standardizer import AnalysisStandardizer
from pathlib import Path

standardizer = AnalysisStandardizer()

# 批量处理
for result_dir in Path("results").iterdir():
    if result_dir.is_dir():
        # 加载结果
        input_data = load_yaml(result_dir / "input.yaml")
        execution_result = load_execution_result(result_dir)
        raw_results = parse_output(result_dir / "output.out")
        analysis_result = load_analysis(result_dir / "analysis.json")
        
        # 标准化
        standardized = standardizer.standardize(
            input_data=input_data,
            execution_result=execution_result,
            raw_results=raw_results,
            analysis_result=analysis_result
        )
        
        # 保存
        output_path = f"data/standardized/{standardized['metadata']['calculation_id']}.json"
        standardizer.export_json(standardized, output_path)
```

## 4. 数据验证

### 4.1 验证标准化数据

```python
from bdfeasyinput.analysis.standardizer import AnalysisStandardizer

standardizer = AnalysisStandardizer(schema_path="schemas/analysis_result_schema.json")

# 加载数据
with open("standardized_data.json") as f:
    data = json.load(f)

# 验证
try:
    standardizer.validate(data)
    print("数据验证通过")
except ValidationError as e:
    print(f"数据验证失败: {e}")
```

## 5. 数据查询和统计

### 5.1 查询标准化数据

```python
from bdfeasyinput.analysis.standardizer import DataManager

manager = DataManager("data/standardized")

# 查询特定任务类型
energy_calculations = manager.query(
    task_type="energy",
    method="pbe0"
)

# 统计信息
stats = manager.get_statistics()
print(f"总计算数: {stats['total_records']}")
print(f"任务类型分布: {stats['task_types']}")
```

## 6. 训练数据格式示例

### 6.1 任务规划训练数据（JSONL）

```jsonl
{"input": "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组", "output": {"task": {"type": "energy"}, "molecule": {"formula": "H2O", "charge": 0, "multiplicity": 1, "coordinates": [{"atom": "O", "x": 0.0, "y": 0.0, "z": 0.1173}, {"atom": "H", "x": 0.0, "y": 0.7572, "z": -0.4692}, {"atom": "H", "x": 0.0, "y": -0.7572, "z": -0.4692}], "units": "angstrom"}, "method": {"type": "dft", "functional": "pbe0", "basis": "cc-pvdz"}}}
{"input": "优化苯分子的几何结构", "output": {"task": {"type": "optimize"}, "molecule": {"formula": "C6H6", "charge": 0, "multiplicity": 1, "coordinates": [...]}, "method": {"type": "dft", "functional": "b3lyp", "basis": "6-31g*"}}}
```

### 6.2 结果分析训练数据（JSONL）

```jsonl
{"input": {"raw_results": {"energy": {"total_energy": -76.4123, "unit": "hartree"}, "convergence": {"scf_converged": true, "scf_iterations": 12}}, "task_type": "energy", "method": {"type": "dft", "functional": "pbe0", "basis": "cc-pvdz"}}, "output": {"analysis": {"summary": {"calculation_successful": true, "quality_assessment": "good"}, "energy_analysis": {"total_energy": -76.4123, "energy_assessment": "合理", "expert_comment": "总能量为负值，符合预期。"}}, "recommendations": {"calculation_quality": "good", "further_calculations": []}}}
```

## 7. 数据管理

### 7.1 数据索引

```python
from bdfeasyinput.analysis.standardizer import DataIndexer

indexer = DataIndexer("data/standardized")

# 创建索引
indexer.create_index()

# 查询
results = indexer.search(
    molecule="H2O",
    method="pbe0",
    date_range=("2024-01-01", "2024-12-31")
)
```

### 7.2 数据统计

```python
# 获取统计信息
stats = indexer.get_statistics()

print(f"总记录数: {stats['total_records']}")
print(f"任务类型分布:")
for task_type, count in stats['task_types'].items():
    print(f"  {task_type}: {count}")
print(f"方法分布:")
for method, count in stats['methods'].items():
    print(f"  {method}: {count}")
```

## 8. 集成到工作流

### 8.1 完整工作流（包含标准化）

```python
from bdfeasyinput import BDFEasyInputWorkflow
from bdfeasyinput.analysis.standardizer import AnalysisStandardizer

workflow = BDFEasyInputWorkflow(
    ai_client=client,
    bdfautotest_path="/path/to/bdfautotest"
)

# 运行完整工作流
results = workflow.run_complete_workflow(
    "计算水分子的单点能",
    run_calculation=True,
    analyze_results=True,
    standardize=True  # 自动标准化
)

# 标准化数据已保存在 results['standardized_data']
```

### 8.2 配置标准化选项

```yaml
# config/analysis_config.yaml
analysis:
  standardize:
    enabled: true
    output_dir: "./data/standardized"
    format: "json"  # json, jsonl
    include_metadata: true
    validate: true
    schema_path: "./schemas/analysis_result_schema.json"
  
  training_data:
    enabled: true
    output_dir: "./data/training"
    formats: ["jsonl"]
    include_planning: true
    include_analysis: true
```

