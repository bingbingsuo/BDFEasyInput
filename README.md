# BDFEasyInput

简化 BDF (Beijing Density Functional Package) 量子化学计算软件的输入生成工具，支持 AI 辅助任务规划。

## 项目简介

BDFEasyInput 旨在让用户通过简洁、直观的配置方式或自然语言描述计算任务，自动生成符合 BDF 规范的专家模式输入文件。

## 核心特性

- 📝 **简洁输入**：使用 YAML/JSON 格式，无需记忆复杂的 BDF 关键词
- 🤖 **AI 辅助规划**：通过自然语言描述，AI 自动规划计算任务并生成输入
- 🔄 **自动转换**：智能映射常用计算方法和基组到 BDF 格式
- ✅ **输入验证**：自动检查参数有效性和兼容性
- 🚀 **自动执行**：集成 BDFAutotest，自动运行 BDF 计算
- 🔬 **AI 结果分析**：基于量子化学专家模式，AI 自动分析计算结果
- 💧 **激发态溶剂效应**：支持 cLR 和 ptSS 非平衡溶剂化校正 ⭐ NEW
- 📊 **完整工作流**：从任务规划到结果分析的一站式解决方案
- 🧪 **多种计算类型**：支持单点能、几何优化、频率计算等
- 🏠 **本地模型支持**：支持 Ollama 等本地模型，保护数据隐私
- 🔧 **易于扩展**：模块化设计，方便添加新功能
- 📊 **完整工作流**：从任务规划到结果分析的一站式解决方案 ⭐ NEW

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd BDFEasyInput

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

**注意**：安装后，请使用 `python -m bdfeasyinput.cli` 而不是 `bdfeasyinput` 命令（详见 [安装说明](INSTALL.md)）。

### 使用示例

#### 方式 1：AI 辅助（自然语言）

```bash
# 使用自然语言描述任务，AI 自动生成 YAML
python -m bdfeasyinput.cli ai-plan "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" -o task.yaml

# 然后转换为 BDF 输入
python -m bdfeasyinput.cli convert task.yaml -o bdf_input.inp
```

#### 方式 2：YAML 输入（传统方式）

```yaml
# example.yaml
task:
  type: energy

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 格式: ATOM X Y Z (单位: angstrom)
    - O  0.0000 0.0000 0.0000
    - H  0.9572 0.0000 0.0000
    - H -0.2398 0.9266 0.0000
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom

method:
  type: dft
  functional: pbe0
  basis: cc-pvdz
```

```bash
# 生成 BDF 输入文件
python -m bdfeasyinput.cli convert example.yaml -o bdf_input.inp
```

#### 方式 3：交互式 AI 对话

```bash
# 启动交互式对话
python -m bdfeasyinput.cli ai-chat

# AI 会引导您完成计算任务的规划
```

#### 方式 4：完整工作流（规划 + 执行 + 分析）⭐ NEW

```bash
# 完整工作流：从自然语言到分析报告
python -m bdfeasyinput.cli workflow "计算水分子的单点能，使用 PBE0 方法" \
  --run \
  --analyze \
  --output-dir ./results

# 只运行计算
python -m bdfeasyinput.cli run bdf_input.inp --output-dir ./results

# 只分析已有结果
python -m bdfeasyinput.cli analyze output.out --input bdf_input.inp
```

## AI 功能配置

### 使用本地模型（推荐）

1. 安装并启动 Ollama：
```bash
# 安装 Ollama (参考 https://ollama.ai)
# 下载模型
ollama pull llama3
```

2. 配置使用本地模型：
```bash
python -m bdfeasyinput.cli ai-plan "..." --provider ollama --model llama3
```

### 使用远程 API

设置环境变量：
```bash
export OPENAI_API_KEY=your_key_here
# 或
export ANTHROPIC_API_KEY=your_key_here
```

然后使用：
```bash
python -m bdfeasyinput.cli ai-plan "..." --provider openai --model gpt-4
```

详细配置请参考 [AI 使用示例](examples/ai_usage_example.md)

## 项目状态

✅ **核心功能已完成** - 支持完整的 BDF 计算工作流

### ✅ 已完成功能

#### 核心功能
- ✅ **YAML 到 BDF 转换器**：完整的转换引擎
  - SCF 单点能量计算（RHF, UHF, RKS, UKS, ROKS）
  - TDDFT 激发态计算（单态、三态、SOC、Spin-flip）
  - 结构优化（基态、激发态）
  - 频率计算（Hessian）
  - **溶剂化效应支持**：
    - 基态溶剂化（IEFPCM, COSMO, CPCM, SMD 等）
    - **激发态非平衡溶剂化** ⭐ NEW
      - cLR（线性响应非平衡溶剂化）
      - ptSS（态特定微扰理论非平衡溶剂化）
- ✅ **执行模块**：支持直接执行和 BDFAutotest 模式
- ✅ **分析模块**：完整的输出解析和 AI 分析
  - 能量、几何结构、频率提取
  - SCF 收敛分析
  - TDDFT 激发态分析
  - **溶剂效应分析**（含非平衡校正）⭐ NEW
  - 多格式报告生成（Markdown, HTML, Text）
  - 中英文双语支持
- ✅ **AI 模块**：任务规划和结果分析
  - 9 个 AI 服务商支持（Ollama, OpenAI, Anthropic, OpenRouter 等）
  - 自然语言任务规划
  - 专家级结果分析

#### 文档系统
- ✅ 完整的项目文档（43+ 文档文件）
- ✅ 开发文档（位于 `docs/dev/`）
- ✅ 用户指南和示例

### 📊 项目统计

- **代码文件**：46+ Python 文件
- **测试文件**：15+ 测试文件
- **示例文件**：24+ 示例
- **支持的计算类型**：5+ 种
- **支持的 AI 服务商**：9 个

**详细进度**：参见 [docs/dev/CURRENT_STATUS_2025.md](docs/dev/CURRENT_STATUS_2025.md)

## 文档

### 用户文档
- **[完整使用手册](docs/USER_MANUAL.md)** ⭐ 推荐阅读
- [AI 提供商指南](docs/ai_providers_guide.md)
- [坐标格式说明](docs/coordinate_format.md)
- [用户指南大纲](docs/user_guide_outline.md)

### 开发文档（docs/dev/）
- [当前状态总结](docs/dev/CURRENT_STATUS_2025.md) ⭐ NEW
- [项目规划](docs/dev/PROJECT_PLAN.md)
- [架构设计](docs/dev/ARCHITECTURE.md)
- [AI 模块设计](docs/dev/AI_MODULE_DESIGN.md)
- [实施路线图](docs/dev/IMPLEMENTATION_ROADMAP.md)
- [快速开始指南](docs/dev/QUICKSTART.md)
- [功能总结](docs/dev/FEATURES_SUMMARY.md)
- [示例文件](examples/)

## 贡献

欢迎贡献代码、报告问题或提出建议！

## 许可证

[待定]

## 相关链接

- BDF 官方网站：[待补充]
- 项目文档：[待补充]
