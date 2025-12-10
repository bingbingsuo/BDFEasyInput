# AI 服务商使用指南

BDFEasyInput 支持多种 AI 服务商，包括本地模型和云端 API。本文档介绍如何配置和使用这些服务商。

## 支持的服务商

### 本地模型
- **Ollama** - 本地运行的模型，推荐用于隐私保护

### 官方 API
- **OpenAI** - GPT-4, GPT-3.5 等
- **Anthropic** - Claude 系列模型

### OpenAI 兼容服务（新增）
- **OpenRouter** - 统一访问多个模型提供商
- **Together AI** - 开源模型 API
- **Groq** - 快速推理服务
- **DeepSeek** - DeepSeek 模型
- **Mistral AI** - Mistral 模型
- **Perplexity** - Perplexity 模型

## 配置方式

### 方式 1: 配置文件（推荐）

编辑 `config/config.yaml`：

```yaml
ai:
  default_provider: "openrouter"  # 设置默认服务商
  
  providers:
    # OpenRouter 配置
    openrouter:
      enabled: true
      api_key_env: "OPENROUTER_API_KEY"
      model: "openai/gpt-4"  # 格式: provider/model-name
      timeout: 60
    
    # Together AI 配置
    together:
      enabled: true
      api_key_env: "TOGETHER_API_KEY"
      model: "meta-llama/Llama-2-70b-chat-hf"
      timeout: 60
    
    # Groq 配置
    groq:
      enabled: true
      api_key_env: "GROQ_API_KEY"
      model: "llama-3-70b-8192"
      timeout: 60
```

### 方式 2: 环境变量

设置相应的 API 密钥环境变量：

```bash
export OPENROUTER_API_KEY="your-api-key"
export TOGETHER_API_KEY="your-api-key"
export GROQ_API_KEY="your-api-key"
# ... 等等
```

### 方式 3: 命令行参数

```bash
# 使用 OpenRouter
bdfeasyinput ai plan "计算水分子的单点能" --provider openrouter --model "openai/gpt-4"

# 使用 Together AI
bdfeasyinput ai plan "优化苯分子" --provider together --model "meta-llama/Llama-2-70b-chat-hf"

# 使用 Groq
bdfeasyinput ai plan "频率计算" --provider groq --model "llama-3-70b-8192"
```

## 各服务商详细说明

### OpenRouter

**特点**：
- 统一访问多个模型提供商（OpenAI, Anthropic, Google, Meta 等）
- 按使用量付费
- 支持多种模型

**配置**：
```yaml
openrouter:
  enabled: true
  api_key_env: "OPENROUTER_API_KEY"
  model: "openai/gpt-4"  # 或 "anthropic/claude-3-sonnet", "google/gemini-pro" 等
```

**可用模型示例**：
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-sonnet`
- `anthropic/claude-3-opus`
- `google/gemini-pro`
- `meta-llama/llama-2-70b-chat-hf`

**获取 API 密钥**：https://openrouter.ai/

### Together AI

**特点**：
- 专注于开源模型
- 价格相对较低
- 支持多种开源模型

**配置**：
```yaml
together:
  enabled: true
  api_key_env: "TOGETHER_API_KEY"
  model: "meta-llama/Llama-2-70b-chat-hf"
```

**可用模型示例**：
- `meta-llama/Llama-2-70b-chat-hf`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`

**获取 API 密钥**：https://together.ai/

### Groq

**特点**：
- 极快的推理速度
- 支持 Llama 系列模型
- 免费额度

**配置**：
```yaml
groq:
  enabled: true
  api_key_env: "GROQ_API_KEY"
  model: "llama-3-70b-8192"
```

**可用模型示例**：
- `llama-3-70b-8192`
- `llama-3-8b-8192`
- `mixtral-8x7b-32768`

**获取 API 密钥**：https://console.groq.com/

### DeepSeek

**特点**：
- 中文支持优秀
- 价格合理
- 支持长上下文

**配置**：
```yaml
deepseek:
  enabled: true
  api_key_env: "DEEPSEEK_API_KEY"
  model: "deepseek-chat"
```

