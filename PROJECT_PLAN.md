# BDFEasyInput 项目规划文档

## 1. 项目概述

### 1.1 项目目标
BDFEasyInput 是一个完整的 BDF 量子化学计算工作流工具，旨在简化 BDF (Beijing Density Functional Package) 的整个使用流程：
1. **输入生成**：通过简洁、直观的输入方式或自然语言描述，自动生成 BDF 输入文件
2. **计算执行**：集成 BDFAutotest，自动运行 BDF 计算
3. **结果分析**：使用 AI 模型分析计算结果，提供专家级见解

### 1.2 核心价值
- **易用性**：降低 BDF 学习曲线，让非专家用户也能快速上手
- **自动化**：从输入生成到结果分析的全流程自动化
- **AI 辅助**：
  - 通过自然语言描述，AI 自动规划计算任务并生成输入
  - AI 分析计算结果，提供专家级见解和建议
- **准确性**：减少手动编写输入文件时的错误
- **完整性**：覆盖从任务规划到结果分析的完整工作流
- **扩展性**：支持未来 BDF 新功能的快速集成

## 2. 技术架构

### 2.1 技术栈建议
- **编程语言**：Python 3.8+
  - 优势：丰富的科学计算生态、易于扩展、良好的可读性
- **核心库**：
  - `pyyaml` / `toml`：配置文件解析
  - `jinja2`：模板引擎（用于生成输入文件）
  - `pydantic`：数据验证和模型定义
  - `click` / `argparse`：命令行界面
- **AI 库**（可选）：
  - `openai`：OpenAI API 客户端
  - `anthropic`：Anthropic API 客户端
  - `ollama`：Ollama 本地模型客户端
  - `langchain`：可选，用于更复杂的 AI 工作流
- **开发工具**：
  - `pytest`：单元测试
  - `black` / `ruff`：代码格式化
  - `mypy`：类型检查

### 2.2 架构设计
```
BDFEasyInput/
├── bdfeasyinput/          # 核心包
│   ├── __init__.py
│   ├── ai/                # AI 模块
│   │   ├── __init__.py
│   │   ├── client/        # AI 客户端
│   │   │   ├── base.py
│   │   │   ├── ollama.py
│   │   │   ├── openai.py
│   │   │   └── anthropic.py
│   │   ├── planner/       # 任务规划器
│   │   │   ├── task_planner.py
│   │   │   └── method_recommender.py
│   │   ├── prompt/        # 提示词模板
│   │   │   └── templates.py
│   │   └── parser/        # AI 输出解析
│   │       └── response_parser.py
│   ├── execution/         # ⭐ NEW 执行模块
│   │   ├── __init__.py
│   │   ├── bdfautotest.py # BDFAutotest 集成
│   │   ├── runner.py      # 执行管理器
│   │   └── monitor.py     # 计算监控
│   ├── analysis/          # ⭐ NEW 结果分析模块
│   │   ├── __init__.py
│   │   ├── parser/        # 输出文件解析
│   │   │   ├── output_parser.py
│   │   │   └── error_parser.py
│   │   ├── analyzer/      # AI 分析器
│   │   │   ├── base_analyzer.py
│   │   │   ├── quantum_chem_analyzer.py
│   │   │   └── result_summarizer.py
│   │   ├── prompt/        # 分析提示词
│   │   │   ├── analysis_prompts.py
│   │   │   └── expert_templates.py
│   │   └── report/        # 报告生成
│   │       ├── report_generator.py
│   │       └── templates/
│   ├── parser/            # 输入解析模块
│   │   ├── yaml_parser.py
│   │   ├── json_parser.py
│   │   └── cli_parser.py
│   ├── translator/        # 转换引擎
│   │   ├── base.py
│   │   ├── dft_translator.py
│   │   ├── wavefunction_translator.py
│   │   └── geometry_translator.py
│   ├── validator/         # 输入验证
│   │   ├── schema.py
│   │   └── validator.py
│   ├── generator/         # BDF输入文件生成
│   │   ├── template_engine.py
│   │   └── formatter.py
│   └── utils/             # 工具函数
│       ├── molecule.py
│       └── constants.py
├── templates/             # BDF输入模板
│   ├── dft.template
│   ├── scf.template
│   └── ...
├── examples/              # 示例输入文件
│   ├── h2o_dft.yaml
│   ├── benzene_scf.yaml
│   └── ...
├── tests/                 # 测试文件
│   ├── test_parser.py
│   ├── test_translator.py
│   └── ...
├── docs/                  # 文档
│   ├── user_guide.md
│   ├── api_reference.md
│   └── examples.md
├── requirements.txt
├── setup.py
├── README.md
└── PROJECT_PLAN.md
```

