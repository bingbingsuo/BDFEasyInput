# BDF 基组使用说明

## 概述

本文档说明如何在 BDF 中使用高斯基组。参考手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Gaussian-Basis-Sets.rst`

## 重要说明

### 球基函数 vs 笛卡尔基函数

**BDF 一律采用球基函数（spherical basis functions）**：

1. 除 Pople 型等较早的基组外，大多数现代高斯基组都是在球基函数下优化的
2. 笛卡尔基函数无论在精度上还是在效率上均无优势，尤其是对于全电子相对论计算还会导致数值不稳定
3. 笛卡尔基函数和球基函数会导致不同的结果。如果用其它量子化学程序重复 BDF 的计算结果，除保证结构、方法、基组相同外，还需检查是否用了球基函数

### 基组数据来源

BDF 内置的高斯基组主要来自以下基组库网站：

- **Basis Set Exchange**：全电子基组，标量ECP基组
- **Stuttgart/Cologne赝势基组库**：主要是SOECP基组和"f-in-core"基组
- **Turbomole基组库**：全电子基组，标量ECP基组，SOECP基组
- **Dyall相对论基组**：全电子相对论基组
- **Sapporo基组库**：全电子基组
- **Clarkson大学ECP基组库**：SOECP基组
- **ccECP基组库**：标量ECP基组；Kr之后是SOECP基组
- **ccRepo基组库**：最新开发的关联一致基组

## 基组类型

### 1. 全电子基组

**分类**：
- 非收缩基组：既可用于非相对论计算也可用于相对论计算，但主要是相对论计算
- 收缩基组：
  - 非相对论收缩基组
  - 相对论收缩基组（DKH、ZORA、X2C等）

**常见基组系列**：
- **Pople 系列**：STO-3G, 3-21G, 6-31G, 6-311G 等
- **关联一致基组（cc-pVnZ）**：cc-pVDZ, cc-pVTZ, cc-pVQZ, cc-pV5Z 等
- **ANO 基组**：ANO-RCC, ANO-R 等
- **Ahlrichs 基组**：def2-SVP, def2-TZVP, def2-QZVP 等
- **Sapporo 基组**：Sapporo-DZP, Sapporo-TZP, Sapporo-QZP 等

**相对论基组**：
- DKH 相对论基组：cc-pVDZ-DK, cc-pVTZ-DK 等
- X2C 相对论基组：cc-pVDZ-X2C, cc-pVTZ-X2C 等
- DKH3 相对论基组：cc-pVDZ-DK3, cc-pVTZ-DK3 等

### 2. 赝势基组（ECP基组）

**分类**：
- **标量赝势基组**：不包含旋轨耦合项
- **旋轨耦合赝势基组（SOECP）**：包含旋轨耦合项

**常见基组系列**：
- **cc-pVnZ-PP 系列**：cc-pVDZ-PP, cc-pVTZ-PP 等（SOECP）
- **Def2 系列**：def2-SVP, def2-TZVP 等（部分元素为全电子，部分为赝势）
- **LANL 系列**：LANL2DZ, LANL2TZ 等
- **Stuttgart 系列**：Stuttgart-RLC, Stuttgart-RSC 等

**注意**：
- 赝势基组需要结合赝势使用，基函数只描述原子的价层电子
- 当体系涉及到比较重的原子时，可以对它们用赝势基组，而其它原子照常用普通的非相对论全电子基组

## 基组指定方式

### 方式 1：对所有原子使用相同的 BDF 内置基组

**高级输入模式**：
```bdf
$COMPASS
Basis
 cc-pvdz
Geometry
 ...
End geometry
$END
```

**YAML 输入**：
```yaml
method:
  basis: cc-pvdz
```

**说明**：
- 基组名称大小写不敏感
- 基组名称直接使用 BDF 内置基组名
- 所有原子使用相同的基组

### 方式 2：为不同元素指定不同基组

**BDF 输入**：
```bdf
$COMPASS
Basis-block
 lanl2dz
 H = 3-21g
 Cl = cc-pvdz
End Basis
Geometry
 H   0.000   0.000    0.000
 Cl  0.000   0.000    1.400
End geometry
$END
```

**YAML 输入**（建议格式）：
```yaml
method:
  basis: lanl2dz  # 默认基组

settings:
  compass:
    basis:
      block:
        default: lanl2dz
        elements:
          H: 3-21g
          Cl: cc-pvdz
```

**说明**：
- 第一行是默认基组
- 之后的行对不同元素指定其它基组，格式为 `元素=基组名`
- 多个元素可以使用相同基组：`元素1,元素2,...,元素n=基组名`
- 必须以 `End Basis` 作为结束

### 方式 3：为同种元素的不同原子指定不同基组

**BDF 输入**：
```bdf
$COMPASS
Basis-block
 6-31g
 H1= cc-pvdz
 H2= 3-21g
End basis
Geometry
 C       0.000   -0.000    0.000
 H1     -0.000   -1.009   -0.357
 H2     -0.874    0.504   -0.457
 H1      0.874    0.504   -0.357
 H2      0.000    0.000    1.200
