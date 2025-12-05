# BDF 直接执行模式

**完成日期**：2025年1月

## ✅ 功能概述

BDFEasyInput 现在支持两种执行模式：

1. **BDFAutotest 模式**：通过 BDFAutotest 工程运行 BDF 计算
2. **直接执行模式**：直接调用 BDF 可执行文件，不通过 BDFAutotest

## 🎯 直接执行模式特点

- ✅ 不依赖 BDFAutotest
- ✅ 在 YAML 文件中配置 BDF 安装目录
- ✅ 自动设置环境变量（BDFHOME, BDF_WORKDIR, BDF_TMPDIR）
- ✅ 支持 OpenMP 配置（OMP_NUM_THREADS, OMP_STACKSIZE）
- ✅ 输出文件自动命名（name.log, name.err）

## 📝 YAML 配置格式

### 基本配置

```yaml
# 计算任务配置
task:
  type: energy
  description: "H2O single point energy calculation"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000  0.0000  0.1173
    - H  0.0000  0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: hf
  basis: cc-pvdz

# 执行配置
execution:
  type: direct  # 直接执行模式
  
  # BDF 安装目录（必需）
  bdf_home: "/path/to/bdf/installation"
  
  # 临时文件目录（可选，默认 "/tmp/$RANDOM"）
  # 支持 $RANDOM 占位符，每次运行生成随机目录名避免冲突
  bdf_tmpdir: "/tmp/$RANDOM"
  
  # OpenMP 线程数（可选，默认使用 CPU 核心数）
  omp_num_threads: 8
  
  # OpenMP 栈大小（可选，默认 "512M"）
  omp_stacksize: "512M"
```

### BDFAutotest 模式配置（对比）

```yaml
execution:
  type: bdfautotest  # BDFAutotest 模式
  
  # BDFAutotest 工程路径（必需）
  bdfautotest_path: "/path/to/BDFAutoTest"
  
  # 配置文件路径（可选）
  config_file: "/path/to/BDFAutoTest/config/config.yaml"
```

## 🔧 环境变量设置

直接执行模式会自动设置以下环境变量：

| 环境变量 | 说明 | 来源 |
|---------|------|------|
| `BDFHOME` | BDF 安装目录 | `execution.bdf_home` |
| `BDF_WORKDIR` | 工作目录 | 输入文件所在目录 |
| `BDF_TMPDIR` | 临时文件目录 | `execution.bdf_tmpdir`（支持 `$RANDOM` 占位符）或 `/tmp/$RANDOM` |
| `OMP_NUM_THREADS` | OpenMP 线程数 | `execution.omp_num_threads` 或 CPU 核心数 |
| `OMP_STACKSIZE` | OpenMP 栈大小 | `execution.omp_stacksize` 或 "512M" |

## 📂 输出文件

### 文件命名规则

- **输入文件**：`name.inp`（由用户指定）
- **输出文件**：`name.log`（自动生成，在 BDF_WORKDIR 中）
- **错误文件**：`name.err`（自动生成，在 BDF_WORKDIR 中）

### 文件位置

所有文件都在 `BDF_WORKDIR`（输入文件所在目录）中：

```
/path/to/input/dir/
├── name.inp    # 输入文件
├── name.log    # 标准输出（BDF 计算结果）
└── name.err    # 标准错误（错误信息）
```

## 💻 使用示例

### 示例 1: 从 YAML 配置创建执行器

```python
import yaml
from bdfeasyinput import BDFConverter
from bdfeasyinput.execution import create_runner

# 1. 读取 YAML 配置
with open('input.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 2. 转换 YAML 到 BDF
converter = BDFConverter()
bdf_input = converter.convert_file('input.yaml', 'output.inp')

# 3. 从配置创建执行器（自动选择 direct 或 bdfautotest）
runner = create_runner(config=config)

# 4. 运行计算
result = runner.run(bdf_input)

# 5. 检查结果
if result['status'] == 'success':
    print(f"计算成功！输出文件: {result['output_file']}")
else:
    print(f"计算失败: {result.get('stderr', 'Unknown error')}")
```

### 示例 2: 直接使用 BDFDirectRunner

