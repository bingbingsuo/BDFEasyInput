# 完整工作流使用示例

## 1. 完整工作流（推荐）

### 1.1 命令行使用

```bash
# 完整流程：规划 + 生成 + 运行 + 分析
bdfeasyinput workflow "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" \
  --run \
  --analyze \
  --output-dir ./results \
  --bdfautotest /path/to/bdfautotest

# 结果将保存在 ./results 目录：
# - bdf_input.inp (BDF 输入文件)
# - output.out (BDF 输出文件)
# - error.err (错误文件，如果有)
# - analysis_report.md (AI 分析报告)
```

### 1.2 Python API

```python
from bdfeasyinput import BDFEasyInputWorkflow
from bdfeasyinput.ai.client import OllamaClient

# 初始化工作流
client = OllamaClient(model_name="llama3")
workflow = BDFEasyInputWorkflow(
    ai_client=client,
    bdfautotest_path="/path/to/bdfautotest"
)

# 运行完整工作流
results = workflow.run_complete_workflow(
    "计算水分子的单点能，使用 PBE0 方法",
    run_calculation=True,
    analyze_results=True
)

# 查看结果
print("BDF 输入文件:", results['bdf_input_file'])
print("执行状态:", results['execution']['status'])
print("分析报告:\n", results['report'])
```

## 2. 分步执行

### 2.1 步骤 1：规划任务

```bash
# 使用 AI 规划任务
bdfeasyinput ai-plan "计算水分子的单点能" -o task.yaml
```

### 2.2 步骤 2：生成 BDF 输入

```bash
# 转换为 BDF 输入
bdfeasyinput convert task.yaml -o bdf_input.inp
```

### 2.3 步骤 3：运行计算

```bash
# 使用 BDFAutotest 运行
bdfeasyinput run bdf_input.inp \
  --bdfautotest /path/to/bdfautotest \
  --output-dir ./results
```

### 2.4 步骤 4：分析结果

```bash
# AI 分析计算结果
bdfeasyinput analyze ./results/output.out \
  --input bdf_input.inp \
  --output analysis_report.md
```

## 3. 只分析已有结果

如果您已经有 BDF 计算结果，可以直接分析：

```bash
# 分析已有输出文件
bdfeasyinput analyze existing_output.out \
  --input existing_input.inp \
  --output analysis.md

# 使用 Python API
from bdfeasyinput.analysis import QuantumChemistryAnalyzer
from bdfeasyinput.ai.client import OllamaClient

client = OllamaClient(model_name="llama3")
analyzer = QuantumChemistryAnalyzer(client)

analysis = analyzer.analyze(
    output_file="existing_output.out",
    input_file="existing_input.inp"
)

# 生成报告
from bdfeasyinput.analysis.report import AnalysisReportGenerator
report = AnalysisReportGenerator().generate(analysis)
print(report)
```

## 4. 分析报告示例

AI 生成的分析报告示例：

```markdown
# BDF 计算结果分析报告

## 计算总结

**计算类型**：单点能计算
**计算方法**：PBE0/cc-pVDZ
**计算状态**：成功收敛

## 能量分析

**总能量**：-76.4123 Hartree
**SCF 能量**：-76.4123 Hartree
**SCF 收敛**：是（收敛阈值：1e-6）

### 能量评估
- 总能量为负值，符合预期
- SCF 迭代收敛良好，能量变化小于阈值
- 建议：能量值合理，计算质量良好

## 几何结构分析

**分子**：H2O
**对称性**：C2v

**键长**：
- O-H: 0.9572 Å（合理范围：0.95-0.97 Å）
- H-H: 1.5144 Å

**键角**：
- H-O-H: 104.5°（合理范围：104-105°）

### 结构评估
- 几何结构合理，键长和键角在预期范围内
- 与实验值（H-O-H: 104.5°）吻合良好
- 建议：结构优化成功

## 收敛性分析

**SCF 收敛**：
- 迭代次数：12
- 最终能量变化：2.3e-7 Hartree
- 收敛质量：优秀

### 收敛评估
- SCF 快速收敛，表明初始猜测良好
- 能量变化远小于阈值，计算可靠
- 建议：无需调整参数

## 方法评估

**使用的计算方法**：PBE0/cc-pVDZ

### 方法适用性
- PBE0 是适合小分子的混合泛函
- cc-pVDZ 基组对水分子足够
- 建议：方法选择合适，结果可靠

## 专业建议

1. **计算质量**：本次计算质量良好，结果可靠
2. **进一步计算**（可选）：
   - 如需更高精度，可考虑使用 cc-pVTZ 基组
   - 可进行频率计算验证结构为最小值
3. **结果使用**：当前结果可用于后续分析

## 专家见解

本次计算成功完成了水分子的单点能计算。使用的 PBE0/cc-pVDZ 方法组合对于小分子体系是合适的选择。计算收敛良好，几何结构合理，与实验值吻合。总体而言，这是一个成功的计算，结果可以用于后续分析。
```

## 5. 配置 BDFAutotest

### 5.1 环境变量

```bash
export BDFAUTOTEST_PATH=/path/to/bdfautotest
export BDF_EXECUTABLE=/path/to/bdf  # 可选
```

### 5.2 配置文件

```yaml
# config/execution_config.yaml
execution:
  bdfautotest:
    path: "/path/to/bdfautotest"
    bdf_executable: "/path/to/bdf"
    default_timeout: 3600
    default_output_dir: "./bdf_results"
```

## 6. 错误处理

### 6.1 计算失败

如果计算失败，AI 会分析错误文件并提供建议：

```bash
# 计算失败后自动分析
bdfeasyinput workflow "..." --run --analyze

# 分析报告会包含：
# - 错误原因分析
# - 修复建议
# - 可能的解决方案
```

### 6.2 分析失败

如果 AI 分析失败，系统会：
- 提供基础解析结果（能量、结构等）
- 记录错误日志
- 允许用户查看原始输出文件

## 7. 批量处理

```python
# 批量处理多个任务
tasks = [
    "计算水分子的单点能",
    "优化苯分子的几何结构",
    "计算甲烷的频率"
]

for task in tasks:
    results = workflow.run_complete_workflow(
        task,
        run_calculation=True,
        analyze_results=True
    )
    print(f"任务完成: {task}")
    print(f"分析报告: {results['report']}")
```

## 8. 高级选项

### 8.1 自定义超时

```bash
bdfeasyinput run bdf_input.inp \
  --timeout 7200  # 2 小时超时
```

### 8.2 监控计算进度

```python
from bdfeasyinput.execution import ExecutionManager, BDFAutotestRunner

runner = BDFAutotestRunner("/path/to/bdfautotest")
manager = ExecutionManager(runner)

job_id = manager.submit("bdf_input.inp")

# 监控进度
while True:
    status = manager.check_status(job_id)
    print(f"进度: {status['progress']}%")
    if status['status'] == 'completed':
        break
    time.sleep(5)
```

### 8.3 自定义分析深度

```python
analyzer = QuantumChemistryAnalyzer(
    client,
    analysis_depth="detailed"  # brief, standard, detailed
)
```

