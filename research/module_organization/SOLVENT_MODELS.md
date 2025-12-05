# BDF 溶剂化模型使用说明

## 概述

BDF 支持隐式溶剂模型（连续介质模型）和显式溶剂模型（QM/MM）。本文档主要介绍隐式溶剂模型的使用。

**参考手册**：
- `/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Solvent-Model.rst`
- `/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Solvent-Dielectric.rst`

## 支持的溶剂模型

BDF 支持以下连续介质模型：

| 模型 | 关键词 | 基态 | 激发态 |
|------|--------|------|--------|
|      |        | 单点 | 梯度 | Hessian | 单点 | 梯度 |
|------|--------|------|------|---------|------|------|
| **COSMO** | `cosmo` | √ | √ | √ | √ | √ |
| **CPCM** | `cpcm` | √ | √ | √ | √ | √ |
| **SS(V)PE** | `ssvpe` | √ | √ | √ | √ | √ |
| **IEFPCM** | `iefpcm` | √ | √ | √ | √ | √ |
| **SMD** | `smd` | √ | √ | √ | √ | √ |
| **ddCOSMO** | `ddcosmo` | √ | √ | √ | √ | √ |

**默认模型**：未指定时，默认使用 IEFPCM 模型。

## 基本使用方法

### 1. 基态溶剂化能计算

在 `SCF` 模块中添加 `solvent` 和 `solmodel` 关键词：

```bdf
$SCF
rks
dft functional
  b3lyp
solvent   # 溶剂化计算开关
  water   # 指定溶剂
solmodel  # 指定溶剂化模型
  smd
$END
```

### 2. 溶剂类型指定

#### 方法 1：使用预定义溶剂名称

```bdf
solvent
  water    # 使用预定义的溶剂名称
```

支持的溶剂名称列表见 `Solvent-Dielectric.rst`，包括：
- `water`、`methanol`、`ethanol`、`acetonitrile`、`dmso`、`thf` 等
- 可以使用完整名称或短名称（如 `H2O` 代表 `water`）

#### 方法 2：用户指定介电常数

```bdf
solvent
  user     # 用户指定
dielectric
  78.3553  # 输入介电常数
```

对于非平衡溶剂化效应计算，还需要指定光介电常数：

```bdf
solvent
  user
dielectric
  78.3553
opticalDielectric
  1.7778   # 光介电常数
```

### 3. 溶剂模型设置

```bdf
solmodel
  IEFPCM   # 溶剂模型：cosmo, cpcm, iefpcm, ssvpe, smd, ddcosmo
```

**COSMO 和 CPCM 的特殊参数**：

```bdf
cosmoFactorK
  0.5  # 介电屏蔽因子 f_ε = (ε-1)/(ε+k) 中的 k
       # COSMO 默认 k=0.5，CPCM 默认 k=0
```

**SMD 模型的特殊参数**：

```bdf
refractiveIndex          # 折射率
  1.43
HBondAcidity            # Abraham 氢键酸度
  0.229
HBondBasicity            # Abraham 氢键碱度
  0.265
SurfaceTensionAtInterface # 表面张力
  61.24
CarbonAromaticity        # 芳香度
  0.12
ElectronegativeHalogenicity # 卤素度
  0.24
```

**注意**：使用 SMD 模型将关闭非静电溶剂化能的计算，取而代之将计算 SMx 系列的 ΔG_CDS。

## 孔穴自定义设置

连续介质模型根据溶质分子形成孔穴，孔穴的形状会对溶剂化能的计算产生较大影响。

### 基本孔穴参数

```bdf
cavity          # 生成孔穴表面的方式
  swig          # swig | switching | ses | sphere，默认为 swig
uatm            # 联合原子拓扑方法
  false         # false | true，默认为 false
radiusType      # 半径类型
  UFF           # UFF | Bondi，默认为 UFF
vdWScale        # vdW 半径缩放因子
  1.1           # 默认 1.1，即 1.1 倍 RadiusType 半径
```

**cavity 选项说明**：
- `switching`：用平滑函数来处理 vdW 表面的格点权重
- `swig`：switching/gaussian，即在 switching 的基础上再使用高斯函数对格点处的点电荷做平滑处理（默认）
- `ses`：solvent-excluded surface
- `sphere`：形成一个圆球状的孔穴来包裹整个分子