```python
from bdfeasyinput.execution import BDFDirectRunner

# 创建直接执行器
runner = BDFDirectRunner(
    bdf_home="/path/to/bdf/installation",
    bdf_tmpdir="/tmp/bdf_tmp",
    omp_num_threads=8,
    omp_stacksize="512M"
)

# 运行计算
result = runner.run("input.inp")

# 检查结果
print(f"状态: {result['status']}")
print(f"输出文件: {result['output_file']}")
print(f"错误文件: {result['error_file']}")
```

### 示例 3: 使用工厂函数

```python
from bdfeasyinput.execution import create_runner

# 方式 1: 从配置创建
runner = create_runner(config=yaml_config)

# 方式 2: 直接指定 BDF 安装目录
runner = create_runner(bdf_home="/path/to/bdf")

# 方式 3: 直接指定 BDFAutotest 路径
runner = create_runner(bdfautotest_path="/path/to/BDFAutoTest")
```

## 🔍 BDF 可执行文件

直接执行模式会自动查找 BDF 可执行文件，按以下顺序：

1. `{BDFHOME}/sbin/bdf.drv`
2. `{BDFHOME}/sbin/bdfdrv.py`

如果都找不到，会抛出 `ValueError` 异常。

## ⚙️ 执行命令

直接执行模式使用的命令格式：

```bash
{BDFHOME}/sbin/bdf.drv -r {input_file}
```

其中：
- `{BDFHOME}` 从 `execution.bdf_home` 读取
- `{input_file}` 是输入文件名（仅文件名，因为工作目录已设置为输入文件目录）

## 📊 返回结果格式

```python
{
    'status': 'success' | 'failed' | 'timeout',
    'output_file': str,          # 输出文件路径（name.log）
    'error_file': str,           # 错误文件路径（name.err）
    'exit_code': int,            # 退出码
    'stdout': str,              # 标准输出（从文件读取）
    'stderr': str,              # 标准错误（从文件读取）
    'execution_time': float,    # 执行时间（秒）
    'command': str,             # 执行的命令
    'bdf_home': str,            # BDF 安装目录
    'bdf_workdir': str,         # 工作目录
    'bdf_tmpdir': str           # 临时目录
}
```

## 🆚 两种模式对比

| 特性 | 直接执行模式 | BDFAutotest 模式 |
|------|-------------|-----------------|
| 依赖 | 仅需 BDF 安装 | 需要 BDFAutotest |
| 配置 | YAML 中配置 | 需要 BDFAutotest 配置文件 |
| 环境变量 | 自动设置 | 由 BDFAutotest 管理 |
| 输出文件 | name.log, name.err | 由 BDFAutotest 决定 |
| 适用场景 | 简单直接执行 | 需要 BDFAutotest 功能 |

## 📋 前置条件

### 直接执行模式

1. **BDF 安装**
   - BDF 已正确安装
   - 可执行文件位于 `{BDFHOME}/sbin/bdf.drv` 或 `{BDFHOME}/sbin/bdfdrv.py`

2. **YAML 配置**
   - `execution.type: direct`
   - `execution.bdf_home` 必须设置

### BDFAutotest 模式

1. **BDFAutotest 工程**
   - 已安装并配置 BDFAutotest
   - 配置文件 `config/config.yaml` 存在

2. **BDF 安装**
   - BDF 包已构建
   - BDFHOME 路径在 BDFAutotest 配置中正确设置

## 🧪 测试

运行示例代码：

```bash
# 直接执行模式示例
python examples/direct_execution_example.py
```

**注意**：需要先设置正确的 BDF 安装路径。

## 📚 相关文档

- [EXECUTION_MODULE_PLAN.md](EXECUTION_MODULE_PLAN.md) - 执行模块实现计划
- [EXECUTION_IMPLEMENTATION.md](EXECUTION_IMPLEMENTATION.md) - BDFAutotest 模式实现总结
- [examples/direct_execution_example.py](examples/direct_execution_example.py) - 直接执行示例
- [examples/h2o_rhf_with_execution.yaml](examples/h2o_rhf_with_execution.yaml) - 包含执行配置的 YAML 示例

---

**状态**：✅ 直接执行模式已实现，可用于测试

