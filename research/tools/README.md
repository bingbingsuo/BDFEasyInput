# BDF 研究工具

本目录包含用于 BDF 输入格式研究的工具脚本。

## 工具列表

### generate_xc_functional_list.py

**功能**：从 BDF libxc 头文件自动生成泛函列表

**使用方法**：

```bash
# 使用默认路径
python research/tools/generate_xc_functional_list.py

# 指定输入文件
python research/tools/generate_xc_functional_list.py /path/to/xc_funcs.h

# 指定输入和输出文件
python research/tools/generate_xc_functional_list.py /path/to/xc_funcs.h output.yaml
```

**默认路径**：
- 输入文件：`~/bdf/BDFAutoTest/bdf-pkg-full/build/include/xc_funcs.h`
- 输出文件：`research/mapping_tables/xc_functionals.yaml`

**输出格式**：
- YAML 格式，包含所有 libxc 支持的泛函
- 每个泛函包含：ID、宏名、家族（LDA/GGA/MGGA/HYB_*）、角色（X/C/XC/K）、描述

**相关工具**：
- `query_xc_functionals.py` - 查询和搜索泛函列表

---

### query_xc_functionals.py

**功能**：查询和搜索 XC 泛函列表

**使用方法**：

```bash
# 列出所有泛函
python research/tools/query_xc_functionals.py list

# 按家族查询
python research/tools/query_xc_functionals.py family GGA
python research/tools/query_xc_functionals.py family HYB_GGA

# 按角色查询
python research/tools/query_xc_functionals.py role XC  # 交换相关泛函
python research/tools/query_xc_functionals.py role X   # 交换泛函
python research/tools/query_xc_functionals.py role C   # 相关泛函

# 搜索泛函
python research/tools/query_xc_functionals.py search PBE
python research/tools/query_xc_functionals.py search B3LYP
```

---

### generate_basis_list.py

**功能**：从 BDF 基组库自动生成基组列表

**使用方法**：

```bash
# 使用默认路径
python research/tools/generate_basis_list.py

# 指定输入文件
python research/tools/generate_basis_list.py /path/to/basisname

# 指定输入和输出文件
python research/tools/generate_basis_list.py /path/to/basisname output.yaml
```

**默认路径**：
- 输入文件：`~/bdf/bdf-pkg-full/basis_library/basisname`
- 输出文件：`research/mapping_tables/bdf_basis_list.yaml`

**文件格式**：

BDF 基组名文件格式（`basisname`）：
```
基组名1    yes/no    yes/no
基组名2    yes/no    yes/no
...
```

- 第一列：基组名
- 第二列：相对论优化标志（yes = 相对论优化，no = 非相对论）
- 第三列：有效核势标志（yes = 包含 ECP，no = 不包含）

**输出格式**：

生成的 YAML 文件包含：
- `version`: 版本号
- `source`: 数据来源
- `total_basis_sets`: 基组总数
- `basis_sets`: 基组字典
  - `bdf_name`: BDF 中的基组名称
  - `relativistic`: 是否为相对论优化基组
  - `ecp`: 是否包含有效核势
  - `aliases`: 别名列表
  - `notes`: 备注信息

**示例输出**：

```yaml
version: "1.0"
source: "BDF basis library"
total_basis_sets: 150
basis_sets:
  cc_pvdz:
    bdf_name: "cc-pVDZ"
    relativistic: false
    ecp: false
    aliases: ["cc-pVDZ"]
    notes: []
  def2_tzvp:
    bdf_name: "def2-TZVP"
    relativistic: false
    ecp: false
    aliases: ["def2-TZVP"]
    notes: []
```

## 依赖

- Python 3.8+
- PyYAML

## 使用场景

1. **初始生成**：首次从 BDF 基组库生成完整列表
2. **更新列表**：BDF 更新后重新生成列表
3. **验证基组**：检查某个基组是否在 BDF 基组库中

## 注意事项

1. 确保 BDF 已正确安装
2. 确保可以访问基组名文件
3. 生成的文件可以手动编辑添加别名和映射关系
