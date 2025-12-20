# BDFEasyInput 功能总结与工作流程图

**最后更新**: 2025年12月17日

## 📋 项目概述

**BDFEasyInput** 是一个完整的 BDF 量子化学计算工作流工具，旨在简化 BDF 软件的输入生成、计算执行和结果分析，支持从任务规划到结果分析的一站式解决方案。

### 核心目标

- **简化输入**：将复杂的 BDF 专家模式输入转换为简洁的 YAML/JSON 格式
- **AI 辅助**：通过自然语言描述自动规划计算任务
- **自动化执行**：集成 BDF 执行引擎，自动运行计算
- **智能分析**：基于量子化学专家知识自动分析计算结果

---

## 🏗️ 系统架构

### 模块结构

```
BDFEasyInput/
├── bdfeasyinput/
│   ├── cli.py                    # 命令行接口
│   ├── converter.py              # 核心转换器
│   ├── validator.py              # 输入验证器
│   ├── config.py                 # 配置管理
│   │
│   ├── modules/                  # BDF 模块生成器
│   │   ├── compass.py           # COMPASS 模块（分子结构、基组）
│   │   ├── scf.py               # SCF 模块（电子结构方法）
│   │   ├── tddft.py             # TDDFT 模块（激发态计算）
│   │   ├── bdfopt.py            # BDFOPT 模块（结构优化）
│   │   ├── resp.py              # RESP 模块（激发态梯度）
│   │   ├── mp2.py               # MP2 模块（后HF方法）
│   │   └── xuanyuan.py          # XUANYUAN 模块（相对论）
│   │
│   ├── ai/                       # AI 辅助模块
│   │   ├── client/              # AI 客户端（9个服务商）
│   │   │   ├── ollama.py
│   │   │   ├── openai_client.py
│   │   │   ├── anthropic_client.py
│   │   │   ├── openrouter_client.py
│   │   │   └── openai_compatible.py  # 兼容多个服务商
│   │   ├── planner/             # 任务规划器
│   │   │   ├── task_planner.py
│   │   │   └── method_recommender.py
│   │   ├── parser/              # 响应解析器
│   │   │   └── response_parser.py
│   │   └── prompt/              # 提示词模板
│   │       └── templates.py
│   │
│   ├── execution/               # 执行模块
│   │   ├── runner.py           # 执行器工厂
│   │   ├── bdf_direct.py       # 直接执行模式
│   │   └── bdfautotest.py      # BDFAutotest 模式
│   │
│   └── analysis/                # 结果分析模块
│       ├── parser/              # 输出解析器
│       │   └── output_parser.py
│       ├── analyzer/            # AI 分析器
│       │   └── quantum_chem_analyzer.py
│       ├── prompt/              # 分析提示词
│       │   ├── analysis_prompts.py
│       │   └── analysis_prompts_en.py
│       └── report/              # 报告生成器
│           ├── report_generator.py
│           └── report_labels.py
```

---

## 🎯 核心功能模块

### 1. 输入转换模块 (Converter)

**功能**：将 YAML/JSON 配置转换为 BDF 专家模式输入文件

#### 1.1 支持的计算类型

- ✅ **SCF 单点能量计算**
  - RHF (限制性 Hartree-Fock)
  - UHF (非限制性 Hartree-Fock)
  - RKS (限制性 Kohn-Sham)
  - UKS (非限制性 Kohn-Sham)
  - ROKS (限制性开壳层 Kohn-Sham)

- ✅ **TDDFT 激发态计算**
  - 单重态激发 (Singlet)
  - 三重态激发 (Triplet)
  - 自旋轨道耦合 (SOC)
  - Spin-flip TDDFT

- ✅ **结构优化**
  - 基态几何优化
  - 激发态几何优化（TDDFT 梯度）

- ✅ **频率计算**
  - Hessian 计算 (`hess only`)
  - 优化后频率计算 (`hess final`)

#### 1.2 支持的 BDF 模块

