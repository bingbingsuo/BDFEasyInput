# OpenAI 兼容服务商支持

## 📋 概述

BDFEasyInput 现在支持多个 OpenAI 兼容的 AI 服务商，包括 OpenRouter、Together AI、Groq、DeepSeek、Mistral AI 和 Perplexity。这些服务商使用 OpenAI 兼容的 API，可以无缝集成到现有工作流中。

## ✨ 新增功能

### 1. OpenRouter 客户端

**文件**: `bdfeasyinput/ai/client/openrouter_client.py`

- 专门的 OpenRouter 客户端类
- 继承自 OpenAIClient，使用 OpenRouter 的 API 端点
- 支持 OpenRouter 的模型格式（`provider/model-name`）

### 2. OpenAI 兼容客户端工厂

**文件**: `bdfeasyinput/ai/client/openai_compatible.py`

- `create_openai_compatible_client()` - 通用工厂函数
- 预定义服务配置（OpenRouter, Together, Groq, DeepSeek, Mistral, Perplexity）
- 支持自定义服务商

### 3. 配置文件更新

**文件**: `config/config.yaml`

新增了以下服务商配置：
- `openrouter` - OpenRouter 配置
- `together` - Together AI 配置
- `groq` - Groq 配置
- `deepseek` - DeepSeek 配置
- `mistral` - Mistral AI 配置
- `perplexity` - Perplexity 配置

### 4. CLI 更新

**文件**: `bdfeasyinput/cli.py`

- 更新了 `get_ai_client_from_config()` 函数以支持新服务商
- 更新了所有 CLI 命令的 `--provider` 选项
- 支持的命令：`ai plan`, `ai chat`, `workflow`

## 🚀 快速开始

### 1. 设置 API 密钥

```bash
export OPENROUTER_API_KEY="your-api-key"
export TOGETHER_API_KEY="your-api-key"
export GROQ_API_KEY="your-api-key"
# ... 等等
```

### 2. 配置服务商

编辑 `config/config.yaml`：

```yaml
ai:
  default_provider: "openrouter"
  
  providers:
    openrouter:
      enabled: true
      api_key_env: "OPENROUTER_API_KEY"
      model: "openai/gpt-4"
```

### 3. 使用

```bash
# 命令行
bdfeasyinput ai plan "计算水分子的单点能" --provider openrouter

# Python API
from bdfeasyinput.ai.client import OpenRouterClient
client = OpenRouterClient(model="openai/gpt-4")
```

## 📚 支持的服务商

| 服务商 | 特点 | 模型示例 |
|--------|------|----------|
| **OpenRouter** | 统一访问多个模型提供商 | `openai/gpt-4`, `anthropic/claude-3-sonnet` |
| **Together AI** | 开源模型 API | `meta-llama/Llama-2-70b-chat-hf` |
| **Groq** | 极快推理速度 | `llama-3-70b-8192` |
| **DeepSeek** | 优秀中文支持 | `deepseek-chat` |
| **Mistral AI** | 高质量欧洲模型 | `mistral-large-latest` |
| **Perplexity** | 实时信息检索 | `pplx-70b-online` |

## 🔧 技术实现

### 架构设计

1. **OpenRouterClient** - 专门的 OpenRouter 客户端
   - 继承自 `OpenAIClient`
   - 使用 OpenRouter 的默认 base URL
   - 支持 OpenRouter 的模型命名格式

2. **create_openai_compatible_client()** - 通用工厂函数
   - 支持预定义服务商
   - 支持自定义服务商
   - 自动处理 API 密钥和环境变量

3. **配置系统集成**
   - 统一的配置格式
   - 环境变量支持
   - 命令行参数覆盖

### 代码结构

```
bdfeasyinput/ai/client/
├── base.py                    # 基础接口
├── openai_client.py           # OpenAI 客户端（已存在）
├── openrouter_client.py      # ⭐ NEW OpenRouter 客户端
└── openai_compatible.py      # ⭐ NEW 兼容客户端工厂
```

## 📖 使用示例

### 示例 1: 使用 OpenRouter

```python
from bdfeasyinput.ai.client import OpenRouterClient
from bdfeasyinput.ai import TaskPlanner

client = OpenRouterClient(
    model="openai/gpt-4",
    api_key="your-api-key"
)

planner = TaskPlanner(ai_client=client)
config = planner.plan("计算水分子的单点能")
```

### 示例 2: 使用通用工厂函数

```python
from bdfeasyinput.ai.client import create_openai_compatible_client

# OpenRouter
client = create_openai_compatible_client(
    service="openrouter",
    model="openai/gpt-4"
)

# Together AI
client = create_openai_compatible_client(
    service="together",
    model="meta-llama/Llama-2-70b-chat-hf"
)

# 自定义服务
client = create_openai_compatible_client(
    service="custom",
    model="custom-model",
    base_url="https://api.custom.com/v1",
    api_key="custom-key"
)
```

### 示例 3: 命令行使用

```bash
# OpenRouter
bdfeasyinput ai plan "计算水分子的单点能" \
  --provider openrouter \
  --model "openai/gpt-4"

# Together AI
bdfeasyinput ai plan "优化苯分子" \
  --provider together \
  --model "meta-llama/Llama-2-70b-chat-hf"

# Groq（快速推理）
bdfeasyinput ai plan "频率计算" \
  --provider groq \
  --model "llama-3-70b-8192"
```

## 🔄 向后兼容性

- ✅ 完全向后兼容现有代码
- ✅ 现有配置继续有效
- ✅ 默认行为不变（仍使用 Ollama 作为默认）

## 📝 配置示例

### 完整配置示例

```yaml
ai:
  default_provider: "openrouter"
  
  providers:
    # OpenRouter
    openrouter:
      enabled: true
      api_key_env: "OPENROUTER_API_KEY"
      base_url: "https://openrouter.ai/api/v1"
      model: "openai/gpt-4"
      timeout: 60
    
    # Together AI
    together:
      enabled: false
      api_key_env: "TOGETHER_API_KEY"
      model: "meta-llama/Llama-2-70b-chat-hf"
      timeout: 60
    
    # Groq
    groq:
      enabled: false
      api_key_env: "GROQ_API_KEY"
      model: "llama-3-70b-8192"
      timeout: 60
```

## 🎯 优势

1. **更多选择** - 用户可以根据需求选择最适合的服务商
2. **成本优化** - 不同服务商定价不同，可以选择性价比更高的
3. **性能优化** - 不同服务商在不同任务上表现不同
4. **灵活性** - 支持自定义服务商，易于扩展

## 📚 相关文档

- [AI 服务商使用指南](docs/ai_providers_guide.md) - 详细使用说明
- [配置文件说明](config/README.md) - 配置选项说明

## 🔮 未来计划

- [ ] 添加更多服务商支持
- [ ] 服务商性能对比工具
- [ ] 自动选择最佳服务商
- [ ] 成本跟踪功能

---

**最后更新**: 2025年1月

