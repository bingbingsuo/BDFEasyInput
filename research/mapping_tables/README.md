# BDF 映射表说明

## 文件说明

### 1. method_mapping.yaml
**用途**：计算方法映射表

**内容**：
- DFT 泛函映射（PBE0, B3LYP 等）
- SCF 方法类型映射（RHF, UHF, RKS, UKS）

**维护**：手动维护，添加新的方法

### 2. basis_mapping.yaml
**用途**：常用基组映射表

**内容**：
- 常用基组的标准名称到 BDF 基组名的映射
- 快速查找常用基组

**维护**：手动维护，添加常用基组

### 3. bdf_basis_list.yaml
**用途**：BDF 支持的完整基组列表

**内容**：
- 所有 BDF 支持的基组（从 BDF 基组名文件自动生成）
- 每个基组的属性（相对论优化、ECP）

**维护**：使用 `research/tools/generate_basis_list.py` 自动生成

**生成方法**：
```bash
python research/tools/generate_basis_list.py
```

### 4. keyword_mapping.yaml
**用途**：BDF 关键词映射表

**内容**：
- YAML 配置项到 BDF 关键词的映射
- 各模块的关键词说明

**维护**：手动维护，根据研究发现更新

## 基组列表生成

### 自动生成完整基组列表

BDF 基组名文件位置：`~/bdf/bdf-pkg-full/basis_library/basisname`

**文件格式**：
```
基组名    相对论优化    有效核势
cc-pvdz   no           no
def2-tzvp yes          no
lanl2dz   no           yes
```

**生成命令**：
```bash
cd research/tools
python generate_basis_list.py
```

**输出**：`research/mapping_tables/bdf_basis_list.yaml`

### 基组属性说明

- **relativistic** (相对论优化)
  - `true`: 基组对相对论效应进行了优化
  - `false`: 非相对论基组
  - **用途**：重元素计算

- **ecp** (有效核势)
  - `true`: 基组包含有效核势
  - `false`: 不包含 ECP
  - **用途**：大体系或重元素计算

## 使用建议

1. **常用基组**：使用 `basis_mapping.yaml` 快速查找
2. **完整列表**：使用 `bdf_basis_list.yaml` 查找所有支持的基组
3. **自动更新**：定期运行生成脚本更新基组列表

## 相关文档

- `research/mapping_tables/basis_mapping_guide.md` - 基组映射指南
- `research/tools/README.md` - 工具使用说明

