# BDF 基组列表总结

## 📊 基组统计

**生成日期**：2024年  
**数据来源**：`~/bdf/bdf-pkg-full/basis_library/basisname`

### 总体统计
- **总基组数**：391 个
- **相对论优化基组**：153 个
- **包含 ECP 的基组**：127 个

## 🔍 基组分类

### 1. 标准基组（非相对论，无 ECP）
- STO-3G, STO-6G
- 3-21G, 3-21++G
- 6-31G, 6-31G*, 6-31G**
- 6-311G, 6-311G*
- cc-pVDZ, cc-pVTZ, cc-pVQZ
- def2-SVP, def2-TZVP
- 等等

### 2. 相对论优化基组
- 后缀通常包含：`-DK`, `-DK3`, `-X2C`
- 示例：
  - `cc-pVDZ-DK`：相对论优化版本
  - `aug-cc-pVDZ-DK`：augmented + 相对论优化
  - `cc-pVDZ-X2C`：X2C 相对论方法

### 3. 包含 ECP 的基组
- 后缀通常包含：`-PP`, `-ccECP`
- 示例：
  - `cc-pVDZ-PP`：包含有效核势
  - `aug-cc-pVDZ-ccECP`：包含 ccECP

### 4. 相对论 + ECP 基组
- 同时包含相对论优化和 ECP
- 用于重元素的高效计算

## 📝 基组命名规律

### 常见后缀
- `-DK`：Douglas-Kroll 相对论方法
- `-DK3`：Douglas-Kroll 三阶
- `-X2C`：X2C 相对论方法
- `-PP`：有效核势（Pseudopotential）
- `-ccECP`：ccECP 有效核势
- `-FW_fi`：Fully-relativistic with finite nucleus
- `-FW_pt`：Fully-relativistic with point nucleus

### 常见前缀
- `aug-`：augmented（扩散函数）
- `t-aug-`：triple-augmented
- `cc-`：correlation-consistent
- `def2-`：Ahlrichs 基组系列

## 🔧 使用工具

### 生成基组列表

```bash
# 使用默认路径
python research/tools/generate_basis_list.py

# 指定路径
python research/tools/generate_basis_list.py /path/to/basisname output.yaml
```

### 查找基组

```bash
# 查找特定基组
grep "cc-pVDZ" research/mapping_tables/bdf_basis_list.yaml

# 查找相对论基组
grep "relativistic: true" research/mapping_tables/bdf_basis_list.yaml

# 查找 ECP 基组
grep "ecp: true" research/mapping_tables/bdf_basis_list.yaml
```

## 💡 基组选择建议

### 根据元素类型

1. **轻元素（H-Ar）**：
   - 标准基组：`cc-pVDZ`, `6-31G*`
   - 不需要相对论优化

2. **过渡金属**：
   - 建议使用相对论优化基组：`cc-pVDZ-DK`
   - 或使用 ECP 基组：`cc-pVDZ-PP`

3. **重元素（> Kr）**：
   - 强烈建议使用相对论优化基组
   - 或使用 ECP 基组减少计算量

### 根据计算类型

1. **单点能**：
   - 可以使用较小基组：`cc-pVDZ`, `6-31G*`

2. **几何优化**：
   - 建议使用中等基组：`cc-pVTZ`, `6-311G*`

3. **高精度计算**：
   - 使用大基组：`cc-pVQZ`, `aug-cc-pVTZ`

## 📋 常用基组映射

### 标准基组
- `cc-pvdz` → `cc-pVDZ`
- `cc-pvtz` → `cc-pVTZ`
- `6-31g*` → `6-31G*`
- `def2-svp` → `def2-SVP`

### 相对论基组
- `cc-pvdz-dk` → `cc-pVDZ-DK`
- `aug-cc-pvdz-dk` → `aug-cc-pVDZ-DK`

### ECP 基组
- `cc-pvdz-pp` → `cc-pVDZ-PP`
- `aug-cc-pvdz-pp` → `aug-cc-pVDZ-PP`

## 🔄 更新基组列表

当 BDF 更新后，重新运行生成工具：

```bash
python research/tools/generate_basis_list.py
```

这会更新 `bdf_basis_list.yaml` 文件，包含最新的基组信息。

---

**基组列表已成功生成！** 共 391 个基组，包括标准基组、相对论优化基组和 ECP 基组。

