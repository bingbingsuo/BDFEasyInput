# BDF 执行和结果分析模块设计

## 1. 功能概述

### 1.1 核心功能
1. **BDF 执行集成**：生成 BDF 输入后，自动调用 BDFAutotest 运行 BDF
2. **结果分析**：使用 AI/LLM 模型分析 BDF 输出文件
3. **专家级分析**：基于量子化学专家模式，提供计算结果的专业分析

### 1.2 工作流程

```
生成 BDF 输入文件
    ↓
调用 BDFAutotest 运行 BDF
    ↓
等待计算完成
    ↓
读取输出文件和错误文件
    ↓
AI 分析计算结果
    ↓
生成分析报告（用户友好）
```

## 2. BDFAutotest 集成模块

### 2.1 模块结构

```
bdfeasyinput/
├── execution/              # ⭐ NEW 执行模块
│   ├── __init__.py
│   ├── bdfautotest.py      # BDFAutotest 集成
│   ├── runner.py           # 执行管理器
│   └── monitor.py          # 计算监控
```

### 2.2 BDFAutotest 接口设计

```python
from typing import Optional, Dict, List
from pathlib import Path

class BDFAutotestRunner:
    """BDFAutotest 执行器"""
    
    def __init__(
        self,
        bdfautotest_path: str,
        bdf_executable: Optional[str] = None,
        working_dir: Optional[str] = None
    ):
        """
        初始化 BDFAutotest 执行器
        
        Args:
            bdfautotest_path: BDFAutotest 工具路径
            bdf_executable: BDF 可执行文件路径（如果 BDFAutotest 需要）
            working_dir: 工作目录
        """
        self.bdfautotest_path = Path(bdfautotest_path)
        self.bdf_executable = bdf_executable
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
    
    def run(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """
        运行 BDF 计算
        
        Args:
            input_file: BDF 输入文件路径
            output_dir: 输出目录（默认与输入文件同目录）
            timeout: 超时时间（秒）
            **kwargs: 其他传递给 BDFAutotest 的参数
        
        Returns:
            包含执行结果的字典：
            {
                'status': 'success' | 'failed' | 'timeout',
                'output_file': str,
                'error_file': str,
                'log_file': str,
                'exit_code': int,
                'execution_time': float
            }
        """
        pass
    
    def check_status(self, job_id: str) -> Dict:
        """检查计算任务状态"""
        pass
    
    def cancel(self, job_id: str) -> bool:
        """取消正在运行的计算"""
        pass
```

### 2.3 执行管理器

```python
class ExecutionManager:
    """计算执行管理器"""
    
    def __init__(self, runner: BDFAutotestRunner):
        self.runner = runner
        self.active_jobs: Dict[str, Dict] = {}
    
    def submit(
        self,
        input_file: str,
        job_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """提交计算任务，返回任务 ID"""
        pass
    
    def wait_for_completion(
        self,
        job_id: str,
        check_interval: int = 5,
        timeout: Optional[int] = None
    ) -> Dict:
        """等待任务完成"""
        pass
    
    def get_results(self, job_id: str) -> Dict:
        """获取计算结果"""
        pass
```

### 2.4 计算监控

```python
class CalculationMonitor:
    """计算过程监控"""
    
    def monitor(
        self,
        job_id: str,
        callback: Optional[Callable] = None
    ) -> None:
        """
        监控计算过程
        
        Args:
            job_id: 任务 ID
            callback: 状态更新回调函数
        """
        pass
    
    def get_progress(self, job_id: str) -> float:
        """获取计算进度（0.0-1.0）"""
        pass
    
    def get_log_tail(self, job_id: str, n_lines: int = 50) -> List[str]:
        """获取日志尾部内容"""
        pass
```

## 3. 结果分析模块

### 3.1 模块结构

```
bdfeasyinput/
├── analysis/                # ⭐ NEW 结果分析模块
│   ├── __init__.py
│   ├── parser/             # 输出文件解析
│   │   ├── output_parser.py
│   │   └── error_parser.py
│   ├── analyzer/           # AI 分析器
│   │   ├── base_analyzer.py
│   │   ├── quantum_chem_analyzer.py
│   │   └── result_summarizer.py
│   ├── prompt/             # 分析提示词
│   │   ├── analysis_prompts.py
│   │   └── expert_templates.py
│   ├── standardizer/       # ⭐ NEW 数据标准化模块
│   │   ├── __init__.py
│   │   ├── schema.py       # Schema 定义
│   │   ├── normalizer.py   # 数据标准化器
│   │   ├── validator.py    # 数据验证器
│   │   └── exporter.py     # 数据导出器
│   └── report/             # 报告生成
│       ├── report_generator.py
│       └── templates/
```