## 3. 功能模块设计

### 3.0 AI 规划模块 (AI Planner) ⭐ NEW
**功能**：使用大语言模型辅助用户规划计算任务
- 自然语言理解：
  - 解析用户的自然语言描述
  - 理解计算意图（单点能、优化、频率等）
  - 提取关键参数（分子、方法、基组等）
- 任务规划：
  - 自动补充缺失参数
  - 推荐合适的方法和基组
  - 优化计算设置
- YAML 生成：
  - 自动生成符合规范的 YAML 输入文件
  - 验证生成的 YAML 有效性
- AI 客户端支持：
  - 本地模型（Ollama、vLLM 等）
  - 远程 API（OpenAI、Anthropic 等）
  - 统一的客户端接口

### 3.1 输入解析模块 (Parser)
**功能**：解析用户的简洁输入
- 支持格式：
  - YAML（推荐，可读性好）
  - JSON（程序友好）
  - 命令行参数（简单任务）
- 解析内容：
  - 分子结构（坐标、分子式）
  - 计算方法（DFT、HF、MP2等）
  - 基组选择
  - 计算类型（单点能、几何优化、频率等）
  - 其他计算参数

### 3.2 验证模块 (Validator)
**功能**：验证输入的正确性和完整性
- 参数范围检查
- 参数兼容性检查
- 必需参数检查
- 分子结构有效性验证

### 3.3 转换模块 (Translator)
**功能**：将简洁输入转换为 BDF 内部表示
- 方法映射（如 "pbe0" → BDF 中的具体关键词）
- 基组映射（如 "cc-pvdz" → BDF 基组名）
- 参数转换（单位转换、格式转换等）
- 默认值填充

### 3.4 生成模块 (Generator)
**功能**：生成 BDF 输入文件
- 使用模板引擎生成标准 BDF 输入格式
- 格式化输出
- 支持多种 BDF 输入风格

### 3.5 执行模块 (Execution) ⭐ NEW
**功能**：集成 BDFAutotest，运行 BDF 计算
- BDFAutotest 集成：
  - 调用 BDFAutotest 运行 BDF
  - 管理计算任务
  - 监控计算进度
- 任务管理：
  - 提交计算任务
  - 等待计算完成
  - 处理超时和错误
- 计算监控：
  - 实时查看计算状态
  - 获取日志信息
  - 进度跟踪

### 3.6 结果分析模块 (Analysis) ⭐ NEW
**功能**：使用 AI 分析 BDF 计算结果
- 输出文件解析：
  - 提取能量、几何结构、频率等关键数据
  - 检查计算收敛性
  - 识别警告和错误
- AI 分析：
  - 基于量子化学专家模式分析结果
  - 提供专业见解和建议
  - 评估计算质量
- 报告生成：
  - 生成用户友好的分析报告
  - 支持多种输出格式（Markdown, HTML, Text）
  - 包含原始数据和建议
- 数据标准化 ⭐ NEW：
  - 标准化分析结果格式
  - 定义统一的数据 Schema
  - 导出训练数据格式（JSONL/JSON）
  - 支持未来 LLM 模型训练

## 4. 输入格式设计

### 4.0 AI 自然语言输入 ⭐ NEW

用户可以直接用自然语言描述计算需求：

**示例 1：完整描述**
```
用户输入："计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组，水分子坐标是..."

AI 输出：生成完整的 YAML 文件
```

**示例 2：简化描述**
```
用户输入："帮我优化苯分子的几何结构"

AI 输出：自动补充推荐方法和基组，生成完整 YAML
```

**示例 3：交互式对话**
```
用户："我想计算一个过渡金属配合物的电子结构"
AI："请问您要计算什么性质？单点能、几何优化还是其他？"
用户："几何优化"
AI："好的，我建议使用 PBE0 泛函和 def2-TZVP 基组，因为..."
```

