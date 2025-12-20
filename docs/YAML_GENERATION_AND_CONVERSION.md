# YAML 生成和转换工具使用指南

本文档介绍 BDFEasyInput 的 YAML 文件生成和 YAML 到 BDF 输入文件转换功能。

## 目录

1. [概述](#概述)
2. [YAML 生成功能](#yaml-生成功能)
3. [转换功能](#转换功能)
4. [命令行接口](#命令行接口)
5. [Python API](#python-api)
6. [使用示例](#使用示例)

## 概述

BDFEasyInput 提供了完整的 YAML 生成和转换工具链：

- **YAML 生成**：从模板、XYZ 文件或通过 AI 生成 YAML 配置文件
- **YAML 转换**：将 YAML 配置文件转换为 BDF 输入文件
- **批量处理**：支持批量转换多个文件
- **验证功能**：自动验证 YAML 配置的有效性

## YAML 生成功能

### 1. 从模板生成

生成指定任务类型的 YAML 模板：

```bash
# 生成单点能计算模板
python -m bdfeasyinput.cli yaml generate energy -o template_energy.yaml

# 生成几何优化模板
python -m bdfeasyinput.cli yaml generate optimize -o template_opt.yaml

# 生成频率计算模板
python -m bdfeasyinput.cli yaml generate frequency -o template_freq.yaml

# 生成 TDDFT 计算模板
python -m bdfeasyinput.cli yaml generate tddft -o template_tddft.yaml
```

### 2. 从 XYZ 文件生成

从 XYZ 坐标文件直接生成 YAML 配置：

```bash
# 基本用法
python -m bdfeasyinput.cli yaml from-xyz molecule.xyz -o molecule.yaml

# 指定计算类型和参数
python -m bdfeasyinput.cli yaml from-xyz molecule.xyz \
  --task-type optimize \
  --charge 0 \
  --multiplicity 1 \
  --functional pbe0 \
  --basis cc-pvdz \
  -o molecule_opt.yaml
```

### 3. 通过 AI 生成

使用自然语言描述生成 YAML（需要配置 AI 服务）：

```bash
python -m bdfeasyinput.cli ai plan \
  "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组" \
  -o task.yaml
```

## 转换功能

### 1. 单个文件转换

将 YAML 文件转换为 BDF 输入文件：

```bash
# 基本转换
python -m bdfeasyinput.cli convert task.yaml -o bdf_input.inp

# 输出到标准输出
python -m bdfeasyinput.cli convert task.yaml
```

### 2. 批量转换

批量转换多个 YAML 文件：

```bash
# 转换当前目录下所有 YAML 文件
python -m bdfeasyinput.cli batch-convert *.yaml

# 指定输出目录
python -m bdfeasyinput.cli batch-convert file1.yaml file2.yaml -d ./output

# 允许覆盖已存在的文件
python -m bdfeasyinput.cli batch-convert *.yaml --overwrite
```

### 3. 预览功能

预览转换结果而不保存文件：

```bash
python -m bdfeasyinput.cli preview task.yaml

# 限制显示行数
python -m bdfeasyinput.cli preview task.yaml --max-lines 30
```

### 4. 验证功能

验证 YAML 配置文件的有效性：

```bash
python -m bdfeasyinput.cli validate-yaml task.yaml
```

## 命令行接口

### YAML 生成命令

#### `yaml generate`

生成 YAML 模板。

**用法：**
```bash
python -m bdfeasyinput.cli yaml generate <task_type> [OPTIONS]
```

**参数：**
- `task_type`: 任务类型 (`energy`, `optimize`, `frequency`, `tddft`)

**选项：**
- `-o, --output`: 输出 YAML 文件路径
- `--no-comments`: 不包含注释

#### `yaml from-xyz`

从 XYZ 文件生成 YAML。

**用法：**
```bash
python -m bdfeasyinput.cli yaml from-xyz <xyz_file> [OPTIONS]
```

**选项：**
- `-o, --output`: 输出 YAML 文件路径
- `-t, --task-type`: 任务类型（默认: `energy`）
- `--charge`: 分子电荷（默认: 0）
- `--multiplicity`: 自旋多重度（默认: 1）
- `--functional`: DFT 泛函（默认: `pbe0`）
- `--basis`: 基组（默认: `cc-pvdz`）
- `--no-validate`: 跳过验证

### 转换命令

#### `convert`

转换单个 YAML 文件到 BDF 输入。

**用法：**
```bash
python -m bdfeasyinput.cli convert <input_file> [OPTIONS]
```

**选项：**
- `-o, --output`: 输出 BDF 文件路径

#### `batch-convert`

批量转换多个 YAML 文件。

**用法：**
```bash
python -m bdfeasyinput.cli batch-convert <yaml_files>... [OPTIONS]
```

**选项：**
- `-d, --output-dir`: 输出目录
- `--overwrite`: 覆盖已存在的文件
- `--no-validate`: 跳过验证

#### `preview`

预览转换结果。

**用法：**
```bash
python -m bdfeasyinput.cli preview <yaml_file> [OPTIONS]
```

**选项：**
- `--max-lines`: 最大显示行数（默认: 50）

#### `validate-yaml`

验证 YAML 配置文件。

**用法：**
```bash
python -m bdfeasyinput.cli validate-yaml <yaml_file>
```

## Python API

### YAML 生成器

```python
from bdfeasyinput import YAMLGenerator, generate_yaml_from_xyz, generate_yaml_template

# 创建生成器
generator = YAMLGenerator(validate_output=True)

# 从模板生成
template = generator.generate_template('energy', include_comments=True)

# 从 XYZ 文件生成
config = generator.generate_from_xyz(
    xyz_path='molecule.xyz',
    task_type='energy',
    charge=0,
    multiplicity=1,
    method={'type': 'dft', 'functional': 'pbe0', 'basis': 'cc-pvdz'}
)

# 保存 YAML
generator.save_yaml(config, 'output.yaml')

# 便利函数
config = generate_yaml_from_xyz('molecule.xyz', output_path='output.yaml')
template = generate_yaml_template('energy', output_path='template.yaml')
```

### 转换工具

```python
from bdfeasyinput import ConversionTool, convert_yaml_to_bdf, batch_convert_yaml

# 创建转换工具
tool = ConversionTool(validate_input=True)

# 转换单个文件
bdf_path = tool.convert_file('task.yaml', 'output.inp')

# 转换字典
bdf_content = tool.convert_dict(config_dict)

# 批量转换
results = tool.batch_convert(['file1.yaml', 'file2.yaml'], output_dir='./output')

# 预览
preview, config = tool.preview('task.yaml', max_lines=50)

# 验证
is_valid, errors, warnings = tool.validate_yaml('task.yaml')

# 从 XYZ 直接转换
bdf_path = tool.convert_from_xyz('molecule.xyz', task_type='energy')

# 便利函数
bdf_path = convert_yaml_to_bdf('task.yaml', 'output.inp')
results = batch_convert_yaml(['file1.yaml', 'file2.yaml'], output_dir='./output')
```

## 使用示例

### 示例 1：从 XYZ 文件生成并转换

```bash
# 步骤 1：从 XYZ 文件生成 YAML
python -m bdfeasyinput.cli yaml from-xyz h2o.xyz \
  --task-type energy \
  --functional pbe0 \
  --basis cc-pvdz \
  -o h2o.yaml

# 步骤 2：转换为 BDF 输入
python -m bdfeasyinput.cli convert h2o.yaml -o h2o.inp
```

### 示例 2：批量处理

```bash
# 批量转换多个 YAML 文件
python -m bdfeasyinput.cli batch-convert \
  h2o_energy.yaml \
  h2o_opt.yaml \
  h2o_freq.yaml \
  -d ./bdf_inputs
```

### 示例 3：Python 脚本示例

```python
from bdfeasyinput import YAMLGenerator, ConversionTool

# 创建生成器和转换工具
yaml_gen = YAMLGenerator()
converter = ConversionTool()

# 从 XYZ 生成 YAML
config = yaml_gen.generate_from_xyz(
    xyz_path='molecule.xyz',
    task_type='optimize',
    charge=0,
    multiplicity=1,
    method={
        'type': 'dft',
        'functional': 'b3lyp',
        'basis': '6-31g*'
    },
    settings={
        'scf': {'convergence': 1e-6},
        'geometry_optimization': {'max_iterations': 50}
    }
)

# 保存 YAML
yaml_gen.save_yaml(config, 'molecule_opt.yaml')

# 转换为 BDF
bdf_path = converter.convert_file('molecule_opt.yaml', 'molecule_opt.inp')
print(f"BDF input file generated: {bdf_path}")
```

### 示例 4：验证和预览

```python
from bdfeasyinput import ConversionTool

tool = ConversionTool()

# 验证 YAML
is_valid, errors, warnings = tool.validate_yaml('task.yaml')
if not is_valid:
    print("Errors:", errors)
else:
    print("YAML is valid!")
    if warnings:
        print("Warnings:", warnings)

# 预览转换结果
preview, config = tool.preview('task.yaml', max_lines=30)
print("Preview:")
print(preview)
```

## 注意事项

1. **验证**：默认情况下，YAML 生成和转换都会进行验证。可以使用 `--no-validate` 或 `validate_output=False` 跳过验证。

2. **文件覆盖**：默认情况下不会覆盖已存在的文件。使用 `--overwrite` 或 `overwrite=True` 允许覆盖。

3. **XYZ 文件格式**：XYZ 文件应遵循标准格式：
   ```
   <number_of_atoms>
   <comment_line>
   <atom_symbol> <x> <y> <z>
   ...
   ```

4. **错误处理**：批量转换时，默认会继续处理其他文件即使某个文件出错。错误信息会记录在返回的字典中。

## 相关文档

- [用户手册](USER_MANUAL.md)
- [AI 使用示例](examples/ai_usage_example.md)
- [配置说明](config/README.md)
