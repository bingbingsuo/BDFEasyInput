# BDF 执行模块实现计划

**优先级**：高（用于测试现有输入转换代码）

**最后更新**：2025年1月

## 🎯 目标

实现 BDF 计算执行模块，通过 BDFAutotest 工程运行 BDF 计算，便于测试现有的输入转换代码。

## 📋 需求分析

### 核心需求
1. **简单集成**：设定 BDFAutotest 工程路径，直接调用 BDFAutotest 命令执行 BDF
2. **执行逻辑委托**：BDF 执行逻辑全部交给 BDFAutotest 管理
3. **便于测试**：能够快速测试生成的 BDF 输入文件是否正确

### 功能要求
- ✅ 配置 BDFAutotest 路径
- ✅ 调用 BDFAutotest 运行 BDF 计算
- ✅ 获取执行结果（成功/失败）
- ✅ 返回输出文件路径
- ✅ 基本的错误处理

### 非必需功能（未来扩展）
- ⏳ 计算进度监控
- ⏳ 任务队列管理
- ⏳ 超时控制
- ⏳ 日志记录

## 🏗️ 架构设计

### 模块结构

```
bdfeasyinput/
└── execution/
    ├── __init__.py
    ├── bdfautotest.py      # BDFAutotest 集成（核心）
    └── config.py            # 配置管理（可选）
```

### 核心类设计

```python
class BDFAutotestRunner:
    """BDFAutotest 执行器 - 简单封装"""
    
    def __init__(self, bdfautotest_path: str):
        """
        初始化执行器
        
        Args:
            bdfautotest_path: BDFAutotest 工程路径
        """
        pass
    
    def run(self, input_file: str, **kwargs) -> Dict[str, Any]:
        """
        运行 BDF 计算
        
        Args:
            input_file: BDF 输入文件路径
            **kwargs: 传递给 BDFAutotest 的额外参数
        
        Returns:
            {
                'status': 'success' | 'failed',
                'output_file': str,  # 输出文件路径
                'error_file': str,   # 错误文件路径（如果有）
                'exit_code': int,    # 退出码
                'stdout': str,       # 标准输出
                'stderr': str        # 标准错误
            }
        """
        pass
```

## 🔧 实现方案

### 方案 1：直接调用 BDFAutotest 命令行（推荐）

**优点**：
- 简单直接
- 不依赖 BDFAutotest 的 Python API
- 易于调试

**实现**：
```python
import subprocess
from pathlib import Path

class BDFAutotestRunner:
    def __init__(self, bdfautotest_path: str):
        self.bdfautotest_path = Path(bdfautotest_path)
        # 假设 BDFAutotest 有命令行接口
        # 需要确认实际的命令格式
    
    def run(self, input_file: str, **kwargs):
        # 调用 BDFAutotest 的命令行工具
        # 例如：python /path/to/bdfautotest/run.py input.inp
        pass
```

### 方案 2：通过 BDFAutotest 的 Python API（如果存在）

**优点**：
- 更紧密的集成
- 更好的错误处理

**缺点**：
- 需要了解 BDFAutotest 的内部 API
- 可能更复杂

## 📝 实现步骤

### Step 1: 研究 BDFAutotest 接口（1-2 小时）

**任务**：
- [ ] 查看 BDFAutotest 的 README 和文档
- [ ] 了解如何调用 BDFAutotest 运行单个 BDF 计算
- [ ] 确认命令行接口或 Python API
- [ ] 测试手动运行一个 BDF 计算

**输出**：
- BDFAutotest 使用方式文档
- 示例命令或代码

### Step 2: 实现基础执行器（2-3 小时）

**任务**：
- [ ] 创建 `bdfeasyinput/execution/` 目录
- [ ] 实现 `BDFAutotestRunner` 类
- [ ] 实现 `run()` 方法
- [ ] 基本的错误处理

**文件**：
- `bdfeasyinput/execution/__init__.py`
- `bdfeasyinput/execution/bdfautotest.py`

### Step 3: 配置管理（1 小时）

**任务**：
- [ ] 支持环境变量配置（`BDFAUTOTEST_PATH`）
- [ ] 支持配置文件
- [ ] 支持命令行参数

### Step 4: 集成到转换器（1 小时）

**任务**：
- [ ] 在 `BDFConverter` 中添加执行选项
- [ ] 创建便捷方法：`convert_and_run()`
- [ ] 更新文档

### Step 5: 测试和文档（1-2 小时）

