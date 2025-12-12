# BDFEasyInput 安装说明

## 快速安装

```bash
# 1. 克隆或进入项目目录
cd BDFEasyInput

# 2. 安装包（开发模式）
pip install -e .

# 3. 安装核心依赖
pip install pyyaml click requests

# 4. 可选：安装 AI 相关依赖
pip install openai anthropic  # 根据需要选择

# 5. 验证安装
python3 -m bdfeasyinput.cli --help
```

## 命令找不到的问题

如果安装后 `bdfeasyinput` 命令找不到，请检查：

### 1. 检查命令是否已安装

```bash
# 查找命令脚本位置
find ~/Library/Python -name "bdfeasyinput" 2>/dev/null
# 或
python3 -m pip show -f bdfeasyinput | grep -A 5 "Files:"
```

### 2. 添加到 PATH

如果命令安装在 `~/Library/Python/3.7/bin/`，需要将其添加到 PATH：

**临时添加（当前终端会话）：**
```bash
export PATH="$HOME/Library/Python/3.7/bin:$PATH"
```

**永久添加（推荐）：**
将以下行添加到 `~/.bashrc` 或 `~/.zshrc`：
```bash
export PATH="$HOME/Library/Python/3.7/bin:$PATH"
```

然后重新加载配置：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

### 3. 使用 Python 模块方式运行

如果 PATH 配置不方便，可以直接使用 Python 模块方式：

```bash
# 替代 bdfeasyinput convert
python3 -m bdfeasyinput.cli convert input.yaml -o output.inp

# 替代 bdfeasyinput run
python3 -m bdfeasyinput.cli run input.inp

# 替代 bdfeasyinput analyze
python3 -m bdfeasyinput.cli analyze output.log
```

### 4. 创建别名（可选）

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
alias bdfeasyinput='python3 -m bdfeasyinput.cli'
```

## 依赖说明

### 必需依赖
- `pyyaml` - YAML 文件解析
- `click` - 命令行界面
- `requests` - HTTP 请求（用于 AI 客户端）

### 可选依赖
- `openai` - OpenAI API 支持
- `anthropic` - Anthropic Claude API 支持
- `ollama` - Ollama 本地模型支持（用户自行安装）
- `pydantic` - 数据验证（如果使用验证功能）
- `pandas` - 数据导出（如果使用 Parquet 格式）

## 验证安装

```bash
# 方法 1：使用命令（需要 PATH 配置）
bdfeasyinput --help

# 方法 2：使用 Python 模块（推荐）
python3 -m bdfeasyinput.cli --help
```

## 常见问题

### Q: 安装时提示缺少 ollama 包
A: ollama 是可选依赖，可以忽略。如果需要使用 Ollama，请单独安装：
```bash
pip install ollama
```

### Q: 命令脚本存在但无法运行
A: 检查依赖是否完整安装，特别是核心依赖：
```bash
pip install pyyaml click requests
```

### Q: Python 版本问题
A: BDFEasyInput 支持 Python 3.7+，但某些依赖可能需要更高版本。建议使用 Python 3.8+。