### 3.2 输出文件解析器

```python
class BDFOutputParser:
    """BDF 输出文件解析器"""
    
    def parse(self, output_file: str) -> Dict:
        """
        解析 BDF 输出文件
        
        Returns:
            包含解析结果的字典：
            {
                'energy': float,           # 总能量
                'scf_energy': float,       # SCF 能量
                'converged': bool,         # 是否收敛
                'geometry': List[Dict],    # 优化后的几何结构
                'frequencies': List[float], # 频率（如果有）
                'properties': Dict,        # 其他性质
                'warnings': List[str],     # 警告信息
                'errors': List[str]        # 错误信息
            }
        """
        pass
    
    def extract_energy(self, output_file: str) -> Optional[float]:
        """提取总能量"""
        pass
    
    def extract_geometry(self, output_file: str) -> List[Dict]:
        """提取几何结构"""
        pass
    
    def check_convergence(self, output_file: str) -> bool:
        """检查计算是否收敛"""
        pass
    
    def extract_frequencies(self, output_file: str) -> List[float]:
        """提取频率（如果有）"""
        pass
```

### 3.3 AI 分析器

```python
class QuantumChemistryAnalyzer:
    """量子化学专家级结果分析器"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.output_parser = BDFOutputParser()
        self.prompt_builder = AnalysisPromptBuilder()
    
    def analyze(
        self,
        output_file: str,
        input_file: Optional[str] = None,
        error_file: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> Dict:
        """
        分析计算结果
        
        Returns:
            分析结果字典：
            {
                'summary': str,              # 简要总结
                'energy_analysis': str,     # 能量分析
                'geometry_analysis': str,    # 几何结构分析
                'convergence_analysis': str, # 收敛性分析
                'recommendations': List[str], # 建议
                'warnings': List[str],       # 警告
                'expert_insights': str      # 专家见解
            }
        """
        # 1. 解析输出文件
        parsed_data = self.output_parser.parse(output_file)
        
        # 2. 构建分析提示词
        prompt = self.prompt_builder.build_analysis_prompt(
            parsed_data=parsed_data,
            input_file=input_file,
            error_file=error_file,
            task_type=task_type
        )
        
        # 3. 调用 AI 分析
        analysis = self.ai_client.chat([
            {"role": "system", "content": self.prompt_builder.get_system_prompt()},
            {"role": "user", "content": prompt}
        ])
        
        # 4. 解析 AI 响应
        result = self.parse_analysis_response(analysis, parsed_data)
        
        return result
    
    def parse_analysis_response(
        self,
        ai_response: str,
        parsed_data: Dict
    ) -> Dict:
        """解析 AI 分析响应"""
        pass
```

### 3.4 分析提示词设计

#### 系统提示词（量子化学专家模式）

```python
QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT = """
你是一位资深的量子化学计算专家，专门分析 BDF 量子化学计算软件的输出结果。

你的任务是：
1. 分析计算结果的质量和可靠性
2. 解释计算结果的意义
3. 识别潜在的问题和警告
4. 提供专业的建议和见解
5. 用通俗易懂的语言向用户解释复杂的量子化学概念

分析重点：
- **能量分析**：总能量、SCF 能量、相对能量等
- **几何结构**：键长、键角、二面角、对称性等
- **收敛性**：SCF 收敛、几何优化收敛等
- **电子结构**：轨道能量、HOMO-LUMO 能隙、电子密度等
- **振动分析**：频率、红外强度、热力学性质等
- **方法评估**：计算方法的适用性、基组质量等

输出要求：
- 使用专业但易懂的语言
- 提供具体的数值和单位
- 给出明确的结论和建议
- 指出需要注意的问题
"""
```

#### 分析提示词模板