**获取 API 密钥**：https://platform.deepseek.com/

### Mistral AI

**特点**：
- 欧洲 AI 公司
- 高质量模型
- 支持多种语言

**配置**：
```yaml
mistral:
  enabled: true
  api_key_env: "MISTRAL_API_KEY"
  model: "mistral-large-latest"
```

**获取 API 密钥**：https://console.mistral.ai/

### Perplexity

**特点**：
- 实时信息检索
- 适合需要最新信息的任务
- 在线模型

**配置**：
```yaml
perplexity:
  enabled: true
  api_key_env: "PERPLEXITY_API_KEY"
  model: "pplx-70b-online"
```

**获取 API 密钥**：https://www.perplexity.ai/

## 使用示例

### Python API

```python
from bdfeasyinput.ai.client import OpenRouterClient, create_openai_compatible_client
from bdfeasyinput.ai import TaskPlanner

# 方式 1: 使用 OpenRouterClient
client = OpenRouterClient(
    model="openai/gpt-4",
    api_key="your-api-key"
)

# 方式 2: 使用通用工厂函数
client = create_openai_compatible_client(
    service="openrouter",
    model="openai/gpt-4"
)

# 使用
planner = TaskPlanner(ai_client=client)
config = planner.plan("计算水分子的单点能")
```

### 命令行使用

```bash
# 使用 OpenRouter
bdfeasyinput ai plan "计算水分子的单点能" \
  --provider openrouter \
  --model "openai/gpt-4"

# 使用 Together AI
bdfeasyinput ai plan "优化苯分子" \
  --provider together \
  --model "meta-llama/Llama-2-70b-chat-hf"

# 使用 Groq（快速推理）
bdfeasyinput ai plan "频率计算" \
  --provider groq \
  --model "llama-3-70b-8192"
```

### 完整工作流

```bash
# 使用 OpenRouter 进行完整工作流
export OPENROUTER_API_KEY="your-api-key"
bdfeasyinput workflow "计算水分子的单点能" \
  --provider openrouter \
  --model "openai/gpt-4" \
  --run \
  --analyze \
  -o ./results
```

## 自定义服务商

如果您的服务商使用 OpenAI 兼容的 API，可以通过配置文件自定义：

```yaml
providers:
  custom_service:
    enabled: true
    api_key_env: "CUSTOM_API_KEY"
    base_url: "https://api.custom-service.com/v1"  # 自定义 base URL
    model: "custom-model-name"
    timeout: 60
```

然后在代码中使用：

```python
from bdfeasyinput.ai.client import create_openai_compatible_client

client = create_openai_compatible_client(
    service="custom_service",
    model="custom-model",
    base_url="https://api.custom-service.com/v1",
    api_key="your-api-key"
)
```

## 注意事项

1. **API 密钥安全**：不要将 API 密钥提交到版本控制系统，使用环境变量或配置文件（已添加到 .gitignore）

2. **费用控制**：不同服务商的定价不同，注意控制使用量

3. **模型选择**：不同模型适合不同任务，建议根据需求选择合适的模型

4. **网络要求**：云端 API 需要网络连接，确保网络畅通

5. **速率限制**：注意各服务商的 API 速率限制

## 故障排除

### 问题：API 密钥未设置

**解决方案**：
```bash
export OPENROUTER_API_KEY="your-api-key"
```

### 问题：模型不存在

**解决方案**：检查模型名称是否正确，参考各服务商的文档

### 问题：超时错误

**解决方案**：增加 timeout 配置
```yaml
providers:
  openrouter:
    timeout: 120  # 增加到 120 秒
```

## 更多信息

- [OpenRouter 文档](https://openrouter.ai/docs)
- [Together AI 文档](https://docs.together.ai/)
- [Groq 文档](https://console.groq.com/docs)
- [DeepSeek 文档](https://platform.deepseek.com/api-docs)
- [Mistral AI 文档](https://docs.mistral.ai/)
- [Perplexity 文档](https://docs.perplexity.ai/)

