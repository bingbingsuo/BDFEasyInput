# BDFEasyInput 快速开始指南

## 项目结构概览

```
BDFEasyInput/
├── PROJECT_PLAN.md          # 项目总体规划文档
├── ARCHITECTURE.md          # 详细架构设计文档
├── IMPLEMENTATION_ROADMAP.md # 实施路线图
├── README.md                # 项目说明
├── QUICKSTART.md            # 本文件 - 快速开始
│
├── requirements.txt         # Python 依赖
├── setup.py                 # 安装配置
├── .gitignore              # Git 忽略文件
│
├── bdfeasyinput/           # 核心代码包（待创建）
│   ├── __init__.py
│   ├── parser/             # 输入解析模块
│   ├── translator/         # 转换引擎
│   ├── validator/          # 验证模块
│   ├── generator/          # 文件生成器
│   └── utils/              # 工具函数
│
├── templates/              # BDF 输入模板（待创建）
│   ├── dft.template
│   ├── scf.template
│   └── ...
│
├── examples/               # 示例输入文件
│   ├── simple_h2o.yaml
│   └── benzene_optimization.yaml
│
├── tests/                  # 测试文件（待创建）
│   ├── test_parser.py
│   ├── test_translator.py
│   └── ...
│
└── docs/                   # 文档
    └── user_guide_outline.md
```

## 核心概念

### 工作流程

```
用户输入 (YAML) → 解析 → 验证 → 转换 → 生成 → BDF 输入文件
```

### 输入格式示例

```yaml
task:
  type: energy

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
  functional: pbe0
  basis: cc-pvdz
```

### 设计原则

1. **简洁性** - 用户输入尽可能简单
2. **透明性** - 生成的输入文件清晰可读
3. **可扩展性** - 易于添加新功能
4. **可靠性** - 严格的验证和测试

## 当前状态

🚧 **项目规划阶段**

已完成：
- ✅ 项目规划文档
- ✅ 架构设计文档
- ✅ 实施路线图
- ✅ 基础项目结构
- ✅ 示例输入文件

待实施：
- ⏳ 核心代码实现
- ⏳ BDF 输入格式研究
- ⏳ 方法/基组映射表
- ⏳ 测试用例

## 下一步行动

### 1. 了解 BDF 输入格式

在开始编码前，需要：
- 收集 BDF 输入文件示例
- 理解 BDF 的关键词和语法
- 建立方法名称映射表
- 建立基组名称映射表

### 2. 搭建开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发模式
pip install -e .
```

### 3. 开始 MVP 开发

按照 `IMPLEMENTATION_ROADMAP.md` 中的阶段 1 开始实施：
1. 创建核心包结构
2. 实现基础数据模型
3. 实现 YAML 解析器
4. 实现简单的转换器和生成器

### 4. 迭代开发

- 先实现最小功能
- 测试和验证
- 逐步扩展功能
- 收集用户反馈

## 关键文档

- **PROJECT_PLAN.md** - 了解项目整体目标和设计
- **ARCHITECTURE.md** - 理解系统架构和模块设计
- **IMPLEMENTATION_ROADMAP.md** - 查看详细实施计划
- **examples/** - 参考输入格式示例

## 需要决定的事项

在开始编码前，建议先明确：

1. **BDF 版本兼容性**
   - 支持哪些 BDF 版本？
   - 不同版本的输入格式差异？

2. **输入格式细节**
   - 坐标单位（Angstrom/Bohr）？
   - 支持哪些文件格式作为输入（XYZ, Mol2 等）？
   - 如何表示内坐标？

3. **方法支持范围**
   - MVP 阶段支持哪些方法？
   - 如何映射方法名称？

4. **基组支持范围**
   - MVP 阶段支持哪些基组？
   - 如何映射基组名称？

5. **计算类型优先级**
   - 优先支持哪些计算类型？
   - 单点能、优化、频率的优先级？

## 联系方式与协作

- 项目仓库：[待添加]
- 问题追踪：[待添加]
- 讨论区：[待添加]

## 贡献指南

欢迎贡献！在开始编码前，请：
1. 阅读项目文档
2. 了解代码风格规范
3. 查看待实现的功能列表
4. 提交 Issue 讨论大的改动

---

**祝开发顺利！** 🚀

