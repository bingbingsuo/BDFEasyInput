# BDFEasyInput 架构设计文档

## 1. 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     用户输入层                                │
│  • 自然语言描述 (NEW)                                         │
│  • YAML/JSON 文件                                            │
│  • 命令行参数                                                 │
│  • 交互式对话 (NEW)                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI 规划层 (NEW)                              │
│  • 意图理解                                                   │
│  • 任务规划                                                   │
│  • 参数推荐                                                   │
│  • YAML 生成                                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    输入解析层 (Parser)                        │
│  - YAML 解析器                                                │
│  - JSON 解析器                                                │
│  - CLI 参数解析器                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  输入验证层 (Validator)                       │
│  - Schema 验证                                                │
│  - 参数范围检查                                               │
│  - 兼容性检查                                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 转换引擎层 (Translator)                       │
│  - 方法映射 (DFT/HF/MP2 → BDF关键词)                         │
│  - 基组映射 (标准基组 → BDF基组)                             │
│  - 参数转换 (单位、格式)                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                生成引擎层 (Generator)                         │
│  - 模板引擎 (Jinja2)                                          │
│  - 格式化器                                                    │
│  - 输出管理                                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  BDF 输入文件                                  │
│              (专家模式格式)                                    │
└─────────────────────────────────────────────────────────────┘
```

## 2. 核心模块详细设计

### 2.0 AI 规划模块 (AI Planner) ⭐ NEW

**职责**：使用大语言模型理解用户需求，规划计算任务，生成 YAML 输入

**接口设计**：
```python
class TaskPlanner:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    def plan(self, user_query: str, context: Optional[Dict] = None) -> Dict:
        """规划计算任务，返回 YAML 结构化的任务描述"""
        pass
    
    def interactive_plan(self) -> Dict:
        """交互式对话规划"""
        pass

