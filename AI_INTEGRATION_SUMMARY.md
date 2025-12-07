# AI 功能集成总结

## 🎯 新增功能概述

BDFEasyInput 现在支持 **AI 辅助任务规划**功能，用户可以通过自然语言描述计算需求，AI 自动规划任务并生成 YAML 输入文件。

## ✨ 核心特性

1. **自然语言输入**：用自然语言描述计算需求，无需编写 YAML
2. **智能规划**：AI 理解用户意图，自动规划计算任务
3. **自动生成 YAML**：AI 生成符合规范的 YAML 输入文件
4. **参数推荐**：自动推荐合适的方法和基组
5. **交互式对话**：支持多轮对话完善计算任务

## 🏗️ 架构变化

### 新增模块结构

```
bdfeasyinput/
├── ai/                    # ⭐ NEW AI 模块
│   ├── client/           # AI 客户端
│   │   ├── base.py
│   │   ├── ollama.py     # 本地模型
│   │   ├── openai.py     # OpenAI API
│   │   └── anthropic.py  # Anthropic API
│   ├── planner/          # 任务规划器
│   │   ├── task_planner.py
│   │   └── method_recommender.py
│   ├── prompt/           # 提示词模板
│   │   └── templates.py
│   └── parser/           # AI 输出解析
│       └── response_parser.py
```

### 更新的架构流程

```
用户自然语言输入
    ↓
[AI 规划层] ⭐ NEW
  • 理解用户意图
  • 规划计算任务
  • 生成 YAML
    ↓
[输入解析层]
    ↓
[验证层]
    ↓
[转换层]
    ↓
[生成层]
    ↓
BDF 输入文件
```

## 📚 新增文档

1. **[AI_MODULE_DESIGN.md](AI_MODULE_DESIGN.md)** - 详细的 AI 模块设计文档
2. **[examples/ai_usage_example.md](examples/ai_usage_example.md)** - AI 功能使用示例
3. **[config/ai_config.example.yaml](config/ai_config.example.yaml)** - AI 配置示例

## 🔧 技术栈更新

### 新增依赖

```txt
# AI 功能依赖（可选）
openai>=1.0.0          # OpenAI API 支持
anthropic>=0.3.0       # Anthropic Claude API 支持
ollama>=0.1.0          # Ollama 本地模型支持
```

### 支持模型

- **本地模型**（推荐）：
  - Ollama (llama3, llama2, mistral 等)
  - vLLM 服务
  - 其他本地部署的模型

- **远程 API**：
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude 3)

## 📖 使用方式

### 1. 命令行使用

```bash
# AI 规划任务
bdfeasyinput ai plan "计算水分子的单点能，使用 PBE0 方法" -o task.yaml

# 流式规划输出
bdfeasyinput ai plan "..." --stream -o task.yaml

# 交互式对话（默认流式）
bdfeasyinput ai chat --stream

# 指定 AI 提供商
bdfeasyinput ai plan "..." --provider ollama --model llama3
```

### 2. Python API

```python
from bdfeasyinput.ai import TaskPlanner
from bdfeasyinput.ai.client import OllamaClient

client = OllamaClient(model_name="llama3")
planner = TaskPlanner(ai_client=client)

task_config = planner.plan(
    "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
)
```

## 🎯 使用场景

### 场景 1：完整描述
```
用户: "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组"
AI: 生成完整 YAML
```

### 场景 2：简化描述
```
用户: "帮我优化苯分子的几何结构"
AI: 自动补充推荐方法和基组，生成完整 YAML
```

### 场景 3：交互式对话
```
用户: "我想计算一个过渡金属配合物"
AI: "请问您要计算什么性质？"
用户: "几何优化"
AI: "好的，我建议使用 PBE0 泛函和 def2-TZVP 基组..."
```

## 🔐 隐私和安全

### 本地模型（推荐）
- ✅ 数据不离开本地
- ✅ 适合敏感研究
- ✅ 无 API 调用费用

### 远程 API
- ⚠️ 数据发送到远程服务
- ✅ 明确的用户提示
- ✅ 支持数据脱敏

## 📅 开发计划

### 阶段 2（完成）
- [x] AI 模块设计文档
- [x] AI 客户端接口
- [x] Ollama 客户端实现
- [x] 基础提示词模板

### 阶段 3（进行中）
- [x] 完整任务规划器（含重试与流式）
- [x] YAML 生成和验证（保存前校验与警告）
- [x] 交互式对话（支持流式输出）
- [x] 方法推荐器（规则与推荐文本）
- [ ] 提示词优化（持续迭代）

## 🔄 与现有功能的关系

AI 功能是**可选的增强功能**：
- ✅ 不影响现有的 YAML/JSON 输入方式
- ✅ 可以与传统输入方式混合使用
- ✅ AI 生成 YAML 后，走相同的验证和转换流程

## 🎓 示例工作流

### 完整流程

```
1. 用户自然语言描述
   "计算水分子的单点能"

2. AI 规划并生成 YAML
   ↓
3. 验证 YAML（可选）
   ↓
4. 转换为 BDF 输入
   ↓
5. 生成 BDF 输入文件
```

### 混合使用

```
1. AI 生成基础 YAML
   ↓
2. 用户手动编辑优化
   ↓
3. 转换为 BDF 输入
```

## 📝 配置示例

```yaml
# config/ai_config.yaml
ai:
  default_provider: "ollama"
  
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"
```

## 🚀 下一步

1. **实施 AI 客户端接口**
2. **实现任务规划器**
3. **优化提示词**
4. **完善文档和示例**

## 📌 注意事项

1. AI 功能是可选的，需要安装额外依赖
2. 本地模型需要先安装和启动（如 Ollama）
3. 远程 API 需要配置 API 密钥
4. AI 生成的 YAML 会自动验证；交互保存前进行校验，如有错误阻止保存

---

**AI 功能将大大提升用户体验，让非专家用户也能轻松使用 BDF 进行量子化学计算！** 🎉
