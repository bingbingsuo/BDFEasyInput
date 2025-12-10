# OpenRouter 配置测试指南

## 前置要求

### 1. 安装依赖

OpenRouter 使用 OpenAI 兼容的 API，需要安装 `openai` 包：

```bash
pip install openai>=1.0.0
```

**注意**：如果您的 Python 版本 < 3.8，可能需要使用较旧版本的 openai：
```bash
pip install "openai<1.0.0"
```

### 2. 设置 API 密钥

根据您的配置，OpenRouter 使用 `OPENAI_API_KEY` 环境变量：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

或者，如果您想使用 `OPENROUTER_API_KEY`：
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

然后修改 `config.yaml` 中的 `api_key_env` 为 `"OPENROUTER_API_KEY"`。

### 3. 启用 OpenRouter

确保 `config/config.yaml` 中：

```yaml
ai:
  default_provider: "openrouter"
  providers:
    openrouter:
      enabled: true
      api_key_env: "OPENAI_API_KEY"  # 或 "OPENROUTER_API_KEY"
      model: "openai/gpt-oss-120b:free"
```

## 测试方法

### 方法 1: 使用测试脚本

```bash
python test_openrouter.py
```

### 方法 2: 使用 CLI 命令

#### 测试 1: 简单规划

```bash
bdfeasyinput ai plan "计算水分子的单点能" -o test_task.yaml
```

#### 测试 2: 指定提供商

```bash
bdfeasyinput ai plan "计算水分子的单点能" \
  --provider openrouter \
  --model "openai/gpt-oss-120b:free" \
  -o test_task.yaml
```

#### 测试 3: 交互式对话

```bash
bdfeasyinput ai chat
```

### 方法 3: Python API

```python
from bdfeasyinput.config import load_config, merge_config_with_defaults
from bdfeasyinput.cli import get_ai_client_from_config
from bdfeasyinput.ai import TaskPlanner

# 从配置创建客户端
client = get_ai_client_from_config()

# 创建规划器
planner = TaskPlanner(ai_client=client)

# 规划任务
task_config = planner.plan("计算水分子的单点能，使用 PBE0 方法")
print(task_config)
```

## 常见问题

### 问题 1: "OpenAI package is not installed"

**解决方案**：
```bash
pip install openai>=1.0.0
```

如果 Python 版本 < 3.8：
```bash
pip install "openai<1.0.0"
```

### 问题 2: "API key not set"

**解决方案**：
```bash
export OPENAI_API_KEY="your-api-key"
# 或
export OPENROUTER_API_KEY="your-api-key"
```

### 问题 3: "Provider 'openrouter' is disabled"

**解决方案**：
在 `config/config.yaml` 中设置：
```yaml
providers:
  openrouter:
    enabled: true
```

### 问题 4: 模型不存在或不可用

**解决方案**：
- 检查模型名称是否正确
- 访问 https://openrouter.ai/models 查看可用模型
- 尝试其他模型，如 `"openai/gpt-4"` 或 `"anthropic/claude-3-sonnet"`

## 验证配置

运行以下命令验证配置：

```bash
# 检查配置加载
python -c "
from bdfeasyinput.config import load_config, get_ai_config
config = load_config()
ai_config = get_ai_config(config)
print('Default provider:', ai_config.get('default_provider'))
print('OpenRouter enabled:', ai_config.get('providers', {}).get('openrouter', {}).get('enabled'))
"

# 检查 API key
python -c "
import os
api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
if api_key:
    print('API Key found:', api_key[:10] + '...')
else:
    print('API Key not found')
"
```

## 下一步

配置成功后，您可以：

1. 使用 AI 规划任务：
   ```bash
   bdfeasyinput ai plan "您的计算任务描述"
   ```

2. 使用完整工作流：
   ```bash
   bdfeasyinput workflow "您的计算任务" --run --analyze
   ```

3. 查看 [AI 服务商使用指南](docs/ai_providers_guide.md) 了解更多选项