**任务**：
- [ ] 编写测试用例
- [ ] 测试各种场景
- [ ] 更新文档
- [ ] 创建使用示例

## 🔍 BDFAutotest 接口调研

### 需要确认的问题

1. **如何运行单个 BDF 计算？**
   - 是否有命令行工具？
   - 命令格式是什么？
   - 需要哪些参数？

2. **输入输出文件**
   - 输入文件格式（.inp）？
   - 输出文件位置？
   - 错误文件位置？

3. **工作目录**
   - 在哪里运行？
   - 输出文件放在哪里？

4. **BDF 可执行文件**
   - BDFAutotest 如何找到 BDF 可执行文件？
   - 需要单独配置吗？

### 调研任务

- [ ] 查看 BDFAutotest 的 `test_runner.py`
- [ ] 查看 BDFAutotest 的 `orchestrator.py`
- [ ] 查看 BDFAutotest 的配置文件示例
- [ ] 尝试手动运行一个测试

## 📦 配置方式

### 方式 1：环境变量（最简单）

```bash
export BDFAUTOTEST_PATH=/path/to/BDFAutoTest
```

### 方式 2：配置文件

```yaml
# config/execution_config.yaml
execution:
  bdfautotest_path: "/path/to/BDFAutoTest"
```

### 方式 3：代码中指定

```python
from bdfeasyinput.execution import BDFAutotestRunner

runner = BDFAutotestRunner("/path/to/BDFAutoTest")
```

## 🎯 使用示例

### 基本使用

```python
from bdfeasyinput import BDFConverter
from bdfeasyinput.execution import BDFAutotestRunner

# 1. 转换 YAML 到 BDF
converter = BDFConverter()
bdf_input = converter.convert_file("input.yaml", "output.inp")

# 2. 运行 BDF 计算
runner = BDFAutotestRunner("/path/to/BDFAutoTest")
result = runner.run("output.inp")

# 3. 检查结果
if result['status'] == 'success':
    print(f"计算成功！输出文件: {result['output_file']}")
else:
    print(f"计算失败！错误: {result.get('error', 'Unknown error')}")
```

### 一键转换+运行

```python
from bdfeasyinput import BDFConverter
from bdfeasyinput.execution import BDFAutotestRunner

converter = BDFConverter()
runner = BDFAutotestRunner("/path/to/BDFAutoTest")

# 转换并运行
bdf_input = converter.convert_file("input.yaml", "output.inp")
result = runner.run("output.inp")
```

## 📊 优先级和时间估算

| 任务 | 优先级 | 时间估算 | 状态 |
|------|--------|----------|------|
| 研究 BDFAutotest 接口 | 高 | 1-2 小时 | ⏳ |
| 实现基础执行器 | 高 | 2-3 小时 | ⏳ |
| 配置管理 | 中 | 1 小时 | ⏳ |
| 集成到转换器 | 中 | 1 小时 | ⏳ |
| 测试和文档 | 中 | 1-2 小时 | ⏳ |

**总计**：约 6-9 小时

## 🚀 快速开始（最小实现）

如果只需要快速测试，可以实现最小版本：

```python
# bdfeasyinput/execution/bdfautotest.py
import subprocess
from pathlib import Path
from typing import Dict, Any

class BDFAutotestRunner:
    def __init__(self, bdfautotest_path: str):
        self.bdfautotest_path = Path(bdfautotest_path)
    
    def run(self, input_file: str) -> Dict[str, Any]:
        """运行 BDF 计算（最小实现）"""
        input_path = Path(input_file)
        output_file = input_path.with_suffix('.out')
        
        # 调用 BDFAutotest（需要确认实际命令）
        # 假设：python /path/to/bdfautotest/run.py input.inp
        cmd = [
            'python',
            str(self.bdfautotest_path / 'run.py'),  # 需要确认
            str(input_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=input_path.parent
        )
        
        return {
            'status': 'success' if result.returncode == 0 else 'failed',
            'output_file': str(output_file),
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
```

## 📝 下一步行动

1. **立即开始**：研究 BDFAutotest 的接口
2. **确认命令**：了解如何调用 BDFAutotest 运行单个计算
3. **实现最小版本**：快速实现基础功能
4. **测试验证**：使用实际例子测试
5. **完善功能**：根据需求逐步完善

---

**注意**：本计划假设 BDFAutotest 有命令行接口。如果实际情况不同，需要调整实现方案。

