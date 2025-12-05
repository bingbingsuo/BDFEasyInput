# BDFEasyInput AI 模块设计文档

## 1. AI 功能概述

### 1.1 核心功能
AI 模块允许用户使用自然语言描述计算需求，系统自动：
1. 理解用户意图
2. 规划计算任务
3. 生成 YAML 输入文件
4. 验证和优化建议

### 1.2 使用场景

**场景 1：自然语言输入**
```
用户："我想计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
  ↓
AI 规划模块理解需求
  ↓
生成 YAML 输入文件
  ↓
转换为 BDF 输入
```

**场景 2：不完整的输入**
```
用户："帮我优化苯分子的结构"
  ↓
AI 自动补充：
  - 推荐合适的方法和基组
  - 设置优化参数
  - 处理分子结构
  ↓
生成完整的 YAML 输入
```

**场景 3：智能建议**
```
用户："计算一个过渡金属配合物的电子结构"
  ↓
AI 提供建议：
  - 推荐适合过渡金属的泛函
  - 建议基组选择
  - 考虑相对论效应
  ↓
生成优化的 YAML 输入
```

## 2. 架构设计

### 2.1 系统架构更新

```
┌─────────────────────────────────────────────────────────────┐
│                  用户输入层 (多种方式)                        │
│  • 自然语言描述                                               │
│  • YAML/JSON 文件                                            │
│  • 命令行参数                                                 │
│  • 交互式对话                                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI 规划层 (NEW)                             │
│  • 意图理解                                                   │
│  • 任务规划                                                   │
│  • 参数推荐                                                   │
│  • YAML 生成                                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    输入解析层 (Parser)                        │
│  • YAML 解析器                                                │
│  • JSON 解析器                                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        [后续流程：验证 → 转换 → 生成]
```

### 2.2 AI 模块组件

```
ai/
├── __init__.py
├── client/              # AI 客户端接口
│   ├── base.py         # 基础接口
│   ├── local.py        # 本地模型客户端
│   ├── openai.py       # OpenAI API 客户端
│   ├── ollama.py       # Ollama 本地模型
│   └── anthropic.py    # Anthropic API 客户端
├── planner/            # 任务规划器
│   ├── task_planner.py
│   ├── method_recommender.py
│   └── parameter_optimizer.py
├── prompt/             # 提示词模板
│   ├── system_prompts.py
│   ├── user_prompts.py
│   └── templates.py
├── parser/             # AI 输出解析
│   ├── yaml_parser.py
│   └── response_parser.py
└── config/             # AI 配置
    └── model_config.py
```

## 3. AI 客户端设计

### 3.1 统一接口

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class AIClient(ABC):
    """AI 客户端统一接口"""
    
    @abstractmethod
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """发送对话请求，返回响应"""
        pass
    
    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> Iterator[str]:
        """流式对话，返回生成器"""
        pass
```

### 3.2 本地模型支持

**Ollama 集成**：
```python
class OllamaClient(AIClient):
    """Ollama 本地模型客户端"""
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # 调用 Ollama API
        pass
```

**其他本地模型**：
- vLLM 服务
- LM Studio
- 自定义模型服务

### 3.3 远程模型支持

**OpenAI API**：
```python
class OpenAIClient(AIClient):
    """OpenAI API 客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
```

**Anthropic Claude**：
```python
class AnthropicClient(AIClient):
    """Anthropic Claude API 客户端"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
```

### 3.4 模型配置

```yaml
# config/ai_config.yaml
ai:
  provider: "ollama"  # 或 "openai", "anthropic"
  
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3"
    timeout: 60
  
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    temperature: 0.7
  
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet-20240229"
  
  defaults:
    temperature: 0.7
    max_tokens: 2000
```

## 4. 任务规划器设计

### 4.1 任务规划流程

```python
class TaskPlanner:
    """计算任务规划器"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.prompt_builder = PromptBuilder()
    
    def plan(
        self, 
        user_query: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """规划计算任务，返回结构化的任务描述"""
        
        # 1. 构建系统提示词
        system_prompt = self.prompt_builder.build_system_prompt()
        
        # 2. 构建用户提示词
        user_prompt = self.prompt_builder.build_user_prompt(
            user_query, 
            context
        )
        
        # 3. 调用 AI 模型
        response = self.ai_client.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # 4. 解析 AI 响应
        task_config = self.parse_response(response)
        
        # 5. 验证和优化
        task_config = self.validate_and_optimize(task_config)
        
        return task_config
    
    def parse_response(self, response: str) -> Dict:
        """解析 AI 响应为结构化数据"""
        # 尝试提取 YAML
        # 或使用 JSON 格式
        pass
```

### 4.2 系统提示词设计

```python
SYSTEM_PROMPT = """
你是一个量子化学计算专家，专门帮助用户规划 BDF 量子化学计算任务。