- **COMPASS**：分子结构、基组、对称性
- **SCF**：电子结构方法、DFT 泛函、溶剂化
- **TDDFT**：激发态计算、非平衡溶剂化（cLR, ptSS）
- **BDFOPT**：几何优化
- **RESP**：激发态梯度计算
- **MP2**：后 HF 方法
- **XUANYUAN**：相对论哈密顿

#### 1.3 关键词映射系统

- 17,000+ 行关键词数据库
- 支持 `common` 和 `expert` 级别关键词
- 基于 BDF 官方手册的完整映射

---

### 2. AI 辅助模块 (AI)

**功能**：通过自然语言描述自动规划计算任务

#### 2.1 AI 服务商支持（9个）

- **Ollama**：本地模型（推荐，数据隐私）
- **OpenAI**：GPT-4, GPT-3.5
- **Anthropic**：Claude 系列
- **OpenRouter**：统一访问多个模型
- **Together AI**：开源模型 API
- **Groq**：快速推理服务
- **DeepSeek**：优秀中文支持
- **Mistral AI**：高质量欧洲模型
- **Perplexity**：实时信息检索

#### 2.2 AI 功能

- **任务规划**：自然语言 → YAML 配置
- **方法推荐**：基于分子特征推荐计算方法
- **结果分析**：专家级量子化学分析
- **交互式对话**：`ai-chat` 命令支持多轮对话

---

### 3. 执行模块 (Execution)

**功能**：自动执行 BDF 计算

#### 3.1 执行模式

- **直接执行模式** (`BDFDirectRunner`)
  - 直接调用 BDF 可执行文件
  - 自动设置环境变量
  - 支持临时目录

- **BDFAutotest 模式** (`BDFAutotestRunner`)
  - 通过 BDFAutotest 工具执行
  - 任务管理和监控
  - 进度跟踪

#### 3.2 功能特性

- 自动环境变量设置
- 输出文件自动命名
- 超时处理
- 错误捕获和报告

---

### 4. 分析模块 (Analysis)

**功能**：解析 BDF 输出文件并生成分析报告

#### 4.1 输出解析器 (`output_parser.py`)

**提取的数据**：

- **能量信息**
  - 总能量 (E_tot)
  - SCF 能量
  - 能量分解（E_ele, E_nn, E_1e, E_ne, E_kin, E_ee, E_xc）
  - 维里比 (Virial Ratio)

- **几何结构**
  - 原子坐标（支持 Bohr 和 Angstrom）
  - 优化后的几何结构
  - 收敛状态

- **优化信息**
  - 每步 SCF 能量（从 `*.out.tmp` 提取）
  - 每步收敛指标（Force-RMS, Force-Max, Step-RMS, Step-Max）
  - 最终 SCF 能量分解

- **TDDFT 信息**
  - 激发态能量
  - 激发态优化信息（ifile, irep, istate, Etot）
  - Spin-flip TDDFT 参数（isf, ialda）

- **频率信息**
  - 振动频率
  - 红外强度
  - 热力学数据

- **其他性质**
  - HOMO-LUMO 能隙
  - 偶极矩
  - Mulliken 布居分析
  - 对称群信息
  - 不可约表示

#### 4.2 AI 分析器 (`quantum_chem_analyzer.py`)

- 基于量子化学专家知识的智能分析
- 收敛性评估
- 结果合理性检查
- 专业建议和优化方案

#### 4.3 报告生成器 (`report_generator.py`)

**报告格式**：
- Markdown（默认）
- HTML
- Text

**报告内容**：
- 计算总结
- 能量分析
- 几何结构分析
- 收敛性分析
- 优化步骤表（基态/激发态）
- 原始数据（结构化展示）

**语言支持**：
- 中文
- 英文

---

### 5. 验证模块 (Validator)

**功能**：验证输入参数的有效性和兼容性

- 参数范围检查
- 参数兼容性检查
- 警告系统（非关键问题）
- Schema 验证

---

## 🔄 完整工作流程