### 自定义原子半径

```bdf
radii           # 自定义原子半径（单位：Å）
  1=1.4430 2=1.7500  # 第一个原子的半径设为 1.4430Å，第二个原子的半径设为 1.7500Å
  # 等号间不能有空格，一行最多 128 字符，一行写不下可以加上 radii 之后新增一行
  # radii 的设置会覆盖 vdWScale*RadiusType 中相同原子的设置
radii
  H=1.4430 O=1.7500  # 也可以按元素符号指定，两种方式可以混合使用
acidHRadius     # 单独设置酸性 H 半径，单位 Å
  1.2
```

### 孔穴格点精度

```bdf
cavityNGrid     # 控制每个原子生成的孔穴表面的格点数，会自动调整至最近的 lebedev 格点
  302           # 默认为 302

# 或者

cavityPrecision # 格点精度
  medium        # ultraCoarse | coarse | medium | fine | ultraFine，默认为 medium
```

## 非静电溶剂化能计算

溶剂化自由能包括静电溶剂化能以及非静电溶剂化能。PCM 模型计算了静电溶剂化能，非静电溶剂化能包括孔穴能（ΔG_cav）和色散-排斥能（ΔG_dis-rep）。

### 开启非静电溶剂化能

```bdf
nonels          # 开启非静电溶剂化能计算
  dis rep cav   # 色散能 排斥能 孔穴能
solventAtoms    # 溶剂分子的各类型原子的个数（分子式）
  H2O1          # 默认为 H2O1，不能省略 1，因为不区分大小写后无法确定元素符号是几个字母
solventRho      # 溶剂分子数密度，单位 molecules Å^-3
  0.03333
solventRadius   # 溶剂分子半径，单位 Å
  1.385
```

**注意事项**：
- 指定 `cav` 时，除非 `solvent` 指定为 `water` 会自动使用默认值，其他溶剂必须手动指定 `solventRho`、`solventRadius`
- 指定 `rep` 或 `dis` 时，除非 `solvent` 指定为 `water` 会自动使用默认值，其他溶剂必须手动指定 `solventRho`、`solventAtoms`

### 常见溶剂的分子半径

| 溶剂 | 半径 (Å) |
|------|----------|
| Water | 1.385 |
| Tetrahydrofuran | 2.900 |
| Cyclohexane | 2.815 |
| Methanol | 1.855 |
| Ethanol | 2.180 |
| Tetrachloromethane | 2.685 |

### 自定义非静电能计算的半径

```bdf
solventAtomicSASRadii  # 计算色散排斥能时，构建 SAS 孔穴的溶剂分子中每类原子的半径
  H=1.20 O=1.50
radiiForCavEnergy      # 计算孔穴能的溶质半径
  H=1.4430 O=1.7500    # 注意事项同 radii
acidHRadiusForCavEnergy # 计算孔穴能的溶质半径，单独设置酸性 H，单位 Å
  1.2
```

## 激发态溶剂化效应

激发态溶剂化效应需要考虑非平衡溶剂化现象。溶剂的极化可以分为快极化和慢极化部分。垂直吸收和发射过程十分迅速，溶剂的偶极和构型不能迅速调整至与溶质电荷达到平衡的状态。

### 垂直吸收计算

#### 线性响应（Linear Response, LR）

```bdf
$SCF
rks
dft functional
  b3lyp
solvent
  user
dielectric
  78.3553
opticalDielectric
  1.7778
solmodel
  iefpcm
$END

$TDDFT
iroot
  8
solneqlr  # 线性响应非平衡溶剂化效应
$END
```

**注意**：计算非平衡溶剂化效应时，如果溶剂为用户指定的，需要设置光介电常数（`opticalDielectric`）。

#### 态特定（State-Specific, SS）

```bdf
$SCF
rks
dft functional
  PBE0
solvent
  water
solmodel
  iefpcm
$END

$TDDFT
iroot
  5
istore
  1
$END

$RESP
nfiles
  1
method
  2
iroot
  1 2 3
geom
norder
  0
solneqss  # 态特定非平衡溶剂化效应
$END
```

BDF 目前支持一阶微扰态特定的能量计算（ptSS）。