```python
def build_analysis_prompt(
    parsed_data: Dict,
    input_file: Optional[str] = None,
    error_file: Optional[str] = None,
    task_type: Optional[str] = None
) -> str:
    """构建分析提示词"""
    
    prompt = f"""
请分析以下 BDF 量子化学计算结果：

**计算任务类型**：{task_type or '未知'}

**计算结果**：
- 总能量：{parsed_data.get('energy', 'N/A')} Hartree
- SCF 收敛：{'是' if parsed_data.get('converged') else '否'}
- 计算状态：{'成功' if parsed_data.get('converged') else '未收敛或失败'}

"""
    
    if parsed_data.get('geometry'):
        prompt += f"""
**几何结构**：
{format_geometry(parsed_data['geometry'])}
"""
    
    if parsed_data.get('frequencies'):
        prompt += f"""
**振动频率**：
{format_frequencies(parsed_data['frequencies'])}
"""
    
    if error_file:
        prompt += f"""
**错误/警告信息**：
{read_error_file(error_file)}
"""
    
    prompt += """
请提供以下分析：
1. **结果总结**：简要说明计算是否成功，主要结果是什么
2. **能量分析**：分析能量的合理性，与文献值对比（如果可能）
3. **几何结构分析**：分析键长、键角等是否合理
4. **收敛性评估**：评估计算的收敛质量
5. **方法评估**：评估所用方法和基组的适用性
6. **专业建议**：如果需要改进，给出具体建议
7. **专家见解**：提供更深层次的专业分析

请用专业但易懂的语言，面向非专家用户。
"""
    
    return prompt
```

### 3.5 报告生成器

```python
class AnalysisReportGenerator:
    """分析报告生成器"""
    
    def generate(
        self,
        analysis_result: Dict,
        output_format: str = "markdown"
    ) -> str:
        """
        生成分析报告
        
        Args:
            analysis_result: AI 分析结果
            output_format: 输出格式（markdown, html, text）
        
        Returns:
            格式化的报告字符串
        """
        pass
    
    def generate_markdown(self, analysis_result: Dict) -> str:
        """生成 Markdown 格式报告"""
        pass
    
    def generate_html(self, analysis_result: Dict) -> str:
        """生成 HTML 格式报告"""
        pass
```

## 4. 完整工作流集成

### 4.1 端到端流程

```python
class BDFEasyInputWorkflow:
    """完整的 BDFEasyInput 工作流"""
    
    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        bdfautotest_path: Optional[str] = None
    ):
        self.ai_planner = TaskPlanner(ai_client) if ai_client else None
        self.runner = BDFAutotestRunner(bdfautotest_path) if bdfautotest_path else None
        self.analyzer = QuantumChemistryAnalyzer(ai_client) if ai_client else None
    
    def run_complete_workflow(
        self,
        user_input: str,  # 可以是自然语言或 YAML 文件路径
        run_calculation: bool = True,
        analyze_results: bool = True
    ) -> Dict:
        """
        完整工作流：
        1. 规划任务（如果是自然语言）
        2. 生成 BDF 输入
        3. 运行计算（可选）
        4. 分析结果（可选）
        """
        results = {}
        
        # 1. 规划任务
        if self.ai_planner and not Path(user_input).exists():
            yaml_config = self.ai_planner.plan(user_input)
            results['yaml_config'] = yaml_config
        else:
            # 从 YAML 文件读取
            yaml_config = load_yaml(user_input)
        
        # 2. 生成 BDF 输入
        bdf_input = self.generate_bdf_input(yaml_config)
        results['bdf_input_file'] = bdf_input
        
        # 3. 运行计算
        if run_calculation and self.runner:
            execution_result = self.runner.run(bdf_input)
            results['execution'] = execution_result
            
            # 4. 分析结果
            if analyze_results and self.analyzer and execution_result['status'] == 'success':
                analysis = self.analyzer.analyze(
                    output_file=execution_result['output_file'],
                    input_file=bdf_input,
                    error_file=execution_result.get('error_file')
                )
                results['analysis'] = analysis
                
                # 生成报告
                report = AnalysisReportGenerator().generate(analysis)
                results['report'] = report
        
        return results
```

### 4.2 命令行接口

```bash
# 完整工作流：规划 + 生成 + 运行 + 分析
bdfeasyinput workflow "计算水分子的单点能" \
  --run \
  --analyze \
  --output-dir ./results

# 只运行计算（不分析）
bdfeasyinput run bdf_input.inp --output-dir ./results

# 只分析已有结果
bdfeasyinput analyze output.out --input bdf_input.inp
```