### 流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     BDFEasyInput 工作流程                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│  用户输入     │
│              │
│ 方式1: 自然语言│  ───┐
│ 方式2: YAML  │  ───┤
│ 方式3: JSON  │  ───┘
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 1: 任务规划 (可选)                                     │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ AI Planner   │─────▶│ YAML Config  │                    │
│  │ (自然语言)    │      │ (结构化配置)  │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  功能:                                                       │
│  - 解析自然语言描述                                          │
│  - 推荐计算方法                                              │
│  - 生成 YAML 配置                                            │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 2: 输入验证                                             │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Validator    │─────▶│ Valid Config │                    │
│  │ (参数检查)    │      │ (验证通过)    │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  功能:                                                       │
│  - 参数范围检查                                              │
│  - 兼容性检查                                                │
│  - 警告提示                                                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 3: BDF 输入生成                                         │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Converter   │─────▶│ BDF Input   │                    │
│  │ (YAML→BDF) │      │ (.inp 文件)  │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  模块生成:                                                   │
│  - COMPASS (结构、基组)                                       │
│  - SCF (电子结构方法)                                         │
│  - TDDFT (激发态)                                            │
│  - BDFOPT (优化)                                             │
│  - RESP (梯度)                                               │
│  - MP2 (后HF)                                                │
│  - XUANYUAN (相对论)                                         │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 4: 计算执行 (可选)                                       │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Runner       │─────▶│ BDF Output   │                    │
│  │ (执行引擎)    │      │ (.log/.out)  │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  执行模式:                                                   │
│  - 直接执行 (BDFDirectRunner)                                 │
│  - BDFAutotest (BDFAutotestRunner)                           │
│                                                              │
│  输出文件:                                                   │
│  - *.log (主输出)                                            │
│  - *.out.tmp (临时输出，含每步SCF能量)                        │
│  - *.err (错误信息)                                          │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 5: 结果解析                                             │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Parser       │─────▶│ Parsed Data  │                    │
│  │ (输出解析)    │      │ (结构化数据)  │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  提取信息:                                                   │
│  - 能量 (总能量、SCF能量、能量分解)                            │
│  - 几何结构 (优化后坐标)                                       │
│  - 优化步骤 (每步SCF能量、收敛指标)                            │
│  - TDDFT 信息 (激发态能量、优化信息)                           │
│  - 频率 (振动频率、热力学)                                     │
│  - 其他性质 (HOMO-LUMO、偶极矩等)                              │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 6: AI 分析 (可选)                                       │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Analyzer     │─────▶│ AI Analysis  │                    │
│  │ (AI分析器)    │      │ (专家分析)    │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  分析内容:                                                   │
│  - 计算总结                                                  │
│  - 能量分析                                                  │
│  - 几何结构分析                                              │
│  - 收敛性评估                                                │
│  - 专业建议                                                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤 7: 报告生成                                             │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Report       │─────▶│ Analysis     │                    │
│  │ Generator    │      │ Report       │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                              │
│  报告格式:                                                   │
│  - Markdown (默认)                                           │
│  - HTML                                                      │
│  - Text                                                      │
│                                                              │
│  报告内容:                                                   │
│  - 计算总结                                                  │
│  - 能量分析 (含SCF能量分解)                                   │
│  - 几何结构                                                  │
│  - 优化步骤表 (基态/激发态)                                    │
│  - 原始数据 (结构化展示)                                      │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  最终结果     │
│              │
│ - BDF 输入文件│
│ - 计算结果    │
│ - 分析报告    │
└──────────────┘
```

---

## 📊 详细工作流程说明

### 方式 1: 完整工作流（推荐）

```bash
# 一步完成：规划 → 转换 → 执行 → 分析
python -m bdfeasyinput.cli workflow \
  "计算水分子的单点能，使用 PBE0 方法" \
  --run \
  --analyze \
  --output-dir ./results
```

**流程**：
1. AI 规划：自然语言 → YAML
2. 转换：YAML → BDF 输入
3. 执行：运行 BDF 计算
4. 解析：提取计算结果
5. AI 分析：生成专家分析
6. 报告：生成 Markdown 报告

### 方式 2: 分步执行

```bash
# 步骤 1: 规划任务
python -m bdfeasyinput.cli ai-plan \
  "计算水分子的单点能" \
  -o task.yaml

