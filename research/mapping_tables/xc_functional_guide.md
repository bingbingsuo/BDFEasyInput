# BDF XC 泛函使用指南

## 基本说明

### BDF 泛函处理方式

**重要**：BDF 根据用户输入的泛函名**直接匹配 libxc 的泛函**，**不做映射或重命名**。

这意味着：
- 用户输入的泛函名会**原样传递**给 BDF
- BDFEasyInput **不进行泛函名转换**
- 泛函名必须与 libxc 中定义的名称匹配

## 支持的输入格式

### 1. 单一交换相关泛函（XC Functional）

**格式**：直接使用泛函名称

**YAML 示例**：
```yaml
method:
  type: dft
  functional: B3LYP
```

**BDF 输出**：
```bdf
$SCF
RKS
dft functional
 B3LYP
$END
```

**常用单一泛函示例**：
- `B3LYP` - B3LYP 混合泛函
- `PBE0` - PBE0 混合泛函
- `PBEH` - PBEH（等同于 PBE0）
- `SCAN` - SCAN meta-GGA 泛函
- `TPSS` - TPSS meta-GGA 泛函

### 2. 交换 + 相关 组合泛函

**格式**：`"Xfun Cfun"`（两个泛函名用空格分隔）

**YAML 示例（字符串形式）**：
```yaml
method:
  type: dft
  functional: "PBE LYP"
```

**YAML 示例（结构化形式）**：
```yaml
method:
  type: dft
  functional:
    x: PBE
    c: LYP
```

**BDF 输出**：
```bdf
$SCF
RKS
dft functional
 PBE LYP
$END
```

**常用组合泛函示例**：
- `"PBE LYP"` - PBE 交换 + LYP 相关
- `"B88 LYP"` - B88 交换 + LYP 相关（BLYP）
- `"PBE PBE"` - PBE 交换 + PBE 相关
- `"B88 P86"` - B88 交换 + P86 相关

## 泛函名称规则

### 1. 大小写

- BDF 可能对泛函名大小写不敏感（需要验证）
- **建议**：使用标准大小写（如 `B3LYP`、`PBE`、`LYP`）

### 2. 空格

- 组合泛函中，交换和相关泛函名之间用**单个空格**分隔
- 不要在泛函名内部使用空格（除非是泛函名的一部分）

### 3. 泛函名来源

- 泛函名必须与 **libxc 库**中定义的名称匹配
- 完整的 libxc 泛函列表见：`research/mapping_tables/xc_functionals.yaml`
- 可以使用 `research/tools/query_xc_functionals.py` 查询支持的泛函

## 泛函验证（可选）

### 使用 libxc 列表验证

虽然 BDF 会直接匹配 libxc，但 BDFEasyInput 可以**可选地**进行验证：

1. **单一泛函验证**：
   - 检查泛函名是否在 libxc 的 XC 泛函列表中（`role: XC`）
   - 如果不在，给出警告但不阻止

2. **组合泛函验证**：
   - 检查交换泛函是否存在且 `role: X` 或 `role: XC`
   - 检查相关泛函是否存在且 `role: C` 或 `role: XC`
   - 如果不在，给出警告但不阻止

### 验证工具

```bash
# 查询所有 XC 泛函（单一泛函）
python research/tools/query_xc_functionals.py role XC

# 查询所有交换泛函
python research/tools/query_xc_functionals.py role X

# 查询所有相关泛函
python research/tools/query_xc_functionals.py role C

# 搜索特定泛函
python research/tools/query_xc_functionals.py search PBE
```

## 实现建议

### 泛函处理函数

