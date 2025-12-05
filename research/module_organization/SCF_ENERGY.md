# SCF 单点能量计算模块编排说明

## 概述

本文档说明如何根据 BDF 手册组织 SCF 单点能量计算的模块。参考手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/SCF.rst`

## 模块组合

对于 SCF 单点能量计算，BDF 高级输入模式的基本模块组合为：

```
$COMPASS
  [分子结构、基组、对称性等]
$END

$XUANYUAN
  [积分计算相关设置，对于RS泛函需要RS参数]
$END

$SCF
  [SCF方法类型、DFT泛函、电荷、自旋等]
$END
```

## 模块详细说明

### 1. COMPASS 模块

**作用**：定义分子结构、基组、对称性等基本设置

**必需内容**：
- `Geometry` ... `End geometry`：分子坐标（默认单位：Angstrom）
- `Basis`：基组名称

**可选内容**：
- `Title`：计算标题
- `Group`：点群对称性
- `NoSymm`：关闭对称性
- `Unit`：坐标单位（默认 Angstrom，可设置为 Bohr）
- `SAORB`：对称匹配轨道（仅当 MCSCF 或 TRAINT 模块存在，且未使用 RI 基组时）
- 其他 COMPASS 模块关键词

**注意事项**：
- 坐标默认单位为 **Angstrom**（不是 Bohr）
- 如果使用 `autofrag` 模块，COMPASS 必须在直角坐标下定义分子坐标，且不能用 `file=filename.xyz` 语法

### 2. XUANYUAN 模块

**作用**：积分计算相关设置

**基本用法**：
- 对于普通泛函（如 B3LYP、PBE0），XUANYUAN 模块可以为空：
  ```
  $XUANYUAN
  $END
  ```

**特殊用法（RS 泛函）**：
- 对于范围分离（Range-Separated）泛函（如 CAM-B3LYP），需要在 XUANYUAN 模块中设置 `RS` 参数：
  ```
  $XUANYUAN
  RS
    0.33   # CAM-B3lyp 默认的 mu 参数为 0.33
  $END
  ```
- 其他 RS 泛函的 mu 值见 XUANYUAN 模块的 `RSOMEGA` 关键词说明

**其他可选关键词**：
- `Direct`：直接积分模式
- `Maxmem`：最大内存
- 其他 XUANYUAN 模块关键词

### 3. SCF 模块

**作用**：SCF 计算的核心设置

**必需内容**：
- SCF 方法类型：`RHF`、`UHF`、`ROHF`、`RKS`、`UKS`、`ROKS` 之一
- `Charge`：分子电荷（必须显式指定）
- `Spin`：自旋多重度（必须显式指定）

**DFT 相关**：
- `dft functional [名称]`：指定 DFT 泛函（对于 RKS/UKS/ROKS）
  - 例如：`dft functional B3lyp`、`dft functional PBE0`、`dft functional CAM-B3lyp`

**可选内容**：
- `Occupied`：占据数（对于 RHF/RKS，指定不可约表示的双占据轨道数目）
- `Alpha`、`Beta`：Alpha/Beta 占据数（对于 UHF/UKS）
- `Grid`：积分格点类型（`Ultra Coarse`、`Coarse`、`Medium`、`Fine`、`Ultra Fine`）
- `Gridtol`：格点截断阈值
- `D3`：Grimme D3 色散矫正
- `FACEX`：自定义精确交换项成分（如将 B3LYP 的 20% 改为 15%）
- `FACCO`：自定义双杂化泛函的 MP2 相关项成分
- `Maxiter`：最大迭代次数
- **溶剂化效应**：`solvent`、`solmodel`、`cavity`、`nonels` 等（详见 `SOLVENT_MODELS.md`）
- 其他 SCF 模块关键词

## SCF 方法选择规则

### 基本规则

| YAML 配置 | BDF SCF 方法 |
|-----------|-------------|
| `method.type: hf, multiplicity: 1` | `RHF` |
| `method.type: hf, multiplicity > 1` | `UHF` |
| `method.type: dft, multiplicity: 1` | `RKS` |
| `method.type: dft, multiplicity > 1` | `UKS` |

### Spin-adapted TDDFT 场景

当 `settings.tddft.spin_adapted: true` 时：
- `method.type: hf` → `ROHF`
- `method.type: dft` → `ROKS`

## 完整示例

### 示例 1：RHF 单点能量计算

**YAML 输入**：
```yaml
task:
  type: energy

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: hf
  basis: cc-pvdz
```

**BDF 输入**：
```bdf
$COMPASS
Title
 Water single point energy calculation
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
$END

$XUANYUAN
$END

$SCF
RHF
Charge
 0
Spin
 1
$END
```

### 示例 2：RKS (B3LYP) 单点能量计算

**YAML 输入**：
```yaml
task:
  type: energy

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz
```

**BDF 输入**：
```bdf
$COMPASS
Title
 Water single point energy calculation, B3LYP
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
Charge
 0
Spin
 1
$END
```

### 示例 3：RKS (CAM-B3LYP) 单点能量计算（RS 泛函）

**YAML 输入**：
```yaml
task:
  type: energy

molecule:
  name: "1,3-Butadiene"
  charge: 0
  multiplicity: 1
  coordinates:
    - C -2.18046929 0.68443844 -0.00725330
    - H -1.64640852 -0.24200621 -0.04439369
    - H -3.24917614 0.68416040 0.04533562
    - C -1.50331750 1.85817167 -0.02681816
    - H -0.43461068 1.85844971 -0.07940766
    - C -2.27196552 3.19155924 0.02664018
    - H -3.34067218 3.19128116 0.07923299
    - C -1.59481380 4.36529249 0.00707382
    - H -2.12887455 5.29173712 0.04421474
    - H -0.52610710 4.36557056 -0.04551805
  units: angstrom

