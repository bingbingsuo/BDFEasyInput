# Debug 目录功能说明

**日期**: 2025年12月9日

## 📋 功能概述

在 `bdfeasyinput` 包中创建了 `debug` 目录，用于测试时作为 BDF 的工作目录。这样可以：
- 集中管理测试文件
- 避免测试文件污染项目根目录
- 方便清理测试数据

## 📁 目录结构

```
BDFEasyInput/
├── bdfeasyinput/      # 主代码包
│   └── ...
└── debug/             # 测试工作目录（与 bdfeasyinput 平级）
    ├── *.inp          # 输入文件（自动复制）
    ├── *.log          # 输出文件
    ├── *.err          # 错误文件
    └── ...            # 其他 BDF 生成的文件
```

## 🚀 使用方法

### 命令行使用

```bash
# 使用 debug 目录作为工作目录
bdfeasyinput run input.inp --use-debug-dir

# 配合配置文件使用
bdfeasyinput run input.inp --use-debug-dir -c config/config.yaml
```

### Python API 使用

```python
from bdfeasyinput.execution import create_runner
from bdfeasyinput.config import load_config, merge_config_with_defaults

# 加载配置
config = load_config('config/config.yaml')
config = merge_config_with_defaults(config)

# 创建执行器
runner = create_runner(config=config)

# 使用 debug 目录运行
result = runner.run('input.inp', use_debug_dir=True)
```

## 🔧 实现细节

### 1. 目录创建

- 目录路径: `debug/` (项目根目录，与 `bdfeasyinput` 平级)
- 自动创建（如果不存在）
- 权限: 755

### 2. 文件处理

当 `use_debug_dir=True` 时：
1. **输入文件**: 自动复制到项目根目录的 `debug/` 目录
2. **工作目录**: 设置为项目根目录的 `debug/`
3. **输出文件**: 所有输出文件（.log, .err 等）都保存在 debug 目录中

### 3. 环境变量

BDF 环境变量设置：
- `BDF_WORKDIR`: `/path/to/BDFEasyInput/debug`
- `BDF_TMPDIR`: `/tmp/$RANDOM` (每次运行使用新的随机目录)
- `BDFHOME`: 从配置文件读取

## 📝 代码修改

### 修改的文件

1. **`bdfeasyinput/execution/bdf_direct.py`**
   - 添加 `use_debug_dir` 参数到 `run()` 方法
   - 实现 debug 目录逻辑
   - 自动复制输入文件到 debug 目录

2. **`bdfeasyinput/cli.py`**
   - 添加 `--use-debug-dir` 选项到 `run` 命令
   - 传递参数给执行器

### 关键代码

```python
# bdfeasyinput/execution/bdf_direct.py
if use_debug_dir:
    # 从 bdfeasyinput/execution/bdf_direct.py 向上三级到项目根目录
    project_root = Path(__file__).parent.parent.parent
    debug_dir = project_root / "debug"
    work_dir = debug_dir
    work_dir.mkdir(parents=True, exist_ok=True)
    # 将输入文件复制到 debug 目录
    debug_input_file = work_dir / input_path.name
    import shutil
    shutil.copy2(input_path, debug_input_file)
    input_file_for_bdf = debug_input_file.name
else:
    work_dir = input_path.parent
    input_file_for_bdf = input_path.name
```

## ✅ 测试验证

### 测试结果

- ✅ Debug 目录创建成功
- ✅ 输入文件自动复制到 debug 目录
- ✅ 输出文件保存在 debug 目录
- ✅ BDF_WORKDIR 正确设置
- ✅ 计算正常运行

### 测试命令

```bash
# 清理旧文件
rm -f debug/*

# 运行测试
bdfeasyinput run test_debug.inp --use-debug-dir -c config/config.yaml

# 检查文件
ls -lh debug/
```

## 🎯 使用场景

1. **开发测试**: 集中管理测试文件
2. **调试计算**: 方便查看和清理测试数据
3. **CI/CD**: 在自动化测试中使用

## 📌 注意事项

1. **文件清理**: Debug 目录中的文件不会自动清理，需要手动删除
2. **输入文件**: 使用 `--use-debug-dir` 时，输入文件会被复制到 debug 目录
3. **权限**: 确保有写入 debug 目录的权限

## 🔄 后续改进建议

1. **自动清理**: 添加选项自动清理 debug 目录
2. **配置选项**: 在配置文件中添加默认使用 debug 目录的选项
3. **日志记录**: 记录使用 debug 目录的运行历史

## 🎉 总结

Debug 目录功能已成功实现，可以方便地用于测试和调试 BDF 计算。所有测试文件都集中在项目根目录的 `debug/` 目录中（与 `bdfeasyinput` 平级），便于管理和清理。

