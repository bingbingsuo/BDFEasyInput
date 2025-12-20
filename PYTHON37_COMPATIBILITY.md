# Python 3.7.4 兼容性说明

## 概述

BDFEasyInput 现在支持 Python 3.7.4 及更高版本。本文档说明如何在 Python 3.7.4 环境中安装和使用。

## 安装说明

### 方法 1：使用 Python 3.7 专用依赖文件（推荐）

```bash
# 安装核心依赖（Python 3.7 兼容版本）
pip install -r requirements-py37.txt

# 安装包
pip install -e .
```

### 方法 2：手动安装依赖

```bash
# 核心依赖
pip install "pyyaml>=6.0" "jinja2>=3.1.0" "requests>=2.28.0" "click>=8.0"

# Pydantic 1.x（Python 3.7 兼容）
pip install "pydantic>=1.10,<2.0"

# 类型提示扩展（用于 Literal 等类型）
pip install "typing-extensions>=4.0.0"

# 安装包
pip install -e .
```

## 主要兼容性调整

### 1. Pydantic 版本

- **Python 3.9+**: 可以使用 Pydantic 2.0
- **Python 3.7-3.8**: 需要使用 Pydantic 1.x（1.10+）

Pydantic 在 BDFEasyInput 中是可选的，默认不使用（`use_pydantic=False`）。如果不需要 Pydantic 验证功能，可以不安装。

### 2. typing.Literal

代码中已经添加了兼容性处理：
- Python 3.8+: 使用 `typing.Literal`
- Python 3.7: 优先使用 `typing_extensions.Literal`，如果未安装则回退到 `str`

建议安装 `typing-extensions` 以获得更好的类型提示支持。

### 3. 其他依赖

所有其他核心依赖（PyYAML, Jinja2, Click, Requests）都支持 Python 3.7.4。

## 已知限制

### AI 功能依赖

某些 AI 相关的可选依赖可能有更高的 Python 版本要求：

- **openai>=1.0.0**: 可能需要 Python 3.8+
- **anthropic>=0.3.0**: 请检查具体版本要求

如果使用 Python 3.7.4 且需要 AI 功能，可能需要：
1. 使用较低版本的这些库（如果可用）
2. 或使用其他 AI 提供商（如 Ollama，通常对 Python 版本要求较低）

### 开发和测试工具

某些开发和测试工具可能需要更高版本的 Python：
- **pytest>=7.0**: 支持 Python 3.7+
- **black>=23.0**: 可能需要 Python 3.8+
- **ruff>=0.1.0**: 可能需要 Python 3.8+

这些工具是可选的，不影响核心功能。

## 测试

在 Python 3.7.4 环境中测试：

```bash
# 检查 Python 版本
python --version  # 应该显示 Python 3.7.4 或更高

# 运行基本功能测试
python -m bdfeasyinput.cli convert examples/h2o_b3lyp.yaml -o test.inp

# 验证转换成功
cat test.inp
```

## 故障排除

### 问题 1: 导入错误 "cannot import name 'Literal' from 'typing'"

**解决方案**: 安装 `typing-extensions`:
```bash
pip install typing-extensions>=4.0.0
```

### 问题 2: Pydantic 安装失败

**解决方案**: 
- 如果不需要 Pydantic 验证功能，可以不安装（代码默认不使用）
- 如果需要，安装 Pydantic 1.x: `pip install "pydantic>=1.10,<2.0"`

### 问题 3: 某些 AI 库无法安装

**解决方案**: 
- 这些库是可选的，不影响核心转换和执行功能
- 可以只使用不需要这些库的功能
- 或考虑升级到 Python 3.8+ 以获得完整功能支持

## 版本要求总结

| 组件 | Python 3.7.4 | Python 3.8+ | 说明 |
|------|--------------|-------------|------|
| 核心功能 | ✅ | ✅ | 完全支持 |
| Pydantic 验证 | ✅ (1.x) | ✅ (2.0) | 可选功能 |
| typing.Literal | ✅ (需 typing-extensions) | ✅ | 已处理兼容性 |
| AI 功能 | ⚠️ (部分限制) | ✅ | 某些库可能需要更高版本 |

## 建议

- **新项目**: 建议使用 Python 3.8 或更高版本，以获得更好的依赖支持和性能
- **现有项目**: 如果必须使用 Python 3.7.4，按照本文档说明安装兼容版本的依赖即可