## 5. 配置管理

### 5.1 BDFAutotest 配置

```yaml
# config/execution_config.yaml
execution:
  bdfautotest:
    path: "/path/to/bdfautotest"  # 或环境变量 BDFAUTOTEST_PATH
    bdf_executable: "/path/to/bdf"  # 可选
    default_timeout: 3600  # 默认超时时间（秒）
    default_output_dir: "./bdf_results"
  
  monitoring:
    check_interval: 5  # 检查间隔（秒）
    log_tail_lines: 50  # 日志尾部行数
```

### 5.2 分析配置

```yaml
# config/analysis_config.yaml
analysis:
  ai:
    provider: "ollama"  # 使用哪个 AI 提供商
    model: "llama3"
  
  output:
    format: "markdown"  # markdown, html, text
    include_raw_data: true  # 是否包含原始数据
    include_recommendations: true  # 是否包含建议
  
  expert_mode:
    enabled: true
    depth: "detailed"  # brief, standard, detailed
```

## 6. 使用示例

### 6.1 Python API

```python
from bdfeasyinput import BDFEasyInputWorkflow
from bdfeasyinput.ai.client import OllamaClient

# 初始化
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

### 6.2 分步执行

```python
# 1. 只生成输入
workflow = BDFEasyInputWorkflow(ai_client=client)
results = workflow.run_complete_workflow(
    "计算水分子的单点能",
    run_calculation=False,
    analyze_results=False
)

# 2. 运行计算
from bdfeasyinput.execution import BDFAutotestRunner
runner = BDFAutotestRunner("/path/to/bdfautotest")
execution_result = runner.run(results['bdf_input_file'])

# 3. 分析结果
from bdfeasyinput.analysis import QuantumChemistryAnalyzer
analyzer = QuantumChemistryAnalyzer(client)
analysis = analyzer.analyze(execution_result['output_file'])
```

## 7. 错误处理

### 7.1 计算失败处理

```python
def handle_calculation_failure(
    execution_result: Dict,
    analyzer: QuantumChemistryAnalyzer
) -> Dict:
    """处理计算失败的情况"""
    
    if execution_result['status'] == 'failed':
        # 分析错误文件
        error_analysis = analyzer.analyze_error(
            execution_result['error_file']
        )
        return {
            'status': 'failed',
            'error_analysis': error_analysis,
            'suggestions': error_analysis.get('suggestions', [])
        }
```

### 7.2 分析失败处理

- 如果 AI 分析失败，降级到基础解析
- 提供原始数据供用户查看
- 记录错误日志

## 8. 性能优化

### 8.1 异步执行

- 支持异步提交多个计算任务
- 批量分析结果

### 8.2 缓存机制

- 缓存解析结果
- 缓存 AI 分析结果（相同输出文件）

## 9. 数据标准化 ⭐ NEW

### 9.1 标准化功能
- 统一的数据格式（JSON Schema）
- 自动标准化分析结果
- 训练数据准备（JSONL 格式）
- 数据验证和质量保证

### 9.2 详细设计
参考 [DATA_STANDARDIZATION_DESIGN.md](DATA_STANDARDIZATION_DESIGN.md) 了解完整的数据标准化设计。

## 10. 开发计划

### Phase 1: BDFAutotest 集成（2-3 周）
- [ ] BDFAutotest 接口设计
- [ ] 执行管理器实现
- [ ] 计算监控功能
- [ ] 测试和验证

### Phase 2: 结果分析基础（2-3 周）
- [ ] 输出文件解析器
- [ ] 基础数据提取
- [ ] 简单分析功能

### Phase 3: AI 分析集成（3-4 周）
- [ ] AI 分析器实现
- [ ] 专家级提示词设计
- [ ] 报告生成器
- [ ] 测试和优化

### Phase 4: 数据标准化（2-3 周）⭐ NEW
- [ ] 数据 Schema 定义
- [ ] 标准化器实现
- [ ] 训练数据准备
- [ ] 数据验证和导出

### Phase 5: 工作流集成（1-2 周）
- [ ] 端到端工作流
- [ ] 命令行接口
- [ ] 文档完善