### 4.1 YAML 输入示例

```yaml
# 基本计算任务
task:
  type: energy          # 或 geometry, frequency, etc.
  
molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    # 单位由 molecule.units 指定（默认: angstrom）
    - O  0.0000 0.0000 0.0000
    - H  0.9572 0.0000 0.0000
    - H -0.2398 0.9266 0.0000
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom

method:
  type: dft
  functional: pbe0  # 单一泛函，或使用 "PBE LYP" 组合泛函
  basis: cc-pvdz

# 高级选项
settings:
  scf:
    convergence: 1e-6
    max_iterations: 100
    # occupied: [3, 0, 1, 0]  # 可选：指定不可约表示的双占据轨道数（RHF/RKS，D2h及其子群）
    # 如果不指定，BDF 会自动计算
  integration:
    grid: fine
```

**坐标格式说明**：
- 坐标格式为 `ATOM X Y Z`，每行一个原子
- 与常见的 XYZ 文件格式兼容
- 详细说明请参考 [坐标格式文档](docs/coordinate_format.md)

### 4.2 简化版本（命令行友好）
```yaml
molecule: h2o.xyz
method: pbe0/cc-pvdz
task: optimize
```

## 5. 开发计划

### Phase 1: 基础框架 (2-3周)
- [ ] 项目初始化
- [ ] 核心架构搭建
- [ ] YAML 解析器实现
- [ ] 基础验证框架
- [ ] 简单的转换器原型
- [ ] AI 模块基础架构（可选）

### Phase 2: 核心功能 (4-6周)
- [ ] 分子结构解析（支持多种格式）
- [ ] 常用计算方法支持（DFT、HF）
- [ ] 基组映射系统
- [ ] BDF 输入文件生成
- [ ] 单元测试覆盖

### Phase 3: 扩展功能 (3-4周)
- [ ] 几何优化支持
- [ ] 频率计算支持
- [ ] 更多 DFT 泛函
- [ ] 电子结构分析任务

### Phase 4: 完善与优化 (2-3周)
- [ ] 错误处理完善
- [ ] 用户文档编写
- [ ] 示例库建设
- [ ] 性能优化

## 6. 设计原则

1. **简洁性**：用户输入尽可能简洁直观
2. **灵活性**：支持从简单到复杂的各种计算场景
3. **可扩展性**：易于添加新的计算方法和支持
4. **向后兼容**：支持 BDF 的不同版本
5. **透明性**：生成的输入文件清晰可读，便于调试

## 7. AI 功能集成 ⭐ NEW

### 7.1 AI 辅助输入
- 自然语言到 YAML 的自动转换
- 智能参数推荐和优化
- 交互式任务规划对话

### 7.2 支持的 AI 模型
- **本地模型**：Ollama（推荐用于隐私保护）
- **远程 API**：OpenAI GPT-4, Anthropic Claude
- **扩展性**：支持更多模型接口

### 7.3 详细设计
参考 [AI_MODULE_DESIGN.md](AI_MODULE_DESIGN.md) 了解完整的 AI 模块设计。

## 8. 完整工作流 ⭐ NEW

### 8.1 端到端流程
```
用户输入（自然语言或 YAML）
    ↓
[AI 规划] → 生成 YAML
    ↓
[转换] → 生成 BDF 输入文件
    ↓
[执行] → 调用 BDFAutotest 运行 BDF
    ↓
[分析] → AI 分析计算结果
    ↓
生成分析报告
```

### 8.2 使用方式
- **完整工作流**：一次性完成从规划到分析的全流程
- **分步执行**：可以分步执行，灵活控制每个环节
- **只分析**：对已有结果进行分析

## 9. 后续考虑

- 图形用户界面（GUI）
- 与常用量子化学工作流工具集成
- 批量计算任务管理
- 结果可视化
- 计算历史记录和对比

## 9. 参考资料

- BDF 用户手册
- 其他量子化学软件的简化输入格式（如 ORCA, Q-Chem）
- YAML/JSON 配置最佳实践
- AI 提示词工程最佳实践
- 大语言模型应用开发指南