End geometry
$END
```

**说明**：
- 在坐标中定义原子类型时，需要在元素符号后加上数字以示区分（如 H1, H2）
- 必须在 Basis-block 中为这些原子类型明确指定基组
- **对称等价原子必须使用相同基组**，程序将对此进行检查
- 如果对称等价原子必须要使用不同基组，可通过 `Group` 设置较低的点群对称性，或者用 `Nosymm` 关闭对称性

### 方式 4：在输入文件中提供基组数据（inline）

**BDF 输入**：
```bdf
$COMPASS
Basis-block
 sto-3g
 inline
 # Pitzer-cc-pVDZ-PP for F
   F       9    2
   S       4    3
              52.19000000
               9.33900000
               1.18100000
               0.36250000
       -0.0097379000     0.0000000000     0.0000000000
       -0.1335636000     0.0000000000     0.0000000000
        0.6014362000     0.0000000000     1.0000000000
        0.5072134000     1.0000000000     0.0000000000
   P       4    2
   ...
 end line
End Basis
Geometry
 ...
End geometry
$END
```

**说明**：
- 使用 `inline` ... `end line` 数据区提供基组数据
- 基组数据格式与自定义基组文件格式相同
- 适用于临时使用非标准基组的情况

### 方式 5：使用自定义基组文件

**步骤**：
1. 在计算目录下创建基组文件，**文件名必须全部大写**（如 `MYBAS-1`）
2. 文件内容格式见手册
3. 在 BDF 输入中引用：

```bdf
$COMPASS
Basis
 mybas-1  # 引用时大小写任意
Geometry
 ...
End geometry
$END
```

**注意**：
- 自定义基组文件必须用 BDF 的混合模式输入
- 在简洁输入模式下，第二行输入基组设置为 `genbas`
- 在高级输入模式下，使用 `Basis` 关键词指定文件名

## 辅助基组（RI 基组）

### 用途

使用密度拟合近似（RI）的方法需要一个辅助的基组，用于加速计算。

### 关键词

- **RI-J**：库伦拟合基组
- **RI-K**：交换拟合基组
- **RI-C**：相关拟合基组

### 使用示例

```bdf
$COMPASS
Basis
 DEF2-SVP
RI-J
 DEF2-SVP
Geometry
 ...
End geometry
$END
```

**YAML 输入**：
```yaml
method:
  basis: def2-svp

settings:
  compass:
    ri:
      ri_j_basis: def2-svp
```

### 注意事项

1. **RI 计算主要用于 MCSCF、MP2 等波函数计算方法**
2. **不推荐在 SCF、TDDFT 等计算中使用 RI**
3. 对于 SCF、TDDFT 计算，推荐使用多级展开库伦势（MPEC）方法，MPEC 方法不依赖辅助基组，计算速度和精度都与 RI 方法相当
4. 高级别密度拟合基组可以用在低级别基组上（如 `cc-pVTZ/C` 可以用于在 `cc-pVTZ` 上做 RI-J）
5. 反之，高级别轨道基组结合低级别的辅助基组则会带来较明显的误差

## 基组别名和缩写

BDF 支持部分基组的别名和缩写：

### 基本规则

1. **6-系列 Pople 基组**：代表极化函数的后缀 P、PP 可以用星号表示
   - 例如：`6-311++G**` 等同于 `6-311++GPP`

2. **def2-系列基组**：连字符 "-" 可以省略
   - 例如：`def2-SVP` 可以写为 `def2SVP`

3. **关联一致基组**：
   - `cc-pV` 可简写为 `V`
   - `cc-pCV` 可简写为 `CV`
   - `cc-pwCV` 可简写为 `WCV`
   - 前缀 `aug-` 可缩写为 `A`（不区分大小写）
   - 例如：`vdz` 表示 `cc-pVDZ`，`awcvtz-dk` 表示 `aug-cc-pwCVTZ-DK`

**注意**：这种基组名的缩写仅限用于 BDF 的输入，不要用在正式的论文和报告中，以免造成读者困惑。

## 基组选择建议

### 根据计算类型选择

1. **非相对论计算**：使用标准全电子基组（如 cc-pVDZ, def2-SVP 等）
2. **相对论计算**：使用相对论优化基组（如 cc-pVDZ-DK, cc-pVDZ-X2C 等）
3. **重元素计算**：考虑使用赝势基组（如 cc-pVDZ-PP, def2-TZVP 等）

### 根据精度要求选择

- **快速计算**：小基组（如 3-21G, STO-3G）
- **标准计算**：中等基组（如 cc-pVDZ, def2-SVP）
- **高精度计算**：大基组（如 cc-pVTZ, cc-pVQZ, def2-TZVP, def2-QZVP）

### 根据元素类型选择

- **轻元素（H-Ar）**：全电子基组
- **过渡金属**：相对论基组或赝势基组
- **重元素（Kr之后）**：赝势基组（SOECP）

## 实现建议

### 在转换器中的处理

1. **统一基组**：
   ```python
   basis = config.get('method', {}).get('basis', '')
   if basis:
       lines.append("Basis")
       lines.append(f" {basis}")
   ```

2. **多基组（Basis-block）**：
   ```python
   basis_block = settings.get('compass', {}).get('basis', {}).get('block', {})
   if basis_block:
       lines.append("Basis-block")
       default = basis_block.get('default', '')
       if default:
           lines.append(f" {default}")
       elements = basis_block.get('elements', {})
       for element, basis_name in elements.items():
           lines.append(f" {element} = {basis_name}")
       lines.append("End Basis")
   ```

3. **辅助基组（RI）**：
   ```python
   ri_settings = settings.get('compass', {}).get('ri', {})
   if ri_settings.get('ri_j_basis'):
       lines.append("RI-J")
       lines.append(f" {ri_settings['ri_j_basis']}")
   # 类似处理 RI-K 和 RI-C
   ```

## 参考文档

- BDF 基组手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Gaussian-Basis-Sets.rst`
- COMPASS 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (compass 部分)
- 基组映射表：`research/mapping_tables/basis_mapping.yaml`

