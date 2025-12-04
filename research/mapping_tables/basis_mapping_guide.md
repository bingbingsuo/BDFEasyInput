# 基组映射指南

## 基组数据来源

### 1. BDF 基组库（主要来源）

**文件位置**：`~/bdf/bdf-pkg-full/basis_library/basisname`

**文件格式**：
```
基组名    相对论优化    有效核势
cc-pVDZ    no    no
def2-TZVP    no    no
cc-pVDZ-DK    yes    no
```

**自动生成**：
使用 `research/tools/generate_basis_list.py` 自动生成完整列表。

### 2. 映射表（用户映射）

**文件位置**：`research/mapping_tables/basis_mapping.yaml`

**用途**：
- 建立标准基组名到 BDF 基组名的映射
- 添加别名支持
- 标记常用基组

## 基组信息字段

### bdf_name
- BDF 中使用的基组名称
- 直接用于 BDF 输入的 `Basis` 关键词
- 示例：`cc-pVDZ`、`6-31G*`

### relativistic
- `true`：相对论优化基组
- `false`：非相对论基组
- 用于重元素计算

### ecp
- `true`：包含有效核势（ECP）
- `false`：不包含 ECP
- 用于减少重元素的计算量

### aliases
- 别名列表
- 支持不同的命名习惯
- 示例：`["cc-pVDZ", "cc-pvdz", "CC-PVDZ"]`

### notes
- 备注信息
- 自动添加的特性说明
- 可以手动添加其他说明

## 使用流程

### 步骤 1：生成基组列表

```bash
# 从 BDF 基组库生成完整列表
python research/tools/generate_basis_list.py
```

这会生成 `bdf_basis_list.yaml`，包含所有 BDF 支持的基组。

### 步骤 2：建立映射关系

在 `basis_mapping.yaml` 中建立常用基组的映射：

```yaml
basis_sets:
  cc-pvdz:
    bdf_name: "cc-pVDZ"  # 从 bdf_basis_list.yaml 获取
    aliases: ["cc-pVDZ", "cc-pvdz"]
    notes: ["常用基组"]
```

### 步骤 3：在转换器中使用

```python
# 加载基组列表
with open('bdf_basis_list.yaml') as f:
    bdf_basis_list = yaml.safe_load(f)

# 加载映射表
with open('basis_mapping.yaml') as f:
    basis_mapping = yaml.safe_load(f)

# 查找基组
def find_basis(yaml_basis_name: str):
    # 1. 在映射表中查找
    # 2. 在基组列表中查找
    # 3. 返回 BDF 基组名
    pass
```

## 基组推荐策略

### 根据元素推荐

- **轻元素（H-Ar）**：标准基组即可
- **过渡金属**：可能需要相对论优化基组
- **重元素（> Kr）**：建议使用相对论优化基组或 ECP 基组

### 根据任务类型推荐

- **单点能**：可以使用较小基组
- **几何优化**：建议使用中等基组
- **频率计算**：建议使用中等或大基组
- **高精度计算**：使用大基组

## 注意事项

1. **基组名称大小写**：
   - BDF 可能不敏感，但建议使用标准名称
   - 从基组库中获取的标准名称

2. **相对论基组**：
   - 标记为 `relativistic: true` 的基组
   - 通常用于过渡金属和重元素

3. **ECP 基组**：
   - 标记为 `ecp: true` 的基组
   - 可以减少计算量，但可能影响精度

4. **基组验证**：
   - 转换前验证基组是否在 BDF 基组库中
   - 如果不在，给出警告或建议替代基组
