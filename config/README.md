# BDFEasyInput 配置文件说明

## 📁 配置文件

### 全局配置文件

**`config.yaml`** - 主配置文件，包含所有设置

这是 BDFEasyInput 的主要配置文件，包含：
- **执行配置**：BDF 计算执行相关设置
- **AI 配置**：AI 模块相关设置
- **分析配置**：结果分析相关设置

### 配置文件位置

默认配置文件路径：`config/config.yaml`

可以通过环境变量 `BDFEASYINPUT_CONFIG` 指定其他路径。

## 🚀 快速开始

### 1. 创建配置文件

```bash
# 复制示例文件
cp config/config.yaml.example config/config.yaml

# 编辑配置文件
vim config/config.yaml
```

### 2. 最小配置示例

对于只想快速开始使用的用户，最小配置如下：

```yaml
execution:
  type: direct
  direct:
    bdf_home: "/path/to/bdf"  # 只需设置 BDF 安装路径

ai:
  enabled: true
  default_provider: "ollama"
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"

analysis:
  enabled: true
```

## 📝 配置说明

### 执行配置 (execution)

#### 直接执行模式（推荐）

```yaml
execution:
  type: direct
  direct:
    bdf_home: "/path/to/bdf"           # 必需
    bdf_tmpdir: "/tmp/$RANDOM"          # 可选，默认 "/tmp/$RANDOM"
    omp_num_threads: 8                  # 可选，null 表示自动
    omp_stacksize: "512M"                # 可选
```

#### BDFAutotest 模式

```yaml
execution:
  type: bdfautotest
  bdfautotest:
    path: "/path/to/BDFAutoTest"        # 必需
    config_file: null                   # 可选
```

### AI 配置 (ai)

#### 基本配置

```yaml
ai:
  enabled: true
  default_provider: "ollama"
  
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"
```

#### 使用 OpenAI

```yaml
ai:
  default_provider: "openai"
  providers:
    openai:
      enabled: true
      api_key_env: "OPENAI_API_KEY"  # 从环境变量读取
      model: "gpt-4"
```

**注意**：需要设置环境变量：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 分析配置 (analysis)

#### 基本配置

```yaml
analysis:
  enabled: true
  output:
    format: "markdown"
    include_recommendations: true
  expert_mode:
    enabled: true
    depth: "detailed"
```

## 🔧 环境变量

可以通过环境变量覆盖某些配置：

| 环境变量 | 说明 |
|---------|------|
| `BDFEASYINPUT_CONFIG` | 配置文件路径 |
| `BDFHOME` | BDF 安装目录（覆盖 `execution.direct.bdf_home`） |
| `BDFAUTOTEST_PATH` | BDFAutotest 路径（覆盖 `execution.bdfautotest.path`） |
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |

## 📚 更多信息

- 详细配置说明：查看 `config.yaml.example` 中的注释
- 执行模式说明：`EXECUTION_DIRECT_MODE.md`
- AI 模块说明：`AI_MODULE_DESIGN.md`
- 分析模块说明：`EXECUTION_AND_ANALYSIS_DESIGN.md`

