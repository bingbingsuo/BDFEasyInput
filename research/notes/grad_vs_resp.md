# GRAD vs RESP 模块说明

## 重要区别

### GRAD 模块
- **仅支持 Hartree-Fock (HF) 和 MCSCF**
- **不支持 DFT 方法**
- 用于 HF 和 MCSCF 的梯度计算

### RESP 模块（推荐）
- **支持所有 SCF 方法**：HF 和 DFT
- **支持 TDDFT 梯度**
- **支持 Hessian 计算**（频率计算）
- **支持分子性质计算**

## 几何优化模块选择

### 推荐：使用 RESP 模块

**原因**：
1. RESP 模块支持所有 SCF 方法（HF 和 DFT）
2. GRAD 模块仅支持 HF 和 MCSCF，不支持 DFT
3. 对于 DFT 计算，必须使用 RESP 模块

**模块组合**：
```
$COMPASS
  [分子结构]
$END

$BDFOPT
  solver
    1
$END

$XUANYUAN
$END

$SCF
  [SCF 设置：RHF/UHF/RKS/UKS]
$END

$resp
  geom
  norder
    1
  method
    1  # 1=SCF梯度, 2=TDDFT梯度
$end
```

### 特殊情况：使用 GRAD 模块

**仅当**：
- 使用 Hartree-Fock 方法（RHF/UHF）
- 或使用 MCSCF 方法

**模块组合**：
```
$COMPASS
  [分子结构]
$END

$BDFOPT
  solver
    1
$END

$XUANYUAN
$END

$SCF
  RHF  # 或 UHF
$END

$GRAD
$END
```

## RESP 模块参数说明

### norder
- `1`：计算梯度（用于几何优化）
- `2`：计算 Hessian（用于频率计算）

### method
- `1`：SCF 梯度（HF/DFT）
- `2`：TDDFT 梯度

### geom
- 无值关键词
- 表示用于几何优化

## 实现建议

### 自动选择模块

```python
def get_gradient_module(method_type: str) -> str:
    """
    根据方法类型选择梯度模块
    
    Args:
        method_type: 'hf' 或 'dft' 或 'mcscf'
    
    Returns:
        'RESP' 或 'GRAD'
    """
    if method_type == 'hf':
        # HF 可以使用 GRAD 或 RESP
        # 为了统一，建议使用 RESP
        return 'RESP'
    elif method_type == 'dft':
        # DFT 必须使用 RESP
        return 'RESP'
    elif method_type == 'mcscf':
        # MCSCF 可以使用 GRAD 或 RESP
        # 为了统一，建议使用 RESP
        return 'RESP'
    else:
        # 默认使用 RESP
        return 'RESP'
```

### 生成 RESP 模块

```python
def generate_resp_module(task_type: str, method_type: str) -> str:
    """
    生成 RESP 模块
    
    Args:
        task_type: 'optimize' 或 'frequency'
        method_type: 'dft' 或 'hf' 或 'tddft'
    
    Returns:
        RESP 模块字符串
    """
    lines = ["$resp"]
    
    if task_type == 'optimize':
        lines.append("geom")
        lines.append("norder")
        lines.append("1")
        
        if method_type == 'tddft':
            lines.append("method")
            lines.append("2")
        else:
            lines.append("method")
            lines.append("1")
    
    elif task_type == 'frequency':
        lines.append("norder")
        lines.append("2")
        lines.append("method")
        lines.append("1")
    
    lines.append("$end")
    
    return "\n".join(lines)
```

## 总结

- **几何优化**：使用 RESP 模块（推荐），GRAD 模块仅用于 HF/MCSCF
- **DFT 计算**：必须使用 RESP 模块
- **频率计算**：使用 RESP 模块（`norder 2`）
- **TDDFT 梯度**：使用 RESP 模块（`method 2`）

---

**建议**：为了统一和兼容性，所有几何优化都使用 RESP 模块。

