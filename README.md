# BDFEasyInput

简化 BDF (Beijing Density Functional Package) 量子化学计算软件的输入生成工具，支持 AI 辅助任务规划。

## 项目简介

BDFEasyInput 旨在让用户通过简洁、直观的配置方式或自然语言描述计算任务，自动生成符合 BDF 规范的专家模式输入文件。

## 核心特性

- 📝 **简洁输入**：使用 YAML/JSON 格式，无需记忆复杂的 BDF 关键词
- 🤖 **AI 辅助规划**：通过自然语言描述，AI 自动规划计算任务并生成输入
- 🔄 **自动转换**：智能映射常用计算方法和基组到 BDF 格式
- ✅ **输入验证**：自动检查参数有效性和兼容性
- 🚀 **自动执行**：集成 BDFAutotest，自动运行 BDF 计算 ⭐ NEW
- 🔬 **AI 结果分析**：基于量子化学专家模式，AI 自动分析计算结果 ⭐ NEW
- 📊 **数据标准化**：标准化分析结果，支持 LLM 模型训练 ⭐ NEW
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

### 使用示例

#### 方式 1：AI 辅助（自然语言）

```bash
# 使用自然语言描述任务，AI 自动生成 YAML
bdfeasyinput ai-plan "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" -o task.yaml

# 然后转换为 BDF 输入
bdfeasyinput convert task.yaml -o bdf_input.inp
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
bdfeasyinput convert example.yaml -o bdf_input.inp
```

#### 方式 3：交互式 AI 对话

```bash
# 启动交互式对话
bdfeasyinput ai-chat

# AI 会引导您完成计算任务的规划
```

#### 方式 4：完整工作流（规划 + 执行 + 分析）⭐ NEW

```bash
# 完整工作流：从自然语言到分析报告
bdfeasyinput workflow "计算水分子的单点能，使用 PBE0 方法" \
  --run \
  --analyze \
  --output-dir ./results

# 只运行计算
bdfeasyinput run bdf_input.inp --output-dir ./results

# 只分析已有结果
bdfeasyinput analyze output.out --input bdf_input.inp
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
bdfeasyinput ai-plan "..." --provider ollama --model llama3
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
bdfeasyinput ai-plan "..." --provider openai --model gpt-4
```

详细配置请参考 [AI 使用示例](examples/ai_usage_example.md)

## 项目状态

🚧 **开发中** - 项目规划阶段

已完成：
- ✅ 项目规划文档
- ✅ AI 模块设计 ⭐ NEW
- ✅ 架构设计
- ✅ 示例输入文件

待实施：
- ⏳ 核心代码实现
- ⏳ AI 模块实现
- ⏳ BDF 输入格式研究
- ⏳ 方法/基组映射表

详细规划请参见：
- [项目规划](PROJECT_PLAN.md)
- [架构设计](ARCHITECTURE.md)
- [AI 模块设计](AI_MODULE_DESIGN.md) ⭐ NEW
- [实施路线图](IMPLEMENTATION_ROADMAP.md)

## 文档

- [项目规划文档](PROJECT_PLAN.md)
- [架构设计文档](ARCHITECTURE.md)
- [AI 模块设计](AI_MODULE_DESIGN.md) ⭐ NEW
- [快速开始指南](QUICKSTART.md)
- [实施路线图](IMPLEMENTATION_ROADMAP.md)
- [示例文件](examples/)

## 贡献

欢迎贡献代码、报告问题或提出建议！

## 许可证

[待定]

## 相关链接

- BDF 官方网站：[待补充]
- 项目文档：[待补充]