method:
  type: dft
  functional: cam-b3lyp
  basis: cc-pvdz

settings:
  xuanyuan:
    rs: 0.33  # CAM-B3lyp 默认的 mu 参数
```

**BDF 输入**：
```bdf
$COMPASS
Title
 1,3-Butadiene single point energy calculation, CAM-B3LYP
Basis
 cc-pvdz
Geometry
 C    -2.1805    0.6844   -0.0073
 H    -1.6464   -0.2420   -0.0444
 H    -3.2492    0.6842    0.0453
 C    -1.5033    1.8582   -0.0268
 H    -0.4346    1.8584   -0.0794
 C    -2.2720    3.1916    0.0266
 H    -3.3407    3.1913    0.0792
 C    -1.5948    4.3653    0.0071
 H    -2.1289    5.2917    0.0442
 H    -0.5261    4.3656   -0.0455
End geometry
$END

$XUANYUAN
RS
 0.33
$END

$SCF
RKS
dft functional
 CAM-B3lyp
Charge
 0
Spin
 1
$END
```

### 示例 4：UHF 单点能量计算（开壳层）

**YAML 输入**：
```yaml
task:
  type: energy

molecule:
  name: "C3H5 radical"
  charge: 0
  multiplicity: 2  # 奇数电子体系，默认多重度为 2
  coordinates:
    - C  0.00000000  0.00000000  0.00000000
    - C  0.00000000  0.00000000  1.45400000
    - C  1.43191047  0.00000000  1.20151555
    - H  0.73667537 -0.61814403 -0.54629970
    - H -0.90366611  0.32890757 -0.54629970
    - H  2.02151364  0.91459433  1.39930664
    - H  2.02151364 -0.91459433  1.39930664
    - H -0.79835551  0.09653770  2.15071009
  units: angstrom

method:
  type: hf
  basis: 3-21g
```

**BDF 输入**：
```bdf
$COMPASS
Title
 C3H5 radical single point energy calculation
Basis
 3-21G
Geometry
 C     0.0000    0.0000    0.0000
 C     0.0000    0.0000    1.4540
 C     1.4319    0.0000    1.2015
 H     0.7367   -0.6181   -0.5463
 H    -0.9037    0.3289   -0.5463
 H     2.0215    0.9146    1.3993
 H     2.0215   -0.9146    1.3993
 H    -0.7984    0.0965    2.1507
End geometry
$END

$XUANYUAN
$END

$SCF
UHF
Charge
 0
Spin
 2
$END
```

### 示例 5：RKS (B3LYP) + D3 色散矫正

**YAML 输入**：
```yaml
task:
  type: energy

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  scf:
    d3: true  # Grimme D3 色散矫正
```

**BDF 输入**：
```bdf
$COMPASS
Title
 Water single point energy calculation, B3LYP-D3
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 B3lyp
D3
Charge
 0
Spin
 1
$END
```

### 示例 6：RKS (M062X) + 高精度格点

**YAML 输入**：
```yaml
task:
  type: energy

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: m062x
  basis: cc-pvdz

settings:
  scf:
    grid: "ultra fine"  # Meta-GGA 泛函需要高精度格点
```

**BDF 输入**：
```bdf
$COMPASS
Title
 Water single point energy calculation, M062X
Basis
 cc-pvdz
Geometry
 O     0.0000    0.0000    0.1173
 H     0.0000    0.7572   -0.4692
 H     0.0000   -0.7572   -0.4692
End geometry
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 M062X
Grid
 Ultra Fine
Charge
 0
Spin
 1
$END
```

## 关键要点总结

1. **模块顺序**：必须按照 `COMPASS` → `XUANYUAN` → `SCF` 的顺序
2. **坐标单位**：BDF 默认使用 **Angstrom**（不是 Bohr）
3. **必需字段**：`Charge` 和 `Spin` 必须在 SCF 模块中显式指定
4. **RS 泛函**：对于 CAM-B3LYP 等范围分离泛函，需要在 XUANYUAN 模块中设置 `RS` 参数
5. **方法选择**：根据 `method.type` 和 `multiplicity` 自动选择 RHF/UHF/RKS/UKS
6. **DFT 泛函**：使用 `dft functional [名称]` 格式指定
7. **色散矫正**：使用 `D3` 关键词启用 Grimme D3 色散矫正
8. **格点精度**：Meta-GGA 泛函（如 M062X）建议使用 `Ultra Fine` 格点

## 实现建议

在转换器中，应该：

1. **模块组织**：
   ```python
   if task_type == 'energy':
       blocks.append(self.generate_compass_block(config))
       blocks.append(self.generate_xuanyuan_block(config))
       blocks.append(self.generate_scf_block(config))
   ```

2. **XUANYUAN 模块处理**：
   - 检查是否为 RS 泛函（如 CAM-B3LYP、LC-BLYP 等）
   - 如果是 RS 泛函，检查 `settings.xuanyuan.rs` 是否设置
   - 如果设置了，在 XUANYUAN 模块中添加 `RS` 关键词

3. **SCF 模块处理**：
   - 根据 `method.type` 和 `multiplicity` 选择方法类型
   - 对于 DFT，添加 `dft functional [名称]`
   - 必须添加 `Charge` 和 `Spin`
   - 处理其他可选关键词（Grid、D3、FACEX 等）

## 参考文档

- BDF SCF 手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/SCF.rst`
- COMPASS 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (compass 部分)
- XUANYUAN 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (xuanyuan 部分)
- SCF 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (scf 部分)

