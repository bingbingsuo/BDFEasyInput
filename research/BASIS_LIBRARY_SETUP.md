# BDF 基组库设置完成

## ✅ 已完成的工作

### 1. 基组列表生成工具

**文件**：`research/tools/generate_basis_list.py`

**功能**：
- 从 BDF 基组库文件读取基组信息
- 解析基组名、相对论标志、ECP 标志
- 生成 YAML 格式的基组列表

**使用方法**：
```bash
# 使用默认路径
python research/tools/generate_basis_list.py

# 指定路径
python research/tools/generate_basis_list.py /path/to/basisname output.yaml
```

### 2. 生成的基组列表

**文件**：`research/mapping_tables/bdf_basis_list.yaml`

**统计信息**：
- **总基组数**：391 个
- **相对论优化基组**：153 个
- **包含 ECP 的基组**：127 个

**文件格式**：
```yaml
version: '1.0'
source: BDF basis library
total_basis_sets: 391
basis_sets:
  cc_pvdz:
    bdf_name: cc-pVDZ
    relativistic: false
    ecp: false
    aliases: [cc-pVDZ]
    notes: []
  cc_pvdz_dk:
    bdf_name: cc-pVDZ-DK
    relativistic: true
    ecp: false
    aliases: [cc-pVDZ-DK]
    notes: []
```

### 3. 文档

已创建以下文档：
- `research/tools/README.md` - 工具使用说明
- `research/tools/README_BASIS.md` - 基组管理详细说明
- `research/mapping_tables/basis_mapping_guide.md` - 基组映射指南
- `research/mapping_tables/basis_list_summary.md` - 基组列表总结

## 📋 BDF 基组库文件格式

**文件位置**：`~/bdf/bdf-pkg-full/basis_library/basisname`

**格式**：
```
基组名    相对论标志    有效核势标志
STO-3G    no          no
cc-pVDZ   no          no
cc-pVDZ-DK   yes      no
cc-pVDZ-PP   no       yes
```

**列说明**：
1. **第一列**：基组名（BDF 中使用的名称）
2. **第二列**：相对论优化标志（yes/no）
3. **第三列**：有效核势标志（yes/no）

## 🔧 使用流程

### 步骤 1：生成基组列表

```bash
cd /Users/bsuo/bdf/BDFEasyInput
python research/tools/generate_basis_list.py
```

### 步骤 2：查看基组列表

```bash
# 查看总览
cat research/mapping_tables/bdf_basis_list.yaml | head -20

# 查找特定基组
grep "cc-pVDZ" research/mapping_tables/bdf_basis_list.yaml

# 查找相对论基组
grep "relativistic: true" research/mapping_tables/bdf_basis_list.yaml
```

### 步骤 3：在转换器中使用

```python
import yaml

# 加载基组列表
with open('research/mapping_tables/bdf_basis_list.yaml') as f:
    basis_list = yaml.safe_load(f)

# 查找基组
def find_basis(basis_name: str):
    # 在列表中查找
    for key, info in basis_list['basis_sets'].items():
        if info['bdf_name'] == basis_name or basis_name in info['aliases']:
            return info
    return None

# 验证基组
def validate_basis(basis_name: str) -> bool:
    return find_basis(basis_name) is not None
```

## 📊 基组分类示例

### 标准基组
- `cc-pVDZ`：标准相关一致基组
- `6-31G*`：标准 Pople 基组
- `def2-SVP`：标准 Ahlrichs 基组

### 相对论优化基组
- `cc-pVDZ-DK`：Douglas-Kroll 相对论方法
- `cc-pVDZ-X2C`：X2C 相对论方法
- `aug-cc-pVDZ-DK`：augmented + 相对论

### ECP 基组
- `cc-pVDZ-PP`：包含有效核势
- `aug-cc-pVDZ-PP`：augmented + ECP

## 🔄 更新基组列表

当 BDF 更新后，重新运行生成工具：

```bash
python research/tools/generate_basis_list.py
```

这会更新 `bdf_basis_list.yaml` 文件。

## 💡 下一步

1. **建立映射关系**：在 `basis_mapping.yaml` 中建立常用基组的映射
2. **添加别名**：为常用基组添加别名支持
3. **基组验证**：在转换器中添加基组验证功能
4. **基组推荐**：根据元素和任务类型推荐基组

---

**基组库设置已完成！** 现在可以使用生成的基组列表进行基组映射和验证。