class AIClient(ABC):
    """AI 客户端统一接口"""
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送对话请求"""
        pass

class OllamaClient(AIClient):
    """Ollama 本地模型客户端"""
    pass

class OpenAIClient(AIClient):
    """OpenAI API 客户端"""
    pass
```

**工作流程**：
1. 接收用户自然语言输入
2. 构建系统提示词（包含量子化学专业知识）
3. 调用 AI 模型生成 YAML
4. 解析和验证 AI 输出
5. 返回结构化任务配置

### 2.1 输入解析模块 (Parser)

**职责**：将用户输入转换为内部数据结构

**接口设计**：
```python
class BaseParser:
    def parse(self, input_source: str) -> CalculationInput:
        """解析输入源，返回标准化的计算输入对象"""
        pass

class YAMLParser(BaseParser):
    def parse(self, yaml_file: str) -> CalculationInput:
        """解析 YAML 文件"""
        pass

class JSONParser(BaseParser):
    def parse(self, json_file: str) -> CalculationInput:
        """解析 JSON 文件"""
        pass

class CLIParser(BaseParser):
    def parse(self, args: argparse.Namespace) -> CalculationInput:
        """解析命令行参数"""
        pass
```

**内部数据结构**：
```python
@dataclass
class CalculationInput:
    task: TaskConfig
    molecule: MoleculeConfig
    method: MethodConfig
    settings: Optional[SettingsConfig] = None
```

### 2.2 验证模块 (Validator)

**职责**：验证输入的正确性和完整性

**验证层次**：
1. **Schema 验证**：使用 Pydantic 进行基础类型和结构验证
2. **业务逻辑验证**：
   - 电荷与自旋多重度的兼容性
   - 基组与方法的兼容性
   - 计算类型与方法的兼容性
   - 参数范围检查

**接口设计**：
```python
class Validator:
    def validate(self, input: CalculationInput) -> ValidationResult:
        """验证输入，返回验证结果"""
        pass
    
    def validate_schema(self, input: CalculationInput) -> bool:
        """Schema 验证"""
        pass
    
    def validate_business_logic(self, input: CalculationInput) -> List[Error]:
        """业务逻辑验证"""
        pass
```

### 2.3 转换模块 (Translator)

**职责**：将用户友好的输入转换为 BDF 内部表示

**核心映射**：

1. **计算方法映射**：
   ```
   "hf" → BDF HF 关键词
   "pbe0" → BDF PBE0 关键词
   "b3lyp" → BDF B3LYP 关键词
   ```

2. **基组映射**：
   ```
   "cc-pvdz" → BDF 基组库中的对应基组
   "6-31g*" → BDF 基组库中的对应基组
   ```

3. **计算类型映射**：
   ```
   "energy" → 单点能计算
   "optimize" → 几何优化
   "frequency" → 频率计算
   ```

**接口设计**：
```python
class Translator:
    def translate(self, input: CalculationInput) -> BDFConfig:
        """将计算输入转换为 BDF 配置"""
        pass

class DFTTranslator(Translator):
    def translate_functional(self, functional: str) -> str:
        """转换 DFT 泛函名称"""
        pass

class BasisSetTranslator(Translator):
    def translate_basis(self, basis: str) -> str:
        """转换基组名称"""
        pass
```

### 2.4 生成模块 (Generator)

**职责**：根据 BDF 配置生成输入文件

### 2.5 执行模块 (Execution) ⭐ NEW

**职责**：集成 BDFAutotest，运行 BDF 计算

**接口设计**：
```python
class BDFAutotestRunner:
    def run(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """运行 BDF 计算，返回执行结果"""
        pass

class ExecutionManager:
    def submit(self, input_file: str) -> str:
        """提交计算任务"""
        pass
    
    def wait_for_completion(self, job_id: str) -> Dict:
        """等待任务完成"""
        pass
```

### 2.6 结果分析模块 (Analysis) ⭐ NEW

**职责**：使用 AI 分析 BDF 计算结果

**接口设计**：
```python
class BDFOutputParser:
    def parse(self, output_file: str) -> Dict:
        """解析 BDF 输出文件，提取关键数据"""
        pass

class QuantumChemistryAnalyzer:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    def analyze(
        self,
        output_file: str,
        input_file: Optional[str] = None
    ) -> Dict:
        """使用 AI 分析计算结果"""
        pass
```

**分析重点**：
- 能量分析（总能量、SCF 能量、相对能量）
- 几何结构分析（键长、键角、对称性）
- 收敛性评估
- 电子结构分析（HOMO-LUMO、轨道能量）
- 振动分析（频率、红外强度）
- 方法评估（方法和基组的适用性）

**模板系统**：
- 使用 Jinja2 模板引擎
- 模板存储在 `templates/` 目录
- 支持模板继承和组合

**接口设计**：
```python
class Generator:
    def __init__(self, template_dir: str):
        self.template_env = jinja2.Environment(...)
    
    def generate(self, config: BDFConfig, output_file: str) -> str:
        """生成 BDF 输入文件"""
        pass
    
    def format_output(self, content: str) -> str:
        """格式化输出，确保符合 BDF 规范"""
        pass
```

## 3. 数据流

### 3.1 标准流程

**传统流程（YAML 输入）**：
```
用户输入 (YAML)
    ↓
[Parser] → CalculationInput (Pydantic Model)
    ↓
[Validator] → 验证通过
    ↓
[Translator] → BDFConfig (内部表示)
    ↓
[Generator] → BDF 输入文件 (文本)
```

**AI 辅助流程（自然语言输入）**：
```
用户自然语言描述
    ↓
[AI Planner] → 理解需求 + 规划任务
    ↓
生成 YAML 字符串
    ↓
[Parser] → CalculationInput (Pydantic Model)
    ↓
[Validator] → 验证通过
    ↓
[Translator] → BDFConfig (内部表示)
    ↓
[Generator] → BDF 输入文件 (文本)
    ↓
[Execution] → 调用 BDFAutotest 运行 BDF ⭐ NEW
    ↓
[Analysis] → AI 分析计算结果 ⭐ NEW
    ↓
生成分析报告 ⭐ NEW
```

**完整工作流** ⭐ NEW：
```
用户输入（自然语言或 YAML）
    ↓
[AI 规划] → YAML
    ↓
[转换] → BDF 输入文件
    ↓
[执行] → BDFAutotest → BDF 运行
    ↓
[分析] → AI 分析输出文件
    ↓
用户友好的分析报告
```

### 3.2 错误处理流程

```
任何步骤失败
    ↓
记录错误信息
    ↓
返回友好的错误消息
    ↓
建议修复方案
```

## 4. 配置管理

### 4.1 映射配置文件

将方法、基组等映射关系存储在配置文件中：

```yaml
# config/mappings.yaml
methods:
  hf:
    bdf_keyword: "HF"
  pbe0:
    bdf_keyword: "PBE0"
    type: "hybrid_dft"
  
basis_sets:
  cc-pvdz:
    bdf_name: "cc-pVDZ"
    library_path: "..."
  "6-31g*":
    bdf_name: "6-31G*"
```

### 4.2 默认值配置

```yaml
# config/defaults.yaml
scf:
  convergence: 1e-6
  max_iterations: 100
geometry_optimization:
  max_iterations: 50
  convergence_threshold: 1e-4
```

## 5. 扩展性设计

### 5.1 插件系统

为了支持未来扩展，考虑插件架构：

```python
class TranslatorPlugin:
    """转换器插件接口"""
    def can_handle(self, input: CalculationInput) -> bool:
        pass
    
    def translate(self, input: CalculationInput) -> BDFConfig:
        pass

# 注册插件
register_plugin(DFTTranslator())
register_plugin(WavefunctionTranslator())
```

### 5.2 模板系统扩展

- 支持自定义模板
- 支持模板变量
- 支持条件渲染

## 6. 测试策略

### 6.1 单元测试
- 每个模块独立测试
- Mock 外部依赖

### 6.2 集成测试
- 端到端测试
- 与真实 BDF 输入文件对比

### 6.3 示例测试
- 验证示例输入能正确生成
- 回归测试

## 7. 性能考虑

- 解析器：一次性解析，结果缓存
- 模板渲染：预编译模板
- 大型分子：流式处理坐标

## 8. 错误处理策略

- 详细的错误消息
- 错误代码系统
- 建议和修复提示
- 日志记录