```python
def process_functional(functional_input: Union[str, Dict]) -> str:
    """
    处理泛函输入，返回 BDF 格式的泛函字符串
    
    Args:
        functional_input: 
            - str: 单一泛函名或 "Xfun Cfun" 组合
            - Dict: {"x": "Xfun", "c": "Cfun"}
    
    Returns:
        BDF 格式的泛函字符串
    """
    if isinstance(functional_input, dict):
        # 结构化输入：{"x": "PBE", "c": "LYP"}
        x = functional_input.get("x", "")
        c = functional_input.get("c", "")
        if x and c:
            return f"{x} {c}"
        elif x:
            return x
        elif c:
            return c
        else:
            raise ValueError("Empty functional specification")
    else:
        # 字符串输入：直接返回
        return functional_input
```

### 可选验证函数

```python
def validate_functional(functional_str: str, xc_db: Dict) -> Tuple[bool, List[str]]:
    """
    验证泛函名是否在 libxc 列表中（可选，仅警告）
    
    Returns:
        (is_valid, warnings)
    """
    warnings = []
    
    parts = functional_str.split()
    if len(parts) == 1:
        # 单一泛函
        func_name = parts[0]
        found = False
        for macro, info in xc_db.items():
            if info.get('short_name') == func_name or macro.endswith(f'_{func_name}'):
                if info.get('role') == 'XC':
                    found = True
                    break
        if not found:
            warnings.append(f"Functional '{func_name}' not found in libxc XC functionals")
    elif len(parts) == 2:
        # 组合泛函
        x_func, c_func = parts
        # 验证交换泛函
        x_found = False
        c_found = False
        for macro, info in xc_db.items():
            if info.get('short_name') == x_func or macro.endswith(f'_{x_func}'):
                if info.get('role') in ('X', 'XC'):
                    x_found = True
            if info.get('short_name') == c_func or macro.endswith(f'_{c_func}'):
                if info.get('role') in ('C', 'XC'):
                    c_found = True
        if not x_found:
            warnings.append(f"Exchange functional '{x_func}' not found in libxc")
        if not c_found:
            warnings.append(f"Correlation functional '{c_func}' not found in libxc")
    
    return len(warnings) == 0, warnings
```

## 常见泛函映射参考

虽然 BDF 不做映射，但这里列出一些常见泛函的 libxc 名称，供参考：

### 单一泛函（XC）

| 用户输入 | libxc 宏名 | 说明 |
|---------|-----------|------|
| `B3LYP` | `XC_HYB_GGA_XC_B3LYP` | B3LYP 混合泛函 |
| `PBE0` | `XC_HYB_GGA_XC_PBEH` | PBE0（PBEH）混合泛函 |
| `PBEH` | `XC_HYB_GGA_XC_PBEH` | PBEH（等同于 PBE0） |
| `SCAN` | `XC_MGGA_XC_SCAN` | SCAN meta-GGA |
| `TPSS` | `XC_MGGA_XC_TPSS` | TPSS meta-GGA |

### 交换泛函（X）

| 用户输入 | libxc 宏名 | 说明 |
|---------|-----------|------|
| `PBE` | `XC_GGA_X_PBE` | PBE 交换 |
| `B88` | `XC_GGA_X_B88` | Becke 88 交换 |
| `B86` | `XC_GGA_X_B86` | Becke 86 交换 |

### 相关泛函（C）

| 用户输入 | libxc 宏名 | 说明 |
|---------|-----------|------|
| `LYP` | `XC_GGA_C_LYP` | Lee-Yang-Parr 相关 |
| `PBE` | `XC_GGA_C_PBE` | PBE 相关 |
| `P86` | `XC_GGA_C_P86` | Perdew 86 相关 |

## 注意事项

1. **直接匹配**：BDF 直接匹配 libxc，不做映射
2. **大小写**：建议使用标准大小写，但可能不敏感
3. **空格**：组合泛函中，交换和相关之间用单个空格
4. **验证**：BDFEasyInput 可以可选地验证，但不强制
5. **错误处理**：如果泛函名不匹配，BDF 会报错，BDFEasyInput 可以提前警告

---

**总结**：用户输入的泛函名会原样传递给 BDF，BDF 直接在 libxc 中匹配。BDFEasyInput 的主要作用是提供友好的输入格式和可选的验证。