你的任务是根据用户的自然语言描述，生成标准的 YAML 格式计算输入文件。

你的输出应该是有效的 YAML 格式，包含以下部分：
1. task: 计算类型（energy, optimize, frequency 等）
2. molecule: 分子结构（坐标、电荷、自旋多重度）
3. method: 计算方法（DFT 泛函、基组等）
4. settings: 计算设置（收敛标准、迭代次数等）

**重要提醒 - 自旋多重度（multiplicity）**：
- **必须提醒用户设置自旋多重度**，这是计算的关键参数
- 自旋多重度 = 2S + 1，其中 S 是总自旋量子数
- 如果用户未指定，BDF 将按以下默认规则处理：
  * 偶数电子数 → 自旋多重度 = 1（闭壳层）
  * 奇数电子数 → 自旋多重度 = 2（开壳层）
- **强烈建议**：在生成 YAML 时，如果用户未明确指定，应该：
  1. 根据分子化学式推断合理的自旋多重度
  2. 如果无法确定，在 YAML 中添加注释提醒用户检查
  3. 对于自由基、激发态等特殊情况，必须明确询问用户

请遵循以下原则：
- 如果用户没有指定方法，推荐合适的方法和基组
- **如果用户没有指定自旋多重度，必须根据分子特征推断或提醒用户**
- 确保参数合理且兼容
- 对于复杂体系，给出专业建议
- 输出必须是有效的 YAML 格式

支持的 DFT 泛函：PBE, PBE0, B3LYP, M06-2X 等
支持的基组：cc-pVDZ, cc-pVTZ, 6-31G*, def2-SVP 等
"""
```

### 4.3 方法推荐器

```python
class MethodRecommender:
    """根据体系特征推荐计算方法"""
    
    def recommend(
        self,
        molecule_info: Dict,
        task_type: str,
        user_preference: Optional[str] = None
    ) -> Dict:
        """推荐合适的方法和基组"""
        
        recommendations = {
            "functional": None,
            "basis": None,
            "reason": ""
        }
        
        # 基于体系特征的推荐逻辑
        # 或调用 AI 给出建议
        
        return recommendations
```

## 5. YAML 生成流程

### 5.1 完整流程

```
用户自然语言输入
    ↓
[AI 规划器] 理解需求 + 规划任务
    ↓
生成 YAML 字符串
    ↓
[YAML 解析器] 验证和结构化
    ↓
[验证器] 检查完整性和合理性
    ↓
输出 YAML 文件 或 继续后续流程
```

### 5.2 输出格式

AI 应该输出标准的 YAML 格式：

```yaml
task:
  type: energy
  description: "单点能计算"

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    # 单位由 molecule.units 指定（默认: angstrom）
    - O  0.0000 0.0000 0.0000
    - H  0.9572 0.0000 0.0000
    - H -0.2398 0.9266 0.0000
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom

method:
  type: dft
  functional: pbe0
  basis: cc-pvdz

settings:
  scf:
    convergence: 1e-6
```

## 6. 提示词工程

### 6.1 Few-Shot Learning

在提示词中包含示例：

```python
EXAMPLES = """
示例 1:
用户: "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"

输出:
```yaml
task:
  type: energy
molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    # 单位由 molecule.units 指定（默认: angstrom）
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom
method:
  type: dft
  functional: pbe0
  basis: cc-pvdz
```
"""
```

### 6.2 结构化输出

引导 AI 输出结构化内容：

```python
PROMPT_TEMPLATE = """
用户需求：{user_query}

请按照以下结构生成 YAML：
1. 分析需求
2. 提取关键信息
3. 生成 YAML 配置
4. 给出推荐理由（可选）

