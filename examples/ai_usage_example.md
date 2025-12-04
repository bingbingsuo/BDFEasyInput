# AI 功能使用示例

## 1. 命令行使用

### 1.1 基础 AI 规划

```bash
# 使用自然语言生成 YAML 输入文件
bdfeasyinput ai-plan "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" -o task.yaml

# 指定使用本地 Ollama 模型
bdfeasyinput ai-plan "优化苯分子的几何结构" \
  --provider ollama \
  --model llama3 \
  -o benzene_opt.yaml

# 使用 OpenAI API
bdfeasyinput ai-plan "计算一个过渡金属配合物的电子结构" \
  --provider openai \
  --model gpt-4 \
  -o complex.yaml
```

### 1.2 交互式对话

```bash
# 启动交互式 AI 对话
bdfeasyinput ai-chat

# 对话示例：
# 用户: "我想计算一个分子的性质"
# AI: "请问您要计算什么分子？什么性质？"
# 用户: "水分子，单点能"
# AI: "好的，您希望使用什么计算方法？"
# ... 继续对话直到生成完整的 YAML
```

### 1.3 直接从对话生成输入

```bash
# 交互式对话并保存结果
bdfeasyinput ai-chat --output task.yaml

# 使用指定的 AI 提供商
bdfeasyinput ai-chat --provider ollama --model llama3
```

## 2. Python API 使用

### 2.1 基础任务规划

```python
from bdfeasyinput.ai import TaskPlanner
from bdfeasyinput.ai.client import OllamaClient

# 初始化本地 Ollama 客户端
client = OllamaClient(model_name="llama3")

# 创建任务规划器
planner = TaskPlanner(ai_client=client)

# 规划任务
task_config = planner.plan(
    "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
)

# 保存为 YAML
import yaml
with open("task.yaml", "w") as f:
    yaml.dump(task_config, f, default_flow_style=False)
```

### 2.2 使用 OpenAI API

```python
from bdfeasyinput.ai.client import OpenAIClient

# 初始化 OpenAI 客户端（需要设置 OPENAI_API_KEY 环境变量）
client = OpenAIClient(model="gpt-4")

planner = TaskPlanner(ai_client=client)

task_config = planner.plan(
    "优化苯分子的几何结构"
)
```

### 2.3 交互式对话

```python
from bdfeasyinput.ai import InteractivePlanner

# 创建交互式规划器
planner = InteractivePlanner()

# 开始对话
task_config = planner.start_conversation()

# 对话过程：
# AI: "您好！请描述您的计算需求。"
# 用户: "我想计算一个过渡金属配合物"
# AI: "请问您要计算什么性质？"
# 用户: "几何优化"
# AI: "好的，我建议使用 PBE0 泛函和 def2-TZVP 基组..."
# ... 继续直到完成
```

### 2.4 完整流程：AI 规划 + 生成 BDF 输入

```python
from bdfeasyinput.ai import TaskPlanner
from bdfeasyinput.ai.client import OllamaClient
from bdfeasyinput import BDFEasyInput

# 1. AI 规划任务
client = OllamaClient(model_name="llama3")
planner = TaskPlanner(ai_client=client)

yaml_config = planner.plan(
    "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
)

# 2. 保存 YAML（可选）
import yaml
with open("task.yaml", "w") as f:
    yaml.dump(yaml_config, f)

# 3. 转换为 BDF 输入
bdf_input = BDFEasyInput()
bdf_file_content = bdf_input.convert(yaml_config)

# 4. 保存 BDF 输入文件
with open("bdf_input.inp", "w") as f:
    f.write(bdf_file_content)
```

## 3. 使用场景示例

### 3.1 简单任务

**输入**：
```
"计算水分子的单点能"
```

**AI 自动补充**：
- 推荐方法：PBE0
- 推荐基组：cc-pVDZ
- 自动设置默认参数

**输出 YAML**：
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

### 3.2 复杂任务

**输入**：
```
"我想计算一个 Ru(II) 配合物的激发态，体系比较大，需要考虑相对论效应"
```

**AI 理解并规划**：
- 识别过渡金属体系
- 推荐使用相对论基组
- 选择适合的 TD-DFT 方法
- 设置合理的计算参数

### 3.3 不完整输入

**输入**：
```
"优化苯分子"
```

**AI 交互式补充**：
- 询问计算方法偏好
- 推荐基组
- 确认优化参数
- 处理分子结构

## 4. 配置 AI 提供商

### 4.1 配置文件方式

创建 `config/ai_config.yaml`：

```yaml
ai:
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
      model: "claude-3-sonnet-20240229"
```

### 4.2 环境变量方式

```bash
# .env 文件
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

## 5. 最佳实践

### 5.1 描述计算需求

**好的描述**：
- "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
- "优化苯分子的几何结构，使用 B3LYP/6-31G*"
- "计算一个过渡金属配合物的激发态，体系有 50 个原子"

**可以改进的描述**：
- "算个分子" → "计算什么分子？什么性质？"
- "优化" → "优化哪个分子？使用什么方法？"

### 5.2 使用交互式对话

对于复杂或不明确的需求，使用交互式对话：
- AI 会逐步询问缺失信息
- 可以实时调整需求
- 获得专业建议

### 5.3 验证 AI 输出

AI 生成的 YAML 会自动验证，但建议：
- 检查关键参数是否符合预期
- 确认分子结构正确
- 验证方法选择是否合适

## 6. 故障排除

### 6.1 AI 模型连接失败

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 检查 OpenAI API 密钥
echo $OPENAI_API_KEY
```

### 6.2 AI 输出格式错误

- 系统会自动验证 YAML 格式
- 如果格式错误，AI 会重新生成
- 可以手动修正后继续

### 6.3 响应时间过长

- 本地模型（Ollama）可能较慢
- 考虑使用更小的模型
- 或切换到远程 API（如果可用）

## 7. 隐私和安全

### 7.1 本地模型（推荐）

- 使用 Ollama 等本地模型
- 数据不离开本地
- 适合敏感研究

### 7.2 远程 API

- 明确告知用户数据会发送到远程服务
- 避免发送敏感信息
- 支持数据脱敏

