# SCF Occupied 关键词说明

## 基本信息

- **关键词**：`Occupied`
- **位置**：SCF 模块（RHF 或 RKS）
- **格式**：四个整数，空格分隔（如 `3 0 1 0`）

## 含义

指定 RHF 或 RKS 计算时不可约表示的双占据轨道数目。

- 采用 **D2h 及其子群**的对称性
- 四个整数分别对应不同不可约表示的双占据轨道数

## 使用规则

### 1. 默认行为（推荐）

**如果用户不指定 `Occupied` 值**：
- 不在 BDF 输入中输出 `Occupied` 关键词
- 让 BDF 自动计算占据轨道数
- 这是最简单和推荐的方式

### 2. 用户指定值

**如果用户在 YAML 中指定了值**：
```yaml
settings:
  scf:
    occupied: [3, 0, 1, 0]  # 或 "3 0 1 0"
```

**转换规则**：
- 直接使用用户提供的值
- 转换为 BDF 格式：`Occupied\n3 0 1 0`
- 不进行任何计算或验证

## YAML 格式支持

### 选项 1：列表格式
```yaml
settings:
  scf:
    occupied: [3, 0, 1, 0]
```

### 选项 2：字符串格式
```yaml
settings:
  scf:
    occupied: "3 0 1 0"
```

### 选项 3：不指定（推荐）
```yaml
settings:
  scf:
    # occupied 不指定，让 BDF 自动计算
```

## 转换示例

### 示例 1：用户不指定（默认）

**YAML**：
```yaml
method:
  type: hf
settings:
  scf:
    convergence: 1e-6
```

**BDF**：
```bdf
$SCF
RHF
$END
```
（不输出 `Occupied`，让 BDF 自动计算）

### 示例 2：用户指定值

**YAML**：
```yaml
method:
  type: hf
settings:
  scf:
    occupied: [3, 0, 1, 0]
```

**BDF**：
```bdf
$SCF
RHF
Occupied
3 0 1 0
$END
```

## 注意事项

1. **仅用于 RHF/RKS**：
   - RHF 和 RKS 使用 `Occupied`
   - UHF 和 UKS 使用 `Alpha` 和 `Beta`，不使用 `Occupied`

2. **对称性**：
   - 基于 D2h 及其子群
   - 四个整数对应不同不可约表示

3. **默认行为**：
   - 不指定时，BDF 会自动计算
   - 这是推荐的方式，除非用户有特殊需求

4. **用户输入验证**：
   - 应该验证用户输入是四个整数
   - 但不需要验证值的合理性（让 BDF 处理）

## 实现建议

```python
def generate_scf_occupied(settings: Dict) -> Optional[str]:
    """
    生成 SCF Occupied 关键词
    
    Args:
        settings: settings.scf 配置
    
    Returns:
        如果用户指定了值，返回格式化的字符串；否则返回 None
    """
    occupied = settings.get("occupied")
    
    if occupied is None:
        # 不输出 Occupied，让 BDF 自动计算
        return None
    
    # 处理用户输入
    if isinstance(occupied, list):
        # 列表格式：[3, 0, 1, 0]
        values = " ".join(str(v) for v in occupied)
    elif isinstance(occupied, str):
        # 字符串格式："3 0 1 0"
        values = occupied
    else:
        raise ValueError(f"Invalid occupied format: {occupied}")
    
    return f"Occupied\n{values}"
```