#### 矫正的线性响应（Corrected Linear Response, cLR）

```bdf
$SCF
rks
dft functional
  PBE0
solvent
  water
solmodel
  iefpcm
$END

$TDDFT
iroot
  5
istore
  1
$END

$TDDFT
iroot
  5
istore
  1
solneqlr  # 第一个 TDDFT 块计算激发态
$END

$RESP
nfiles
  1
method
  2
iroot
  1
geom
norder
  0
solneqlr
solneqss  # cLR 需要同时指定
$END
```

### 激发态几何优化

对于几何优化过程，溶剂有足够的时间进行响应，应考虑平衡溶剂效应。

```bdf
$SCF
dft functional
  gb3lyp
rks
solModel
  iefpcm
solvent
  water
$END

$TDDFT
iroot
  5
istore
  1
soleqlr  # 平衡溶剂化效应
$END

$RESP
geom
soleqlr  # 平衡溶剂化效应
method
  2
nfiles
  1
iroot
  1
$END
```

需要在 `TDDFT` 以及 `RESP` 模块中加入 `soleqlr` 关键词来表示平衡溶剂效应的计算。

### 垂直发射计算

在激发态的平衡几何结构下，进行 ptSS 或者 cLR 的平衡溶剂化效应的计算，将保存对应的溶剂慢极化电荷。在随后的 SCF 模块中加入 `emit` 关键词，来计算非平衡的基态能量。

```bdf
$SCF
dft functional
  PBE0
rks
solModel
  iefpcm
solvent
  water
$END

$TDDFT
iroot
  5
istore
  1
$END

$RESP
nfiles
  1
method
  2
iroot
  1
geom
norder
  0
soleqss  # 平衡溶剂化效应
$END

$SCF
dft functional
  PBE0
rks
solModel
  iefpcm
solvent
  water
emit     # 计算非平衡的基态能量
$END
```

## 显式溶剂和隐式溶剂相结合

激发态溶剂化效应可以采用显式溶剂和隐式溶剂相结合的方法计算。以水溶液为例，由于溶质分子的 HOMO 和 LUMO 轨道有可能弥散到第一水合层，所以在进行激发态计算时可以将第一水合层的水分子包括在 TDDFT 计算区域，而其余部分用隐式溶剂处理。

具体步骤：
1. 使用 Amber 程序进行分子动力学模拟，确定第一水合层
2. 使用 VMD 程序选择第一水合层分子
3. 将第一水合层分子坐标加入 COMPASS 模块的 Geometry 中
4. 在 SCF 模块中设置隐式溶剂模型

## 输出文件

使用 `cosmosave` 关键词可以保存孔穴体积、表面积，tesserae 坐标、电荷、面积等信息到工作目录的 `.cosmo` 文件：

```bdf
cosmosave
```

如有需要，可以利用 `$BDFHOME/sbin/conv2gaucosmo.py` 将其转化为类似 Gaussian 的 cosmors 关键词所生成的文件的格式。

## YAML 输入示例

### 基本溶剂化能计算

```yaml
task:
  type: energy

molecule:
  name: "Formaldehyde"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.00000000  -0.54200000
    - O  0.00000000  0.00000000   0.67700000
    - H  0.00000000  0.93500000  -1.08200000
    - H  0.00000000  -0.93500000  -1.08200000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g

settings:
  scf:
    solvent:
      name: water
      model: smd
```

### 用户指定介电常数

```yaml
settings:
  scf:
    solvent:
      name: user
      dielectric: 78.3553
      optical_dielectric: 1.7778  # 用于非平衡溶剂化效应
      model: iefpcm
```

### 自定义孔穴参数

```yaml
settings:
  scf:
    solvent:
      name: water
      model: iefpcm
      cavity:
        type: swig  # swig | switching | ses | sphere
        uatm: false
        radius_type: UFF  # UFF | Bondi
        vdW_scale: 1.1
        precision: medium  # ultraCoarse | coarse | medium | fine | ultraFine
      radii:
        H: 1.4430
        O: 1.7500
      acid_h_radius: 1.2
```

### 非静电溶剂化能

```yaml
settings:
  scf:
    solvent:
      name: water
      model: iefpcm
      non_electrostatic:
        components: [dis, rep, cav]  # 色散能、排斥能、孔穴能
        solvent_atoms: H2O1
        solvent_rho: 0.03333  # molecules Å^-3
        solvent_radius: 1.385  # Å
```