必须输出有效的 YAML 格式。
"""
```

## 7. 配置和部署

### 7.1 配置文件

```yaml
# config/ai_settings.yaml
ai:
  enabled: true
  default_provider: "ollama"
  
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"
    
    openai:
      enabled: false
      api_key_env: "OPENAI_API_KEY"
      model: "gpt-4"
    
    anthropic:
      enabled: false
      api_key_env: "ANTHROPIC_API_KEY"
      model: "claude-3-sonnet"
  
  planning:
    temperature: 0.7
    max_tokens: 2000
    use_streaming: false
  
  prompts:
    system_prompt_file: "prompts/system.txt"
    examples_file: "prompts/examples.yaml"
```

### 7.2 环境变量

```bash
# .env 文件
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

## 8. 使用示例

### 8.1 命令行使用

```bash
# 使用自然语言生成 YAML
bdfeasyinput ai-plan "计算水分子的单点能，使用 PBE0 方法"

# 指定 AI 提供商
bdfeasyinput ai-plan "优化苯分子结构" --provider ollama --model llama3

# 交互式对话
bdfeasyinput ai-chat

# 从对话生成 YAML
bdfeasyinput ai-chat --output task.yaml
```

### 8.2 Python API

```python
from bdfeasyinput.ai import TaskPlanner
from bdfeasyinput.ai.client import OllamaClient

# 初始化 AI 客户端
client = OllamaClient(model_name="llama3")

# 创建规划器
planner = TaskPlanner(ai_client=client)

# 规划任务
task_config = planner.plan(
    "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
)

# 保存 YAML
with open("task.yaml", "w") as f:
    yaml.dump(task_config, f)
```

### 8.3 交互式对话

```python
from bdfeasyinput.ai import InteractivePlanner

planner = InteractivePlanner()

# 开始对话
planner.start_conversation()

# 用户: "我想计算一个过渡金属配合物"
# AI: "请问您要计算什么性质？是单点能、几何优化还是其他？"
# 用户: "几何优化"
# AI: "好的，我建议使用 PBE0 泛函和 def2-TZVP 基组..."
# ... 对话继续直到生成完整的 YAML
```

## 9. 错误处理和验证

### 9.1 AI 输出验证

```python
class AIResponseValidator:
    """验证 AI 生成的 YAML"""
    
    def validate(self, ai_response: str) -> ValidationResult:
        """验证 AI 输出"""
        # 1. 检查 YAML 格式
        # 2. 检查必需字段
        # 3. 检查参数合理性
        # 4. 如果不合法，提示 AI 重新生成
        pass
```

### 9.2 错误处理策略

1. **YAML 格式错误**：提示 AI 修正或手动修复
2. **参数不完整**：自动补充或询问用户
3. **参数不合理**：警告并给出建议
4. **AI 响应异常**：重试或降级到手动输入

## 10. 性能优化

### 10.1 缓存机制

- 缓存常见的任务规划结果
- 缓存模型响应（相同输入）

### 10.2 流式输出

- 支持流式响应，提升用户体验
- 实时显示生成进度

### 10.3 批量处理

- 支持批量规划任务
- 优化 API 调用

## 11. 安全考虑

### 11.1 API 密钥管理

- 使用环境变量存储密钥
- 支持密钥轮换
- 不在日志中记录密钥

### 11.2 输入验证

- 验证用户输入，防止注入攻击
- 限制输入长度和内容

### 11.3 数据隐私

- 本地模型优先（数据不离开本地）
- 远程 API 使用时明确告知用户
- 支持数据脱敏

## 12. 开发计划

### Phase 1: 基础 AI 集成（2-3 周）
- [ ] AI 客户端接口设计
- [ ] Ollama 客户端实现
- [ ] OpenAI 客户端实现（可选）
- [ ] 基础提示词模板

### Phase 2: 任务规划器（2-3 周）
- [ ] 任务规划器实现
- [ ] YAML 生成逻辑
- [ ] 响应解析和验证
- [ ] 错误处理

### Phase 3: 优化和扩展（2-3 周）
- [ ] 方法推荐功能
- [ ] 交互式对话
- [ ] 提示词优化
- [ ] 性能优化

### Phase 4: 集成测试（1-2 周）
- [ ] 端到端测试
- [ ] 用户测试
- [ ] 文档完善

## 13. 依赖更新

需要添加的依赖：

```txt
# AI 相关
openai>=1.0.0          # OpenAI API
anthropic>=0.3.0       # Anthropic API
ollama>=0.1.0          # Ollama 客户端
langchain>=0.1.0       # 可选：LangChain 支持
```

