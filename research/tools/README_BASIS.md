# BDF 基组管理说明

## BDF 基组库位置

**文件路径**：`~/bdf/bdf-pkg-full/basis_library/basisname`

## 文件格式

每行格式：
```
基组名    相对论优化标志    有效核势标志
```

示例：
```
cc-pVDZ    no    no
def2-TZVP    no    no
cc-pVDZ-DK    yes    no
cc-pVDZ-PP    no    yes
```

### 列说明

1. **第一列（基组名）**：
   - BDF 中使用的基组名称
   - 直接用于 BDF 输入的 `Basis` 关键词

2. **第二列（相对论优化）**：
   - `yes`：基组对相对论效应进行了优化
   - `no`：非相对论基组
   - 用于过渡金属等重元素计算

3. **第三列（有效核势）**：
   - `yes`：基组包含有效核势（ECP）
   - `no`：不包含 ECP
   - ECP 用于重元素，减少计算量

## 基组列表生成

### 自动生成工具

使用 `generate_basis_list.py` 从 BDF 基组库自动生成基组列表：

```bash
# 使用默认路径
python research/tools/generate_basis_list.py

# 指定路径
python research/tools/generate_basis_list.py /path/to/basisname output.yaml
```

### 生成的文件

工具会生成 `research/mapping_tables/bdf_basis_list.yaml`，包含：

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
```

## 基组映射策略

### 1. 标准名称映射

建立标准基组名（如 `cc-pvdz`）到 BDF 基组名的映射：

```yaml
basis_sets:
  cc-pvdz:
    bdf_name: "cc-pVDZ"  # 从 bdf_basis_list.yaml 获取
    aliases: ["cc-pVDZ", "cc-pvdz", "CC-PVDZ"]
```

### 2. 大小写处理

- BDF 基组名可能有不同大小写形式
- 建议统一使用 BDF 基组库中的标准名称
- 可以添加别名支持不同大小写

### 3. 相对论和 ECP 基组

- 对于重元素，可能需要相对论优化基组
- 对于大体系，可能需要 ECP 基组
- 在映射表中标记这些特性，便于推荐

## 使用建议

1. **首次使用**：
   ```bash
   python research/tools/generate_basis_list.py
   ```
   生成完整的基组列表

2. **更新基组列表**：
   - BDF 更新后，重新运行生成工具
   - 检查新增的基组

3. **添加映射**：
   - 在 `basis_mapping.yaml` 中添加常用基组的映射
   - 添加别名支持不同的命名习惯

4. **验证基组**：
   - 在转换前检查基组是否在 BDF 基组库中
   - 如果不在，给出警告或建议

## 实现建议

### 基组验证函数

```python
def validate_basis(basis_name: str, bdf_basis_list: Dict) -> bool:
    """验证基组是否在 BDF 基组库中"""
    # 检查直接匹配
    # 检查别名匹配
    # 返回是否有效
    pass

def get_basis_info(basis_name: str, bdf_basis_list: Dict) -> Dict:
    """获取基组信息（包括相对论、ECP 等）"""
    # 查找基组
    # 返回详细信息
    pass
```

### 基组推荐

```python
def recommend_basis(element: str, task_type: str) -> List[str]:
    """根据元素和任务类型推荐基组"""
    # 考虑元素（重元素需要相对论基组）
    # 考虑任务类型
    # 返回推荐列表
    pass
```