### TDDFT 非平衡溶剂化效应

```yaml
task:
  type: tddft

molecule:
  name: "Formaldehyde"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.00000000  -0.54200000
    - O  0.00000000  0.00000000   0.67700000
    - H  0.00000000  0.93500000  -1.08200000
    - H  0.00000000  -0.93500000  -1.08200000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g

settings:
  scf:
    solvent:
      name: user
      dielectric: 78.3553
      optical_dielectric: 1.7778
      model: iefpcm
  tddft:
    n_states: 8
    linear_response_non_equilibrium: true  # solneqlr
```

### TDDFT 激发态几何优化（平衡溶剂化）

```yaml
task:
  type: optimize

molecule:
  name: "Phenol"
  charge: 0
  multiplicity: 1
  coordinates:
    [coordinates]
  units: angstrom

method:
  type: dft
  functional: gb3lyp
  basis: 6-31g

settings:
  scf:
    solvent:
      name: water
      model: iefpcm
  tddft:
    n_states: 5
    store_wavefunction: 1
    linear_response_equilibrium: true  # soleqlr
  resp:
    method: 2
    nfiles: 1
    iroot: 1
    linear_response_equilibrium: true  # soleqlr
```

## 实现建议

### 转换器中的处理

1. **SCF 模块中的溶剂设置**：
   ```python
   def generate_scf_block(self, config):
       # ... existing code ...
       
       # Solvent settings
       solvent_settings = scf_settings.get('solvent', {})
       if solvent_settings:
           solvent_name = solvent_settings.get('name')
           if solvent_name:
               lines.append("solvent")
               if solvent_name == 'user':
                   lines.append(" user")
                   dielectric = solvent_settings.get('dielectric')
                   if dielectric:
                       lines.append("dielectric")
                       lines.append(f" {dielectric}")
                   optical_dielectric = solvent_settings.get('optical_dielectric')
                   if optical_dielectric:
                       lines.append("opticalDielectric")
                       lines.append(f" {optical_dielectric}")
               else:
                   lines.append(f" {solvent_name}")
           
           model = solvent_settings.get('model')
           if model:
               lines.append("solmodel")
               lines.append(f" {model}")
           
           # Cavity settings
           cavity = solvent_settings.get('cavity', {})
           if cavity:
               cavity_type = cavity.get('type')
               if cavity_type:
                   lines.append("cavity")
                   lines.append(f" {cavity_type}")
               # ... other cavity parameters ...
           
           # Non-electrostatic
           nonels = solvent_settings.get('non_electrostatic', {})
           if nonels:
               components = nonels.get('components', [])
               if components:
                   lines.append("nonels")
                   lines.append(f" {' '.join(components)}")
               # ... other nonels parameters ...
   ```

2. **TDDFT 模块中的溶剂设置**：
   ```python
   def generate_tddft_block(self, config):
       # ... existing code ...
       
       # Solvent non-equilibrium
       if tddft_settings.get('linear_response_non_equilibrium'):
           lines.append("solneqlr")
       if tddft_settings.get('linear_response_equilibrium'):
           lines.append("soleqlr")
   ```

3. **RESP 模块中的溶剂设置**：
   ```python
   def generate_resp_block(self, config):
       # ... existing code ...
       
       # Solvent settings
       resp_settings = settings.get('resp', {})
       solvent = resp_settings.get('solvent', {})
       if solvent.get('linear_response_non_equilibrium'):
           lines.append("solneqlr")
       if solvent.get('linear_response_equilibrium'):
           lines.append("soleqlr")
       if solvent.get('state_specific_non_equilibrium'):
           lines.append("solneqss")
       if solvent.get('state_specific_equilibrium'):
           lines.append("soleqss")
   ```

## 参考文档

- BDF 溶剂化模型手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Solvent-Model.rst`
- BDF 溶剂介电常数列表：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Solvent-Dielectric.rst`
- SCF 单点能量计算：`research/module_organization/SCF_ENERGY.md`
- TDDFT 计算：`research/module_organization/TDDFT.md`
- 结构优化：`research/module_organization/GEOMETRY_OPTIMIZATION.md`

