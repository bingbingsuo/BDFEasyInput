# BDFEasyInput 用户使用手册

## 目录

1. [简介](#1-简介)
2. [安装与配置](#2-安装与配置)
3. [命令行接口](#3-命令行接口)
4. [YAML 输入格式](#4-yaml-输入格式)
5. [计算类型详解](#5-计算类型详解)
6. [AI 辅助功能](#6-ai-辅助功能)
7. [高级特性](#7-高级特性)
8. [结果分析](#8-结果分析)
9. [故障排除](#9-故障排除)
10. [常见问题](#10-常见问题)

---

## 1. 简介

### 1.1 什么是 BDFEasyInput

BDFEasyInput 是一个用于简化 BDF (Beijing Density Functional Package) 量子化学计算软件输入生成的工具。它提供了：

- **简洁的 YAML/JSON 配置格式**：无需记忆复杂的 BDF 关键词
- **AI 辅助任务规划**：通过自然语言描述自动生成计算输入
- **自动转换**：智能映射常用方法和基组到 BDF 格式
- **自动执行**：集成 BDF 执行引擎，支持直接执行和 BDFAutotest 模式
- **AI 结果分析**：基于量子化学专家知识自动分析计算结果
- **完整工作流**：从任务规划到结果分析的一站式解决方案

### 1.2 核心特性

- ✅ **多种计算类型**：单点能、几何优化、频率计算、TDDFT 激发态
- ✅ **多种电子结构方法**：HF、DFT (B3LYP, PBE0, M06-2X 等)、TDDFT
- ✅ **溶剂化效应**：支持 IEFPCM、COSMO、CPCM、SMD 等，包括激发态非平衡溶剂化（cLR、ptSS）
- ✅ **AI 集成**：支持 9 个 AI 服务商（Ollama、OpenAI、Anthropic、OpenRouter 等）
- ✅ **双语支持**：中文和英文报告生成
- ✅ **模块化设计**：易于扩展和维护

---

## 2. 安装与配置

### 2.1 系统要求

- Python 3.7 或更高版本
- BDF 软件已安装并配置（如果需要进行计算）

### 2.2 安装步骤

```bash
# 1. 克隆或进入项目目录
cd BDFEasyInput

# 2. 安装包（开发模式）
pip install -e .

# 3. 安装核心依赖
pip install pyyaml click requests

# 4. 可选：安装 AI 相关依赖
pip install openai anthropic  # 根据需要选择
```

**注意**：安装后请使用 `python -m bdfeasyinput.cli` 而不是 `bdfeasyinput` 命令（详见 [INSTALL.md](../INSTALL.md)）。

### 2.3 验证安装

```bash
python3 -m bdfeasyinput.cli --help
```

应该看到类似以下输出：

```
Usage: python -m bdfeasyinput.cli [OPTIONS] COMMAND [ARGS]...

  BDFEasyInput - Easy input generator for BDF quantum chemistry software.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  ai        AI-powered task planning commands.
  analyze   Analyze BDF calculation results using AI.
  convert   Convert YAML input file to BDF input format.
  run       Run BDF calculation from input file.
  workflow  Complete workflow: plan → convert → run → analyze.
```

### 2.4 配置文件

配置文件位于 `config/config.yaml`，包含以下主要配置：

#### 执行配置

```yaml
execution:
  type: bdfautotest  # 或 'direct'
  
  # 直接执行模式
  direct:
    bdf_home: "/path/to/bdf"
    bdf_tmpdir: "/tmp/$RANDOM"
    omp_num_threads: 4
  
  # BDFAutotest 模式
  bdfautotest:
    path: "/path/to/BDFAutoTest"
    config_file: null
  
  timeout: 3600  # 超时时间（秒）
```

#### AI 配置

```yaml
ai:
  enabled: true
  default_provider: "ollama"
  
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"
      timeout: 180
    
    openai:
      enabled: false
      api_key_env: "OPENAI_API_KEY"
      model: "gpt-4"
```

#### 分析配置

```yaml
analysis:
  ai:
    enabled: true
    language: "zh"  # 或 "en"
    provider: "ollama"
```

详细配置说明请参考 `config/config.yaml.example`。

---

## 3. 命令行接口

### 3.1 基本命令结构

所有命令使用以下格式：

```bash
python -m bdfeasyinput.cli <command> [options] [arguments]
```

### 3.2 主要命令

#### `convert` - 转换 YAML 为 BDF 输入

将 YAML 配置文件转换为 BDF 输入文件。

```bash
python -m bdfeasyinput.cli convert <input_file> [-o OUTPUT] [-c CONFIG]
```

**参数：**
- `input_file`：输入的 YAML 文件路径（必需）
- `-o, --output`：输出的 BDF 输入文件路径（可选，默认输出到标准输出）
- `-c, --config`：配置文件路径（可选）

**示例：**

```bash
python -m bdfeasyinput.cli convert task.yaml -o bdf_input.inp
```

#### `ai plan` - AI 辅助任务规划

使用自然语言描述生成 YAML 配置文件。

```bash
python -m bdfeasyinput.cli ai plan [QUERY] [-o OUTPUT] [--provider PROVIDER] [--model MODEL] [--stream]
```

**参数：**
- `QUERY`：自然语言描述（可选，如果不提供会提示输入）
- `-o, --output`：输出的 YAML 文件路径（可选）
- `--provider`：AI 提供商（ollama, openai, anthropic 等）
- `--model`：模型名称（覆盖配置文件中的设置）
- `--stream`：实时流式输出
- `--no-validate`：跳过 YAML 验证
- `-c, --config`：配置文件路径

**示例：**

```bash
# 使用自然语言生成配置
python -m bdfeasyinput.cli ai plan "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" -o task.yaml

# 使用指定模型
python -m bdfeasyinput.cli ai plan "..." --provider ollama --model llama3

# 流式输出
python -m bdfeasyinput.cli ai plan "..." --stream
```

#### `ai chat` - 交互式 AI 对话

启动交互式对话模式，逐步规划计算任务。

```bash
python -m bdfeasyinput.cli ai chat [-o OUTPUT] [--provider PROVIDER] [--model MODEL]
```

**参数：**
- `-o, --output`：输出的 YAML 文件路径（可选）
- `--provider`：AI 提供商
- `--model`：模型名称
- `--stream / --no-stream`：是否流式输出（默认启用）

**示例：**

```bash
python -m bdfeasyinput.cli ai chat -o task.yaml
```

#### `run` - 执行 BDF 计算

运行 BDF 计算。

```bash
python -m bdfeasyinput.cli run <input_file> [-o OUTPUT_DIR] [--timeout TIMEOUT] [--use-debug-dir]
```

**参数：**
- `input_file`：BDF 输入文件路径（必需）
- `-o, --output-dir`：输出目录（可选，默认使用输入文件所在目录）
- `--timeout`：超时时间（秒）
- `--use-debug-dir`：使用调试目录（测试用）
- `-c, --config`：配置文件路径

**示例：**

```bash
python -m bdfeasyinput.cli run bdf_input.inp -o ./results
```

#### `analyze` - 分析计算结果

使用 AI 分析 BDF 计算结果。

```bash
python -m bdfeasyinput.cli analyze <output_file> [-i INPUT] [-e ERROR] [-o OUTPUT] [--format FORMAT]
```

**参数：**
- `output_file`：BDF 输出文件路径（必需）
- `-i, --input`：BDF 输入文件路径（可选，有助于分析）
- `-e, --error`：错误文件路径（可选）
- `-o, --output`：分析报告输出路径（可选，默认输出到标准输出）
- `--format`：报告格式（markdown, html, text，默认 markdown）
- `--task-type`：任务类型（可选，帮助 AI 更好理解）
- `-c, --config`：配置文件路径

**示例：**

```bash
python -m bdfeasyinput.cli analyze output.log -i input.inp -o analysis_report.md --format markdown
```

#### `workflow` - 完整工作流

从自然语言描述到结果分析的完整工作流。

```bash
python -m bdfeasyinput.cli workflow [QUERY] [--run] [--analyze] [-o OUTPUT_DIR] [--provider PROVIDER] [--model MODEL]
```

**参数：**
- `QUERY`：自然语言描述（可选）
- `--run / --no-run`：是否执行计算（默认否）
- `--analyze / --no-analyze`：是否分析结果（默认否）
- `-o, --output-dir`：输出目录（默认 `./results`）
- `--provider`：AI 提供商
- `--model`：模型名称
- `-c, --config`：配置文件路径

**示例：**

```bash
# 完整流程：规划 → 转换 → 执行 → 分析
python -m bdfeasyinput.cli workflow "计算水分子的单点能，使用 PBE0 方法" \
  --run \
  --analyze \
  --output-dir ./results
```

### 3.3 命令组合使用

典型的完整工作流程：

```bash
# 步骤 1：AI 规划任务
python -m bdfeasyinput.cli ai plan "计算甲醛分子在水溶液中的激发能，采用 B3LYP 泛函，cc-pvdz 基组" -o task.yaml

# 步骤 2：转换为 BDF 输入
python -m bdfeasyinput.cli convert task.yaml -o bdf_input.inp

# 步骤 3：执行计算
python -m bdfeasyinput.cli run bdf_input.inp -o ./results

# 步骤 4：分析结果
python -m bdfeasyinput.cli analyze ./results/bdf_input.log -i bdf_input.inp -o analysis_report.md
```

或使用 `workflow` 命令一键完成：

```bash
python -m bdfeasyinput.cli workflow "计算甲醛分子在水溶液中的激发能，采用 B3LYP 泛函，cc-pvdz 基组" \
  --run --analyze -o ./results
```

---

## 4. YAML 输入格式

### 4.1 基本结构

YAML 配置文件的基本结构如下：

```yaml
task:
  type: <计算类型>
  description: "<可选描述>"

molecule:
  name: "<分子名称>"
  charge: <电荷>
  multiplicity: <自旋多重度>
  coordinates:
    - <原子符号> <X> <Y> <Z>
    # ...
  units: angstrom  # 或 bohr

method:
  type: <方法类型>
  functional: <泛函名称>  # 仅对 DFT
  basis: <基组名称>

settings:
  # 各种计算设置
```

### 4.2 任务类型 (task.type)

支持的计算类型：

- `energy`：单点能计算
- `optimize`：几何优化
- `frequency`：频率计算
- `tddft`：TDDFT 激发态计算

**示例：**

```yaml
task:
  type: energy
  description: "Water single point energy"
```

### 4.3 分子结构 (molecule)

#### 基本信息

```yaml
molecule:
  name: "Water"  # 可选
  charge: 0      # 必需
  multiplicity: 1  # 必需（自旋多重度 = 2S + 1）
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom  # 可选，默认 angstrom（也可用 bohr）
```

#### 坐标格式

- **列表格式**（推荐）：
  ```yaml
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
  ```

- **字符串格式**（也支持）：
  ```yaml
  coordinates: |
    O  0.0000 0.0000 0.1173
    H  0.0000 0.7572 -0.4692
  ```

#### 电荷和自旋多重度

- **charge**：分子总电荷（整数）
- **multiplicity**：自旋多重度 = 2S + 1，其中 S 是总自旋量子数
  - 闭壳层分子：`multiplicity: 1`
  - 开壳层分子（自由基）：`multiplicity: 2` 或更高
  - **如果未指定，BDF 将根据电子数自动推断**

### 4.4 计算方法 (method)

#### 方法类型

- `hf`：Hartree-Fock
- `dft`：密度泛函理论

#### DFT 泛函

常用泛函示例：

```yaml
method:
  type: dft
  functional: b3lyp      # B3LYP
  functional: pbe0       # PBE0
  functional: m06-2x     # M06-2X
  functional: cam-b3lyp  # CAM-B3LYP
  functional: wb97xd     # ωB97X-D
  basis: cc-pvdz
```

支持的泛函列表请参考 BDF 手册。

#### 基组

常用基组示例：

```yaml
method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz      # cc-pVDZ
  basis: cc-pvtz      # cc-pVTZ
  basis: 6-31g*       # 6-31G*
  basis: 6-311g**     # 6-311G**
  basis: def2-svp     # def2-SVP
  basis: def2-tzvp    # def2-TZVP
```

### 4.5 计算设置 (settings)

#### SCF 设置

```yaml
settings:
  scf:
    convergence: 1e-6        # 能量收敛标准
    max_iterations: 100      # 最大迭代次数
    grid: medium             # 积分格点（ultraCoarse, coarse, medium, fine, ultraFine）
    d3: true                 # Grimme D3 色散校正
```

#### 几何优化设置

```yaml
settings:
  geometry_optimization:
    max_iterations: 50
    convergence:
      energy: 1e-6           # 能量收敛标准
      gradient: 1e-4         # 梯度收敛标准
      displacement: 1e-3     # 位移收敛标准
```

#### 频率计算设置

```yaml
settings:
  geometry_optimization:  # 频率计算也使用此设置
    thermochemistry:
      temperature: 298.15   # 温度（K）
      pressure: 1.0         # 压力（atm）
      scale_factor: 1.0     # 频率缩放因子
      electronic_degeneracy: 1
```

#### TDDFT 设置

```yaml
settings:
  tddft:
    spin: singlet           # 或 triplet
    nstates: 5              # 计算几个激发态
    roots: 5                # 同 nstates
    tda: false              # 是否使用 TDA 近似（默认 false，使用完整 TDDFT）
    spin_adapted: false     # 是否使用 spin-adapted TDDFT
```

---

## 5. 计算类型详解

### 5.1 单点能计算 (energy)

**目的**：在给定几何结构下计算电子能量。

**最小配置：**

```yaml
task:
  type: energy

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz
```

**完整示例：**

```yaml
task:
  type: energy
  description: "Water single point energy with B3LYP/cc-pVDZ"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    convergence: 1e-6
    max_iterations: 100
    grid: medium
```

### 5.2 几何优化 (optimize)

**目的**：优化分子几何结构，寻找能量最低点（基态或激发态）。

**最小配置：**

```yaml
task:
  type: optimize

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 初始猜测结构
    - C  0.0000 1.3970 0.0000
    - C  1.2098 0.6985 0.0000
    # ...
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g*
```

**完整示例：**

```yaml
task:
  type: optimize
  description: "Benzene geometry optimization"

molecule:
  name: "Benzene"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.0000 1.3970 0.0000
    - C  1.2098 0.6985 0.0000
    - C  1.2098 -0.6985 0.0000
    - C  0.0000 -1.3970 0.0000
    - C -1.2098 -0.6985 0.0000
    - C -1.2098 0.6985 0.0000
    - H  0.0000 2.4810 0.0000
    - H  2.1490 1.2415 0.0000
    - H  2.1490 -1.2415 0.0000
    - H  0.0000 -2.4810 0.0000
    - H -2.1490 -1.2415 0.0000
    - H -2.1490 1.2415 0.0000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g*

settings:
  geometry_optimization:
    max_iterations: 50
    convergence:
      energy: 1e-6
      gradient: 1e-4
      displacement: 1e-3
  scf:
    convergence: 1e-6
    max_iterations: 100
```

### 5.3 频率计算 (frequency)

**目的**：计算分子振动频率、热力学性质和确认结构稳定性。

**最小配置：**

```yaml
task:
  type: frequency

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 通常是优化后的结构
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz
```

**完整示例：**

```yaml
task:
  type: frequency
  description: "H2O ground state frequency calculation"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    convergence: 1e-6
    max_iterations: 100
  geometry_optimization:
    thermochemistry:
      temperature: 298.15  # 298.15 K
      pressure: 1.0        # 1 atm
      scale_factor: 1.0    # 频率缩放因子
      electronic_degeneracy: 1
```

**注意**：频率计算通常需要在优化后的结构上进行，以确保是势能面上的稳定点。

### 5.4 TDDFT 激发态计算 (tddft)

**目的**：计算电子激发能、激发态性质（如振子强度、跃迁偶极矩）。

**最小配置：**

```yaml
task:
  type: tddft

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  tddft:
    spin: singlet
    nstates: 3
```

**完整示例：**

```yaml
task:
  type: tddft
  description: "H2O TDDFT singlet excitation energies"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    convergence: 1e-6
    max_iterations: 100
  tddft:
    spin: singlet          # 或 triplet（计算三重态）
    nstates: 3             # 计算 3 个激发态
    roots: 3               # 同 nstates
    tda: false             # false = 完整 TDDFT (RPA), true = TDA 近似
```

**TDDFT 选项说明：**

- `spin: singlet`：计算单重态激发态（默认）
- `spin: triplet`：计算三重态激发态
- `nstates` / `roots`：计算的激发态数量
- `tda`：
  - `false`（默认）：使用完整 TDDFT（RPA）
  - `true`：使用 TDA 近似（Tamm–Dancoff Approximation），计算更快但精度略低

---

## 6. AI 辅助功能

### 6.1 AI 提供商配置

BDFEasyInput 支持多个 AI 服务商：

1. **Ollama**（推荐用于本地使用）
2. **OpenAI** (GPT-4, GPT-3.5)
3. **Anthropic** (Claude)
4. **OpenRouter**（支持多个模型提供商）
5. **Together AI**
6. **Groq**
7. **DeepSeek**
8. **Mistral**
9. **Perplexity**

### 6.2 使用本地模型 (Ollama)

**安装 Ollama：**

```bash
# 参考 https://ollama.ai
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama3
```

**配置：**

在 `config/config.yaml` 中：

```yaml
ai:
  default_provider: "ollama"
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"
      timeout: 180
```

**使用：**

```bash
python -m bdfeasyinput.cli ai plan "计算水分子的单点能，使用 PBE0 方法" -o task.yaml
```

### 6.3 使用远程 API

#### OpenAI

**设置 API 密钥：**

```bash
export OPENAI_API_KEY=your_key_here
```

**使用：**

```bash
python -m bdfeasyinput.cli ai plan "..." --provider openai --model gpt-4 -o task.yaml
```

#### Anthropic Claude

**设置 API 密钥：**

```bash
export ANTHROPIC_API_KEY=your_key_here
```

**使用：**

```bash
python -m bdfeasyinput.cli ai plan "..." --provider anthropic --model claude-3-sonnet-20240229 -o task.yaml
```

### 6.4 自然语言规划示例

**示例 1：简单单点能计算**

```bash
python -m bdfeasyinput.cli ai plan "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" -o task.yaml
```

**示例 2：几何优化**

```bash
python -m bdfeasyinput.cli ai plan "优化苯分子的几何结构，使用 B3LYP 泛函和 6-31G* 基组" -o task.yaml
```

**示例 3：TDDFT 激发态计算**

```bash
python -m bdfeasyinput.cli ai plan "计算甲醛分子的前 5 个单重激发态，使用 B3LYP/cc-pVDZ" -o task.yaml
```

**示例 4：包含溶剂效应**

```bash
python -m bdfeasyinput.cli ai plan "计算甲醛分子在水溶液中的激发能，采用 B3LYP 泛函，cc-pvdz 基组，用线性响应理论考虑非平衡溶剂效应对激发能的影响" -o task.yaml
```

### 6.5 交互式对话模式

使用 `ai chat` 命令进行多轮对话：

```bash
python -m bdfeasyinput.cli ai chat -o task.yaml
```

交互过程示例：

```
AI Task Planner - Interactive Mode
Type 'exit' or 'quit' to end the conversation

You: 我想计算水分子的单点能
AI: 好的，我需要一些信息：您想使用什么方法和基组？
You: 使用 PBE0 和 cc-pVDZ
AI: [生成配置并显示]
[s]ave, [c]ontinue, or [q]uit? s
Configuration saved to: task.yaml
```

---

## 7. 高级特性

### 7.1 溶剂化效应

#### 基态溶剂化

**基本配置：**

```yaml
settings:
  scf:
    solvent:
      name: water        # 溶剂名称（water, methanol, acetonitrile, dmso 等）
      model: iefpcm      # 溶剂模型（iefpcm, cosmo, cpcm, smd 等）
```

**支持的溶剂模型：**
- `iefpcm`（默认）：IEFPCM
- `cosmo`：COSMO
- `cpcm`：CPCM
- `smd`：SMD
- `ssvpe`：SS(V)PE
- `ddcosmo`：ddCOSMO

**预定义溶剂：**
`water`, `methanol`, `ethanol`, `acetonitrile`, `dmso`, `thf`, `benzene` 等。

**用户指定介电常数：**

```yaml
settings:
  scf:
    solvent:
      name: user
      dielectric: 78.3553          # 静态介电常数
      optical_dielectric: 1.7778   # 光学介电常数（用于非平衡溶剂化）
      model: iefpcm
```

**自定义孔穴参数：**

```yaml
settings:
  scf:
    solvent:
      name: water
      model: iefpcm
      cavity:
        type: swig                 # swig | switching | ses | sphere
        radius_type: UFF           # UFF | Bondi
        vdW_scale: 1.1
        precision: medium          # ultraCoarse | coarse | medium | fine | ultraFine
      radii:
        H: 1.4430
        O: 1.7500
```

**非静电溶剂化能：**

```yaml
settings:
  scf:
    solvent:
      name: water
      model: iefpcm
      non_electrostatic:
        components: [dis, rep, cav]  # 色散能、排斥能、孔穴能
        solvent_atoms: H2O1
        solvent_rho: 0.03333         # molecules Å^-3
        solvent_radius: 1.385        # Å
```

#### 激发态非平衡溶剂化

激发态计算中，溶剂的极化分为快极化和慢极化，需要非平衡溶剂化校正。

**方法 1：cLR（corrected Linear Response，矫正的线性响应）**

```yaml
task:
  type: tddft

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # ...

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    solvent:
      name: user
      dielectric: 78.3553
      optical_dielectric: 1.7778   # 必需
      model: iefpcm
  tddft:
    nstates: 8
    solvent_effect:
      mode: clr                    # 线性响应非平衡溶剂化
```

**方法 2：ptSS（perturbative State-Specific，一阶微扰态特定）**

```yaml
task:
  type: tddft

molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # ...

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    solvent:
      name: water
      model: iefpcm
  tddft:
    nstates: 5
    solvent_effect:
      mode: ptss                   # 态特定非平衡溶剂化
      resp_nfiles: 1               # RESP 模块参数
      resp_iroot: 1                # 计算的根（激发态编号）
```

**完整示例（ptSS）：**

```yaml
task:
  type: tddft
  description: "Formaldehyde TDDFT with ptSS non-equilibrium solvation"

molecule:
  name: "Formaldehyde"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.00000000  -0.54200000
    - O  0.00000000  0.00000000   0.67700000
    - H  0.00000000  0.93500000  -1.08200000
    - H  0.00000000  -0.93500000  -1.08200000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g

settings:
  scf:
    solvent:
      name: water
      model: iefpcm
  tddft:
    spin: singlet
    nstates: 5
    solvent_effect:
      mode: ptss
      resp_nfiles: 1
      resp_iroot: 1
```

### 7.2 高级 SCF 设置

```yaml
settings:
  scf:
    convergence: 1e-6
    max_iterations: 100
    grid: medium                   # 积分格点精度
    grid_tolerance: 1e-7           # 格点截断阈值
    d3: true                       # Grimme D3 色散校正
    vshift: 0.0                    # 虚轨道能级移动（帮助 SCF 收敛）
    fac_ex: 0.20                   # 精确交换成分（用于自定义泛函）
    fac_co: 0.0                    # 双杂化泛函的 MP2 相关项成分
```

### 7.3 对称性设置

```yaml
settings:
  compass:
    symmetry: true                 # 是否使用对称性（默认 true）
    point_group: auto              # 点群（auto 表示自动检测）
```

禁用对称性：

```yaml
settings:
  compass:
    symmetry: false
```

### 7.4 开壳层计算

对于开壳层分子（自由基），需要设置正确的自旋多重度：

```yaml
molecule:
  charge: 0
  multiplicity: 2                 # 开壳层（doublet）
  coordinates:
    # ...

method:
  type: dft                       # 会自动使用 UKS（开壳层 DFT）
  functional: b3lyp
  basis: cc-pvdz
```

**自旋多重度规则：**
- 闭壳层（偶数电子）：`multiplicity: 1`
- 自由基（奇数电子）：通常 `multiplicity: 2`
- 三重态：`multiplicity: 3`

---

## 8. 结果分析

### 8.1 分析命令

```bash
python -m bdfeasyinput.cli analyze <output_file> [-i INPUT] [-e ERROR] [-o OUTPUT] [--format FORMAT]
```

**示例：**

```bash
python -m bdfeasyinput.cli analyze output.log -i input.inp -o report.md --format markdown
```

### 8.2 分析报告内容

分析报告包含以下内容：

#### 原始数据
- **几何结构**：优化后的分子结构
- **SCF 能量组件**：总能量、电子能量、核排斥能等
- **SCF 收敛信息**：收敛标准、实际收敛值、迭代次数
- **HOMO-LUMO 能隙**：轨道能量、能隙、收敛建议
- **性质**：偶极矩、Mulliken 和 Löwdin 布居分析

#### TDDFT 分析（如果适用）
- 计算方法（TDDFT/RPA 或 TDA）
- 激发能、振子强度、跃迁偶极矩
- JK 算符内存信息（估算内存、最大内存、每次可计算的根数、效率警告）
- 自旋翻转计算说明（如果适用）

#### 溶剂效应分析（如果适用）
- 溶剂模型和方法
- 介电常数
- 孔穴参数（tessellation 方法、tessera 数量等）
- 非平衡溶剂化校正（cLR 或 ptSS）
  - 校正后的垂直吸收能量
  - 非平衡溶剂化自由能
  - 平衡溶剂化自由能
  - cLR 校正值

#### AI 分析总结
- 计算方法的合理性评估
- 结果的可信度分析
- 潜在问题和改进建议

### 8.3 报告格式

支持三种格式：

- **Markdown**（默认）：适合阅读和版本控制
- **HTML**：适合网页展示
- **Text**：纯文本格式

### 8.4 双语支持

在配置文件中设置语言：

```yaml
analysis:
  ai:
    language: "zh"  # 中文（默认）
    # 或
    language: "en"  # 英文
```

或在命令行中通过配置文件指定。

---

## 9. 故障排除

### 9.1 常见错误

#### 命令找不到

**问题：** `bdfeasyinput: command not found`

**解决方案：**

1. 使用 Python 模块方式：
   ```bash
   python3 -m bdfeasyinput.cli --help
   ```

2. 添加 PATH（见 [INSTALL.md](../INSTALL.md)）：
   ```bash
   export PATH="$HOME/Library/Python/3.7/bin:$PATH"
   ```

3. 创建别名：
   ```bash
   alias bdfeasyinput='python3 -m bdfeasyinput.cli'
   ```

#### YAML 解析错误

**问题：** `yaml.scanner.ScannerError` 或类似错误

**解决方案：**
- 检查 YAML 语法（缩进、冒号、列表格式）
- 使用在线 YAML 验证器检查
- 确保所有字符串都用引号（如果包含特殊字符）

#### 验证错误

**问题：** `ValidationError: ...`

**解决方案：**
- 检查必需字段是否提供（task.type, molecule.charge, molecule.multiplicity, method.type）
- 检查参数值是否在允许范围内
- 查看错误消息中的具体提示

#### SCF 不收敛

**问题：** SCF 迭代达到最大次数仍未收敛

**解决方案：**
1. 检查初始几何结构是否合理
2. 增加 `settings.scf.max_iterations`
3. 降低 `settings.scf.convergence` 标准（不推荐）
4. 添加 `vshift` 关键词（如果 HOMO-LUMO 能隙很小）：
   ```yaml
   settings:
     scf:
       vshift: 0.1  # 移动虚轨道能级
   ```
5. 尝试不同的初始猜测（如果支持）

#### TDDFT 内存不足

**问题：** JK 算符内存不足，导致效率低下

**解决方案：**
如果 `Nexit`（请求的根数）大于每次可计算的根数，在 TDDFT 设置中添加：

```yaml
settings:
  tddft:
    memjkop: "1024M"  # 每 OpenMP 线程的内存（MB）
```

注意：实际使用内存 = `memjkop` × OpenMP 线程数

### 9.2 调试技巧

#### 查看生成的 BDF 输入

转换后查看生成的 BDF 输入文件，确认格式正确：

```bash
python -m bdfeasyinput.cli convert task.yaml -o input.inp
cat input.inp
```

#### 使用调试目录

运行计算时使用 `--use-debug-dir` 选项：

```bash
python -m bdfeasyinput.cli run input.inp --use-debug-dir
```

#### 检查日志

查看执行日志和错误文件以定位问题。

### 9.3 获取帮助

- 查看命令帮助：`python -m bdfeasyinput.cli <command> --help`
- 查看项目文档：`docs/` 目录
- 查看示例：`examples/` 目录
- 查看开发文档：`docs/dev/` 目录

---

## 10. 常见问题

### Q1: 如何选择合适的基组？

**A:** 一般建议：
- **小分子（< 10 原子）**：`cc-pVTZ` 或 `6-311G**`
- **中等分子（10-50 原子）**：`cc-pVDZ` 或 `6-31G*`
- **大分子（> 50 原子）**：`6-31G` 或 `def2-SVP`

### Q2: 如何选择合适的泛函？

**A:** 常用建议：
- **通用目的**：`B3LYP`（最常用）
- **长程相互作用**：`CAM-B3LYP`、`ωB97X-D`
- **金属体系**：`M06`、`M06-2X`
- **快速计算**：`PBE`、`PBE0`

### Q3: 如何判断几何优化是否收敛？

**A:** 查看输出文件中的收敛信息：
- 能量变化 < 收敛标准
- 梯度最大值 < 梯度收敛标准
- 位移最大值 < 位移收敛标准

如果未收敛，可以：
- 增加最大迭代次数
- 放宽收敛标准（不推荐）
- 检查结构是否合理

### Q4: 频率计算中出现虚频怎么办？

**A:** 虚频（负频率）表示结构不是稳定点。建议：
1. 重新优化几何结构（更严格的收敛标准）
2. 检查初始结构是否合理
3. 如果是最小值附近，可以忽略小的虚频（< 50 cm⁻¹）

### Q5: TDDFT 中 TDA 和完整 TDDFT 有什么区别？

**A:**
- **TDA**（`tda: true`）：Tamm–Dancoff 近似，忽略 de-excitation 项，计算更快，但可能低估激发能
- **完整 TDDFT**（`tda: false`，默认）：包含所有项，更准确但计算更慢

**建议**：初始筛选用 TDA，最终结果用完整 TDDFT。

### Q6: 如何选择合适的溶剂模型？

**A:**
- **IEFPCM**（默认）：通用，适用于大多数情况
- **COSMO**：适合极性溶剂
- **SMD**：包含更多溶剂参数，可能更准确
- **CPCM**：简单快速

### Q7: cLR 和 ptSS 有什么区别？

**A:**
- **cLR**：矫正的线性响应，计算快速，适合大多数情况
- **ptSS**：态特定微扰理论，理论上更准确，但计算更慢且更复杂

**建议**：先用 cLR，如果需要更高精度再用 ptSS。

### Q8: 如何提高计算速度？

**A:**
1. 使用较小的基组（如 `6-31G*` 而非 `cc-pVTZ`）
2. 降低积分格点精度（`grid: coarse`）
3. 使用 TDA 而非完整 TDDFT（对于激发态）
4. 减少计算的激发态数量
5. 使用更快的泛函（如 `PBE` 而非 `M06-2X`）

### Q9: 如何设置自旋多重度？

**A:**
- **闭壳层分子**（偶数电子，如 H₂O）：`multiplicity: 1`
- **自由基**（奇数电子，如 CH₃·）：`multiplicity: 2`
- **三重态**（如 O₂）：`multiplicity: 3`

如果不确定，AI 规划功能可以自动推断。

### Q10: 支持哪些文件格式？

**A:**
- **输入**：YAML（推荐）、JSON
- **输出**：BDF 输入格式（.inp）
- **分析报告**：Markdown（.md）、HTML（.html）、Text（.txt）

---

## 附录

### A. 完整的 YAML 配置模板

参见 `examples/` 目录中的示例文件。

### B. 支持的 DFT 泛函列表

请参考 BDF 手册中的完整列表。常用泛函包括：
- B3LYP, PBE0, M06-2X, CAM-B3LYP, ωB97X-D, PBE, TPSS, M06, etc.

### C. 支持的基组列表

请参考 BDF 手册。常用基组包括：
- cc-pVDZ, cc-pVTZ, cc-pVQZ
- 6-31G, 6-31G*, 6-311G**
- def2-SVP, def2-TZVP
- aug-cc-pVDZ（扩散函数）

### D. 参考文档

- **项目 README**：[README.md](../README.md)
- **安装说明**：[INSTALL.md](../INSTALL.md)
- **开发文档**：[docs/dev/](../docs/dev/)
- **示例文件**：[examples/](../examples/)
- **BDF 手册**：参考 BDF 软件文档

### E. 更新日志

查看 `docs/dev/CURRENT_STATUS_2025.md` 了解最新功能更新。

---

**最后更新**：2025年

**版本**：1.0

**维护者**：BDFEasyInput 开发团队