# 步骤 2: 生成 BDF 输入
python -m bdfeasyinput.cli convert \
  task.yaml \
  -o bdf_input.inp

# 步骤 3: 运行计算
python -m bdfeasyinput.cli run \
  bdf_input.inp \
  --output-dir ./results

# 步骤 4: 分析结果
python -m bdfeasyinput.cli analyze \
  ./results/output.log \
  --input bdf_input.inp \
  -o analysis_report.md
```

### 方式 3: 只分析已有结果

```bash
# 分析已有的 BDF 输出文件
python -m bdfeasyinput.cli analyze \
  existing_output.log \
  --input existing_input.inp \
  -o analysis_report.md
```

---

## 🔑 关键特性

### 1. 智能优化步骤提取

**基态优化**：
- 从 `*.out.tmp` 提取每步 SCF 能量
- 从 `*.log` 提取每步收敛指标
- 生成优化步骤表

**激发态优化**：
- 从 `*.out.tmp` 提取 TDDFT 梯度信息（ifile, irep, istate, Etot）
- 结合 SCF 能量和收敛指标
- 生成 TDDFT 激发态优化表

### 2. SCF 能量分解

- 从最后一次 `Final scf result` 提取完整能量分解
- 包含：E_tot, E_ele, E_sol, E_nn, E_1e, E_ne, E_kin, E_ee, E_xc, Virial Ratio
- 在报告中详细展示

### 3. 多格式报告

- **Markdown**：便于阅读和版本控制
- **HTML**：便于网页展示
- **Text**：纯文本格式

### 4. 双语支持

- 中文报告（默认）
- 英文报告

---

## 📈 数据流图

```
用户输入
    │
    ├─→ [AI Planner] ──→ YAML Config
    │
    ├─→ [Validator] ──→ Validated Config
    │
    ├─→ [Converter] ──→ BDF Input File
    │
    ├─→ [Runner] ──→ BDF Output Files
    │                    │
    │                    ├─→ *.log (主输出)
    │                    ├─→ *.out.tmp (每步SCF能量)
    │                    └─→ *.err (错误)
    │
    ├─→ [Parser] ──→ Parsed Data
    │                    │
    │                    ├─→ 能量信息
    │                    ├─→ 几何结构
    │                    ├─→ 优化步骤
    │                    ├─→ TDDFT 信息
    │                    └─→ 其他性质
    │
    ├─→ [AI Analyzer] ──→ AI Analysis
    │
    └─→ [Report Generator] ──→ Analysis Report
```

---

## 🎯 使用场景

### 场景 1: 快速单点能计算

```bash
python -m bdfeasyinput.cli workflow \
  "计算苯分子的单点能，使用 B3LYP/6-31G" \
  --run
```

### 场景 2: 结构优化 + 频率计算

```yaml
# task.yaml
task:
  type: optimization
  frequency: true

molecule:
  # ... 分子结构

method:
  type: dft
  functional: pbe0
  basis: cc-pvdz
```

### 场景 3: TDDFT 激发态优化

```yaml
# task.yaml
task:
  type: tddft_optimization
  state: 1  # 优化第1个激发态

tddft:
  states: 5
  method: tda
```

### 场景 4: 批量分析已有结果

```bash
# 分析多个输出文件
for file in *.log; do
  python -m bdfeasyinput.cli analyze "$file" \
    --input "${file%.log}.inp" \
    -o "${file%.log}_report.md"
done
```

---

## 📚 相关文档

- [用户手册](../USER_MANUAL.md)
- [架构设计](ARCHITECTURE.md)
- [AI 模块设计](AI_MODULE_DESIGN.md)
- [执行与分析设计](EXECUTION_AND_ANALYSIS_DESIGN.md)
- [当前状态](CURRENT_STATUS_2025.md)

---

## 🔄 版本历史

- **v1.0** (2025-12-17): 完整工作流实现
  - 优化步骤提取增强
  - TDDFT 激发态优化支持
  - SCF 能量分解展示
  - 报告生成优化

---

**文档维护**: 本文档随项目发展持续更新
