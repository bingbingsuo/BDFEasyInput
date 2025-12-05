# 结构优化与频率计算模块编排说明

## 概述

本文档说明如何根据 BDF 手册组织结构优化和频率计算的模块。参考手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Optimization.rst`

## 基本模块编排

### 1. 基态结构优化

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例：CH3Cl 在 B3LYP/def2-SV(P) 水平下的结构优化**

```bdf
$COMPASS
Title
 CH3Cl geometry optimization
Basis
 def2-SV(P)
Geometry
 C                  2.67184328    0.03549756   -3.40353093
 H                  2.05038141   -0.21545378   -2.56943947
 H                  2.80438882    1.09651909   -3.44309081
 H                  3.62454948   -0.43911916   -3.29403269
 Cl                 1.90897396   -0.51627638   -4.89053325
End geometry
$END

$BDFOPT
solver
 1
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

$RESP
geom
$END
```

**说明**：
- `BDFOPT` 模块控制结构优化过程
- `RESP` 模块负责计算梯度（`geom` 关键词表示用于几何优化）
- `solver 1` 表示使用 BDF 自带优化器（在冗余内坐标下优化）
- `solver 0` 表示使用 DL-FIND 优化器（在直角坐标下优化）

### 2. 结构优化的执行流程

结构优化任务中，程序并不是按顺序、单次、线性地调用各模块，而是会反复多次调用各模块：

1. 运行 `COMPASS`，读取分子结构等信息
2. 运行 `BDFOPT`，对结构优化所需的中间量进行初始化
3. `BDFOPT` 启动一个独立的 BDF 进程，用来计算当前结构下的能量和梯度，该进程只执行 `COMPASS`、`XUANYUAN`、`SCF`、`RESP` 各模块，而跳过 `BDFOPT`
4. 待后一个进程结束时，`BDFOPT` 汇总当前结构的能量和梯度信息，并据此调整分子结构
5. `BDFOPT` 根据当前结构的梯度以及几何结构步长的大小，判断结构是否收敛，如收敛或达到最大迭代次数，则程序结束；如不收敛，则跳至第 3 步

**输出文件**：
- `.out` 文件：只包含 `COMPASS` 和 `BDFOPT` 模块的输出，可以用来监测结构优化的进程
- `.out.tmp` 文件：包含 SCF 迭代、布居分析等详细信息
- `.optgeom` 文件：优化后的分子结构的笛卡尔坐标（单位：Bohr）

### 3. 收敛判据

结构优化收敛需要满足以下四个条件（均方根力和最大力、均方根步长和最大步长）：

```
Force-RMS < 0.2000E-03 Hartree/Bohr
Force-Max < 0.3000E-03 Hartree/Bohr
Step-RMS  < 0.8000E-03 Bohr
Step-Max  < 0.1200E-02 Bohr
```

这些收敛限可以通过 `tolgrad` 和 `tolstep` 关键词来设定。

## 频率计算

### 1. 单独频率计算

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例：CH3Cl 在平衡结构下的谐振频率计算**

```bdf
$COMPASS
Title
 CH3Cl frequency calculation
Basis
 def2-SV(P)
Geometry
 C          -0.93557703       0.15971089       0.58828595
 H          -1.71170348      -0.52644336       0.21665897
 H          -1.26240747       1.20299703       0.46170050
 H          -0.72835075      -0.04452039       1.64971607
 Cl          0.56770184      -0.09691413      -0.35697029
End geometry
$END

$BDFOPT
hess
 only
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

$RESP
geom
$END
```

**说明**：
- `hess only` 表示只进行频率计算而不做几何结构优化
- 对于基态 DFT 计算，程序进行解析 Hessian 计算
- 对于 TDDFT 等暂不支持解析 Hessian 的理论级别，程序将自动改为数值 Hessian 计算
- 数值 Hessian 计算需要计算 6N 个梯度（N 为原子数），其中每个原子分别向 x、y、z 轴正负方向进行扰动
- 程序实际共计算 6N+1 个梯度（包括未扰动结构的梯度，用于检查结构优化是否收敛）
- 因扰动结构会破坏分子的点群对称性，所以即便用户输入的分子存在点群对称性，计算也会自动改为在 C(1) 群下进行

**频率分析输出**：
- 振动所属不可约表示、振动频率、约化质量、力常数和简正模
- 各振动模式是按振动频率从小到大的顺序排列的，虚频排在所有实频的前面
- 热化学分析结果：
  - 零点能（Zero-point Energy）
  - 热校正能（Thermal correction to Energy）
  - 热校正焓（Thermal correction to Enthalpy）
  - 热校正 Gibbs 自由能（Thermal correction to Gibbs Free Energy）
  - 电子能 + 零点能
  - 电子能 + 热校正能
  - 电子能 + 热校正焓
  - 电子能 + 热校正 Gibbs 自由能

**热化学量计算假设**（默认）：
- 频率校正因子为 1.0
- 温度为 298.15 K
- 压强为 1 atm
- 电子态的简并度为 1

可以通过 `scale`、`temp`、`press`、`ndeg` 关键词修改这些参数。

### 2. 结构优化 + 频率计算（opt+freq）

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例**：

```bdf
$BDFOPT
solver
 1
hess
 final
$END
```

**说明**：
- `hess final` 表示在结构优化成功结束后才进行数值 Hessian 计算
- 若结构优化不收敛，则程序直接报错退出，而不进行 Hessian 及频率、热力学量的计算
- 可以在同一个 BDF 任务里依次实现结构优化与频率分析，无需单独编写两个输入文件

### 3. 过渡态优化 + 频率计算

**示例：HCN/HNC 异构反应的过渡态优化**

```bdf
$COMPASS
Title
 HCN <-> HNC transition state
Basis
 def2-SVP
Geometry
 C  0.00000000  0.00000000  0.00000000
 N  0.00000000  0.00000000  1.14838000
 H  1.58536000  0.00000000  1.14838000
End geometry
$END

$BDFOPT
solver
 1
hess
 init+final
iopt
 10
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

$RESP
geom
$END
```

**说明**：
- `iopt 10` 表示优化过渡态
- `hess init+final` 表示既产生初始 Hessian 以备过渡态优化需要，又在结构优化收敛后再次进行 Hessian 计算
- 过渡态优化必须在第一步结构优化之前产生一个初始的精确 Hessian（因为模型 Hessian 一般不存在虚频）
- 也可以将 `init+final` 替换为 `init`，但一般需要检验最终收敛的结构的虚频数目，因此不建议省略 `final`

## 特殊优化方法

### 1. Dimer 方法（过渡态优化）

**特点**：只需要梯度，不需要计算 Hessian 矩阵

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例**：

```bdf
$COMPASS
Title
 HCN <-> HNC transition state
Basis
 def2-SVP
Geometry
 C  0.00000000  0.00000000  0.00000000
 N  0.00000000  0.00000000  1.14838000
 H  1.58536000  0.00000000  1.14838000
End geometry
nosymm  # 必须关闭对称性（或使用 norotate）
$END

$BDFOPT
solver
 0  # 必须使用 DL-FIND 优化器
iopt
 3  # L-BFGS（默认，也可以不指定）
dimer
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

$RESP
geom
$END
```

**注意事项**：
1. Dimer 方法要调用 DL-FIND 外部库（`solver=0`），仅支持 L-BFGS 优化算法（`iopt=3`）
2. 由于 DL-FIND 与 BDF 默认的坐标转动有冲突，必须在 `compass` 模块中加上关键词 `norotate` 禁止分子转动，或用 `nosymm` 关闭对称性；对于双原子和三原子分子，只能用 `nosymm`
3. 如果在过渡态优化后做频率计算，加上 `hess final`。由于 Dimer 方法不需要 Hessian，不要用 `init+final`

### 2. CI-NEB 方法（最低能量路径和过渡态）

**特点**：计算最低能量路径，同时得到过渡态结构

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例**：

```bdf
$COMPASS
Basis-block
 def2-SVP
End basis
Geometry
 C    0.0200000   0.0000000   0.0000000
 N    0.0000000  -1.1400000   0.0000000
 H    0.0000000   1.0500000   0.0000000
End geometry
nosymm  # 必须关闭对称性（或使用 norotate）
$END

$BDFOPT
solver
 0  # 必须使用 DL-FIND 优化器
iopt
 3
neb-block
 crude
 nebmode
  0
 nimage
  3
end neb
geometry2
 C    0.0000000   0.0000000   0.0000000
 N   -1.1500000   0.2300000   0.0000000
 H   -1.6100000   1.1100000   0.0000000
end geometry2
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

$RESP
geom
$END
```

**说明**：
- CI-NEB 计算需要提供两个端点的坐标，其中第一个端点的初始结构在 `COMPASS` 模块提供，第二个端点的初始结构在 `Geometry2` ... `End Geometry2` 输入块提供
- 两套坐标的原子顺序必须一致
- `nimage 3` 表示使用 3 个中间像点
- `nebmode 0` 表示对反应物和产物做能量最小化（默认固定不优化）
- 如果 `NFrame>1`，可以在 `Geometry2` 中为 CI-NEB 计算提供中间像点的结构

### 3. 限制性结构优化

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例：冻结内坐标**

```bdf
$BDFOPT
solver
 1
constrain
 1  # 1 个约束
 2 5  # 限制原子 2 和原子 5 之间的距离
$END
```

**示例：冻结多个内坐标**

```bdf
$BDFOPT
solver
 1
constrain
 2  # 2 个约束
 1 2  # 限制原子 1 和原子 2 之间的距离
 2 5 10  # 限制原子 2、5、10 形成的键角
$END
```

**示例：冻结内坐标并设定目标值**

```bdf
$BDFOPT
solver
 1
constrain
 1  # 1 个约束
 2 3 = 2.0  # 限制原子 2 和原子 3 之间的距离为 2.0 Angstrom
$END
```

**示例：冻结笛卡尔坐标**

```bdf
$BDFOPT
solver
 1
frozen
 3  # 冻结 3 个原子
 2 -1  # 冻结原子 2 的 x、y、z 坐标
 5 -1  # 冻结原子 5 的 x、y、z 坐标
 10 -1  # 冻结原子 10 的 x、y、z 坐标
$END
```

**说明**：
- `constrain` 用于限制内坐标（键长、键角、二面角）
- `frozen` 用于冻结笛卡尔坐标
- 可以同时使用 `constrain` 和 `frozen`
- 冻结类型：`-1`=冻结 x、y、z；`-2`=冻结 x；`-3`=冻结 y；`-4`=冻结 z；`-23`=冻结 x、y；`-24`=冻结 x、z；`-34`=冻结 y、z（仅 DL-FIND 支持部分冻结）
- 即使分子坐标是以直角坐标而非内坐标的形式输入的，BDF 仍然可以对内坐标做限制性优化
- 程序冻结的是用户指定的各原子之间的相对笛卡尔坐标，原子的绝对笛卡尔坐标仍可能因为分子标准取向的变化而变化
- 同一个计算可以既冻结任意多的笛卡尔坐标，也冻结任意多的内坐标
- 当用户同时冻结多个内坐标并赋值时，需确认其冻结的内坐标值彼此自洽

### 4. 柔性扫描

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例：一维扫描**

```bdf
$BDFOPT
solver
 1  # 柔性扫描必须指定 solver=1
scan
 1  # 扫描 1 个坐标
 5 6 = 4.0 1.0 -0.1  # 将原子 5 和原子 6 之间的键长从 4.0 扫到 1.0，步长 -0.1
$END
```

**示例：散点扫描**

```bdf
$BDFOPT
solver
 1
scan
 1 9  # 扫描 1 个坐标，扫 9 个点
 5 6  # 这个坐标是原子 5 和原子 6 之间的键长
 4.0  # 从这行开始是键长的值
 3.0
 2.5
 2.0
 1.8
 1.6
 1.4
 1.2
 1.0
$END
```

**示例：二维扫描**

```bdf
$BDFOPT
solver
 1
scan
 2  # 扫描 2 个坐标
 2 4 5 = 90 120 5  # 原子 2、4、5 的键角从 90 度扫到 120 度，步长 5 度
 2 4 5 13 = 0 360 10  # 原子 2、4、5、13 的二面角从 0 度扫到 360 度，步长 10 度
$END
```

**说明**：
- 柔性扫描功能仅支持 `solver=1`，不支持 `solver=0`
- 扫描结果输出到 `$BDFTASK.scanpes` 文件
- 每步结构优化的结构会输出到 `$BDFTASK.optgeom1`、`$BDFTASK.optgeom2` 等文件中

### 5. O(1) 数值 Hessian 方法（O1NumHess）

**特点**：仅需约 100 个梯度计算，适用于大体系（150 原子以上可加速至传统方法的 1/10）

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例：1-辛醇的 Hessian 计算**

```bdf
$COMPASS
Title
 1-Oct-OH
Basis
 STO-3G
Geometry
 [coordinates]
End Geometry
nosym
norotate
$END

$BDFOPT
hess
 only
qrrho  # 对于大体系、非共价相互作用重要的体系推荐使用
o1numhess
ncorepergrad
 2  # 每个梯度计算使用的核数，默认 1
$END

$XUANYUAN
$END

$SCF
RHF
$END

$RESP
geom
$END
```

**说明**：
- `o1numhess` 关键词启用 O(1) 数值 Hessian 方法
- 需要用户安装 Python3（3.6 或以上版本）、NumPy 和 SciPy
- 默认设置下，平均振动频率误差一般为 2~5 cm^-1，反应 Gibbs 自由能误差一般在 1 kcal/mol 左右
- `ncorepergrad` 指定每个梯度计算用多少个核，最优取值应使得 `OMP_NUM_THREADS/ncorepergrad` 约为预期需要计算的梯度数的 1/5~1/10 左右
- 适用于程序暂不支持解析 Hessian 的情形（如 TDDFT Hessian、开启 MPEC+COSX 的基态 Hessian）
- 也可用于计算结构优化的初始 Hessian，或在结构优化结束后计算 Hessian（即 "opt freq" 计算）

### 6. 自动消除虚频

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP`

**示例：极小值点优化**

```bdf
$BDFOPT
solver
 1
rmimag  # 自动消除虚频
hess
 final
$END
```

**示例：过渡态优化**

```bdf
$BDFOPT
solver
 1
rmimag
hess
 init  # 计算初始 Hessian。如果需要最终 Hessian 的热化学分析，改为 init+final
iopt
 10  # 过渡态优化
$END
```

**说明**：
- `rmimag`（或 `removeimag`）关键词可以自动消除多余的虚频
- 对于极小值点优化：如果有虚频，自动将分子结构沿着绝对值最大的虚频对应的振动模的方向扰动，然后继续优化
- 对于过渡态优化：
  - 如果虚频数目大于 1，自动将分子结构沿着绝对值第二大的虚频的方向扰动，然后继续优化
  - 如果虚频数目等于 0，自动尝试在附近寻找虚频数目等于 1 的结构
- 程序不能保证在所有情况下都能消除所有多余的虚频，优化结束后用户仍然需要检查虚频数目
- 如果分子具有点群对称性，但计算时没有指定 `nosymm`，则可能无法完全消除所有的虚频
- 限制性优化得到的结构，有可能存在无法消掉的虚频，用户应通过观察虚频的振动模式自行判断

### 7. 锥形交叉点（CI）和最低能量交叉点（MECP）优化

**特点**：需要调用 DL-FIND 外部库（`solver=0`）

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `TDDFT` → `RESP`（多个 RESP 块）

**示例：CI 优化（乙烯的 T1 态和 T2 态的锥形交叉点）**

```bdf
$COMPASS
Title
 C2H4 Molecule test run
Basis
 6-31G
Geometry
 [coordinates]
End geometry
nosymm
$END

$BDFOPT
imulti  # 优化 CI
 2
maxcycle
 50
tolgrad
 1.d-4
tolstep
 5.d-3
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 BHHLYP
Charge
 0
Spin
 1
$END

$TDDFT
imethod
 1
isf
 1
itda
 1
nroot
 5
idiag
 1
istore
 1
crit_e
 1.d-8
crit_vec
 1.d-6
$END

$RESP
geom
norder
 1
method
 2
iroot
 1
nfiles
 1
$END

$RESP
geom
norder
 1
method
 2
iroot
 2
nfiles
 1
$END

$RESP
iprt
 1
QUAD
FNAC
double
norder
 1
method
 2
nfiles
 1
pairs
 1
 1 1 1 1 1 2
$END
```

**示例：MECP 优化（S0 和 T1 的最低能量交叉点）**

```bdf
$COMPASS
Title
 C2H4 Molecule test run
Basis
 6-31G
Geometry
 [coordinates]
End geometry
nosymm
$END

$BDFOPT
solver
 0  # 必须使用 DL-FIND 优化器
imulti
 2
maxcycle
 50
tolgrad
 1.d-4
tolstep
 5.d-3
noncoupl  # 不执行态间耦合梯度计算（用于 MECP 优化）
$END

$XUANYUAN
$END

$SCF
RKS
dft functional
 BHHLYP
Charge
 0
Spin
 1
$END

$RESP
geom
norder
 1
method
 1
$END

$SCF
UKS
dft functional
 BHHLYP
Charge
 0
Spin
 3
$END

$RESP
geom
norder
 1
method
 1
$END
```

**说明**：
- CI 优化需要计算两个激发态的梯度，以及它们之间的非绝热耦合矢量（NACME）
- MECP 优化仅需计算两个态的梯度，无需计算非绝热耦合矢量
- `imulti 2` 表示用梯度投影方法优化 CI 或 MECP
- `noncoupl` 用于 MECP 优化，表示不执行态间耦合梯度计算
- 注意能量一行的值总是显示为 0，这并不代表优化时体系能量不变，而是因为优化 CI/MECP 不会用到能量的收敛情况来判断是否收敛

### 8. 内禀反应坐标（IRC）计算

**特点**：计算连接势能面相邻两个极小点的能量最低路径

**模块顺序**：`IRC` → `COMPASS` → `XUANYUAN` → `SCF` → `RESP`

**示例**：

```bdf
$IRC
ircpts  # 反应路径的最大步数
 50
ircdir  # 选择反应路径的方向
 0
ircalpha  # 反应路径的步长参数
 0.05
$END

$COMPASS
Title
 Irc4bdf
Geometry
 [过渡态结构的坐标]
End Geometry
Basis
 CC-PVDZ
$END

$XUANYUAN
$END

$SCF
UKS
guess
 readmo  # 读取过渡态收敛的分子轨道信息
dft functional
 GB3LYP
Charge
 0
Spin
 2
$END

$RESP
Geom
$END
```

**说明**：
- IRC 计算需要过渡态结构的力常数（`.hess` 文件）和收敛的分子轨道信息（`.scforb` 文件）
- 需要把 `$IRC` 模块的参数写在输入文件的最前面
- 需要保留优化过渡态时使用的计算参数（`$SCF` 和 `$RESP` 模块需要严格保留）
- 需要把过渡态对应的 `hess`、`scforb` 文件都改名为与输入文件同名
- 计算结果会生成 `.irc` 文件和 `.trj` 文件

### 9. 多态混合模型（自旋混合态的结构优化）

**特点**：用于研究多态反应，优化自旋混合态的结构

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `RESP` → `SCF` → `RESP`（两个 SCF+RESP 循环）

**示例：ZnS 分子的两态自旋混合优化**

```bdf
$COMPASS
Title
 two-state calculation of ZnS
Basis
 lanl2dz
Geometry
 Zn  0.0  0.0  0.0
 S   0.0  0.0  2.05
END geometry
$END

$BDFOPT
solver
 1
multistate
 2soc  400  # 两态自旋混合，旋轨耦合常数 400 cm^-1
$END

$XUANYUAN
$END

%cp $BDF_WORKDIR/$BDFTASK.scforb.1   $BDF_WORKDIR/$BDFTASK.scforb    2>/dev/null || :

$SCF
rks
dft functional
 pbe0
charge
 0
spinmulti
 1
$END

%cp $BDF_WORKDIR/$BDFTASK.scforb     $BDF_WORKDIR/$BDFTASK.scforb.1

$RESP
geom
$END

%cp $BDF_WORKDIR/$BDFTASK.egrad1     $BDF_WORKDIR/$BDFTASK.egrad.1

%cp $BDF_WORKDIR/$BDFTASK.scforb.2   $BDF_WORKDIR/$BDFTASK.scforb    2>/dev/null || :

$SCF
uks
dft functional
 pbe0
charge
 0
spinmulti
 3
$END

%cp $BDF_WORKDIR/$BDFTASK.scforb     $BDF_WORKDIR/$BDFTASK.scforb.2

$RESP
geom
$END

%cp $BDF_WORKDIR/$BDFTASK.egrad1     $BDF_WORKDIR/$BDFTASK.egrad.2
```

**说明**：
- 多态混合计算的选项是 `2soc`（类似有 `3soc`、`4soc` 等）
- 两个自旋态需要有**不同的自旋多重度**（除非理论计算证明两个相同自旋的态之间也存在强 SOC 相互作用）
- 旋轨耦合常数经验值 400 cm^-1 是程序默认值，可以省略不写
- 两个自旋态的能量、梯度要分别保存到 `$BDFTASK.egrad.1` 和 `$BDFTASK.egrad.2` 文件
- 需要分别备份两个 SCF 计算的轨道文件为 `$BDFTASK.scforb.1` 和 `$BDFTASK.scforb.2`
- 在复制命令的末尾需要加上 `2>/dev/null || :` 以屏蔽首次复制出错的信息

## 激发态结构优化

**模块顺序**：`COMPASS` → `BDFOPT` → `XUANYUAN` → `SCF` → `TDDFT` → `RESP`

**示例：丁二烯第一激发态结构优化**

```bdf
$COMPASS
Title
 C4H6 TDDFT optimization
Basis
 CC-PVDZ
Geometry
 C   -1.85874726   -0.13257980    0.00000000
 H   -1.95342119   -1.19838319    0.00000000
 H   -2.73563916    0.48057645    0.00000000
 C   -0.63203020    0.44338226    0.00000000
 H   -0.53735627    1.50918564    0.00000000
 C    0.63203020   -0.44338226    0.00000000
 H    0.53735627   -1.50918564    0.00000000
 C    1.85874726    0.13257980    0.00000000
 H    1.95342119    1.19838319    0.00000000
 H    2.73563916   -0.48057645    0.00000000
End Geometry
$END

$BDFOPT
solver
 1
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

$TDDFT
nroot
 0 0 0 1  # 计算 1Bu 态（对于 C(2h) 点群：Ag, Au, Bg, Bu）
istore
 1
# TDDFT 梯度计算需要更严格的收敛标准
crit_vec
 1.d-6  # default 1.d-5
crit_e
 1.d-8  # default 1.d-7
$END

$RESP
geom
norder
 1  # First-order nuclear derivative (gradient)
method
 2  # TDDFT response properties
nfiles
 1  # Must be the same number as istore in $TDDFT
iroot
 1  # Calculate the gradient of the first root
$END
```

**说明**：
- TDDFT 结构优化需要 `TDDFT` 模块和 `RESP` 模块
- `TDDFT` 模块需要设置 `istore` 保存波函数
- TDDFT 梯度计算需要更严格的收敛标准（`crit_vec 1.d-6`、`crit_e 1.d-8`）
- `RESP` 模块参数：
  - `method 2`：TDDFT 响应性质
  - `nfiles` 必须与 `TDDFT` 中的 `istore` 相同
  - `iroot` 指定计算第几个激发态的梯度（注意：这里的 `iroot` 与 `TDDFT` 模块中的 `iroot` 意义不同）

## BDFOPT 关键词说明

### 求解器选择

1. **`solver`**：优化器选择
   - `solver 0`：使用 DL-FIND 优化器（直角坐标，支持更多优化类型）
   - `solver 1`：使用 BDF 自带优化器（冗余内坐标，推荐用于极小值点和过渡态优化）

### 优化类型

1. **`iopt`**：优化目标
   - `iopt 3`：优化极小值点（L-BFGS，默认）
   - `iopt 10`：优化过渡态（P-RFO）
   - 其他值：参见 DL-FIND 文档

### 收敛控制

1. **`tolgrad`**：均方根梯度的收敛标准（单位：Hartree/Bohr）
   - 默认值：DL-Find 为 `2.D-4`，BDF 为 `3.D-4`

2. **`tolstep`**：均方根步长的收敛标准（单位：Bohr）
   - 默认值：`1.2D-3`（仅 BDF 优化器有效）

3. **`tolene`**：能量变化的收敛标准（单位：Hartree）
   - 默认值：`1.D-6`（仅 DL-Find 优化器有效）

4. **`trust`**：置信半径（trust radius）
   - 默认值：`0.3`
   - 正数：初始置信半径，可能动态调整
   - 负数：初始置信半径，且禁止超过该值

5. **`maxcycle`**：最大优化步数
   - 默认值：DL-Find 为 50，BDF 为 `max(100, 6*原子数)`

### Hessian 计算

1. **`hess`**：Hessian 计算模式
   - `hess only`：只计算 Hessian（频率计算）
   - `hess init`：计算初始 Hessian，然后进行结构优化
   - `hess final`：结构优化收敛后计算 Hessian（opt+freq）
   - `hess init+final`：既计算初始 Hessian，又在优化收敛后计算 Hessian（过渡态优化推荐）

2. **`restarthess`**：断点续算频率计算

3. **`o1numhess`**：使用 O(1) 数值 Hessian 方法（仅需约 100 个梯度，适用于大体系）
   - 需要用户安装 Python3、NumPy 和 SciPy
   - 适用于程序暂不支持解析 Hessian 的情形（如 TDDFT Hessian、开启 MPEC+COSX 的基态 Hessian）

4. **`recalchess`**：每隔若干步重新计算精确 Hessian（用于过渡态优化）
   - 例如：`recalchess 10` 表示每隔 10 步重新计算一次精确 Hessian

5. **`readhess`**：读取 Hessian 文件作为初始 Hessian
   - 需要与输入文件同名的 `.hess` 文件
   - 即使读取初始 Hessian，仍然需要写 `hess init+final` 而不是 `hess final`

6. **`usenumhess`**：强制使用数值 Hessian（即使支持解析 Hessian）

7. **`parhess`**：完美并行梯度计算（适用于大体系、多核计算）
   - 默认会开启 `OMP_NUM_THREADS` 个进程，每个进程计算一个梯度
   - 仅 2025 年 7 月及以后的 BDF 版本可用，且要求用户安装 Python3、NumPy 和 SciPy

8. **`ncorepergrad`**：指定每个梯度计算使用的核数（用于 O1NumHess 或 ParHess）

### 约束和冻结

1. **`constrain`**：限制内坐标
   - 格式：第一行是约束数目 N，随后 N 行定义约束
   - 2 个原子：限制键长
   - 3 个原子：限制键角
   - 4 个原子：限制二面角
   - 可以设定目标值：`2 3 = 2.0`（限制键长为 2.0 Angstrom）

2. **`frozen`**：冻结笛卡尔坐标
   - 格式：第一行是冻结原子数 N，随后 N 行定义冻结
   - 冻结类型：`-1`=冻结 x、y、z；`-2`=冻结 x；`-3`=冻结 y；`-4`=冻结 z；`-23`=冻结 x、y；`-24`=冻结 x、z；`-34`=冻结 y、z

### 扫描

1. **`scan`**：柔性扫描
   - 格式：第一行是扫描维度 N（或 M N 表示散点扫描），随后定义扫描坐标和范围
   - 网格扫描：`A B = start end interval`
   - 散点扫描：先定义坐标，再列出各点的值

### 多态优化

1. **`imulti`**：多态优化类型
   - `imulti 0`：不执行多态优化（默认）
   - `imulti 1`：用惩罚函数方法优化 CI 或 ISC
   - `imulti 2`：用梯度投影方法优化 CI 或 MECP

2. **`multistate`**：多态自旋混合模型
   - `2soc [chi]`：两态自旋混合（chi 为旋轨耦合常数，单位 cm^-1，默认 400）
   - `3soc [chi]`：三态自旋混合
   - `4soc [chi]`：四态自旋混合

3. **`noncoupl`**：不执行态间耦合梯度计算（用于 MECP 优化）

### 热化学量计算

1. **`scale`**：频率校正因子
   - 默认值：`1.0`
   - 例如：`scale 0.98` 表示频率校正因子为 0.98

2. **`temp`**：温度（单位：Kelvin）
   - 默认值：`298.15`

3. **`press`**：压强（单位：atm）
   - 默认值：`1.0`

4. **`ndeg`**：电子态的简并度
   - 对于非相对论或标量相对论计算，且电子态不存在空间简并性的情形，电子态的简并度等于自旋多重度（2S+1）
   - 对于存在空间简并性的电子态，还应乘上电子态的空间简并度
   - 对于考虑了旋轨耦合的相对论性计算，应将自旋多重度替换为相应旋量态的简并度（2J+1）

5. **`qrrho`**：开启 QRRHO 方法
   - 对于大分子（100 个原子以上）、柔性分子，以及非共价相互作用比较重要的体系的自由能、熵计算，建议打开 QRRHO
   - 开启 QRRHO 后，自由能、熵结果与 ORCA、Turbomole 可比，但与 Gaussian 不可比

### 其他

1. **`rmimag`**：自动消除虚频

2. **`dimer`**：使用 Dimer 方法优化过渡态（仅 `solver=0`）

3. **`neb`**：使用 CI-NEB 方法计算反应路径（仅 `solver=0`）

4. **`geometry2`**：为 CI-NEB 指定第二个端点的几何结构

5. **`nframe`**：在 `Geometry2` 中提供的坐标个数

## RESP 模块关键词说明

### 基本参数

1. **`geom`**：无值关键词，表示用于几何优化

2. **`norder`**：导数阶数
   - `norder 1`：计算梯度（用于几何优化）
   - `norder 2`：计算 Hessian（用于频率计算）

3. **`method`**：计算方法
   - `method 1`：SCF 梯度（HF/DFT）
   - `method 2`：TDDFT 梯度

4. **`nfiles`**：读取的波函数文件数（用于 TDDFT 梯度）
   - 必须与 `TDDFT` 模块中的 `istore` 相同

5. **`iroot`**：计算第几个激发态的梯度（用于 TDDFT 梯度）
   - 注意：这里的 `iroot` 与 `TDDFT` 模块中的 `iroot` 意义不同

## 几何优化常见问题

### 1. 虚频问题

**问题类型**：
- 优化极小值点收敛的结构有虚频
- 优化过渡态收敛的结构的虚频多于 1 个
- 优化过渡态收敛的结构没有虚频

**解决方法**：
- 使用 `rmimag` 关键词自动消除多余的虚频（推荐首先尝试）
- 当 `rmimag` 无法奏效时，手动解决：
  - **虚频数目小于预期值**：一般说明得到的过渡态结构定性错误，需要根据化学常识重新准备初猜结构
  - **虚频数目大于预期值**：
    - 可能是数值误差导致的：加大格点、减小积分截断阈值、减小各类收敛阈值
    - 可能是真实存在的：从输出文件查看虚频对应的简正模，沿着该简正模方向对收敛的结构进行扰动，然后重新优化
  - 无法仅从频率计算结果判断某个虚频是否是数值误差导致的，但一般而言，虚频的绝对值越小，就越可能是数值误差导致的
  - 限制性优化得到的结构，有可能存在无法消掉的虚频，用户应通过观察虚频的振动模式自行判断

### 2. 对称性问题

**问题**：当初始结构具有 C(1) 群以上的点群对称性时，结构优化有可能会破坏点群对称性

**解决方法**：
- 仍然在高对称性下优化至收敛，然后计算频率。若存在虚频，按照虚频问题的方法扰动分子结构来消除虚频
- 在 COMPASS 模块中指定采用分子点群的某一个子群，此时程序只会保持该子群对称性不被破坏
- 若指定的是 C(1) 群，则程序允许以任何方式破坏分子对称性，可以最大程度上提高得到低能量结构的概率，但代价为无法利用点群对称性加速计算

### 3. 几何优化不收敛

**导致不收敛的因素**：
- 能量、梯度存在数值噪声
- 势能面过于平缓
- 分子有不止一个稳定波函数，结构优化时波函数在各个稳定解之间来回跳跃
- 分子结构不合理（坐标单位错误、多画或漏画原子、非成键原子之间的距离太近等）
- 某些反应不存在过渡态
- 某些激发态结构优化可能会优化到锥形交叉点附近
- 某些 TDDFT 结构优化可能会优化到势能面上基态波函数不稳定的区域
- 极个别情况下，因为程序构建的内坐标含有接近 180 度的键角，导致优化失败

**解决方法**（按顺序尝试）：
1. 以优化不收敛的任务的最后一帧结构为初始结构，重新开始优化（使用 `restart` 关键词）
2. 减小优化步长（置信半径 `trust`）
3. 对于过渡态优化，使用 `recalchess` 定期重新计算精确 Hessian
4. 加大格点，减小积分截断阈值及 SCF 等的收敛阈值，以减小数值误差
5. 改用 DL-Find 优化器（`solver 0`），在直角坐标下优化结构

**重要**：在应用以上方法之前，用户应检查当前这个不收敛的计算所得结构相比用户提供的初猜结构哪个更合理，用其中较为合理的那个结构作为接下来重新优化的初猜结构。

## 注意事项

1. **梯度模块选择**：
   - **RESP 模块**：支持所有 SCF 方法（HF 和 DFT）以及 TDDFT
   - **GRAD 模块**：仅支持 HF 和 MCSCF，不支持 DFT
   - 对于 DFT 计算，必须使用 RESP 模块

2. **点群对称性**：
   - 数值频率计算必须在 C(1) 群下进行（即使输入结构有对称性）
   - 如果用户希望指定每个不可约表示下的轨道占据数，或希望计算某个特定不可约表示下的某个激发态的数值频率，则用户必须先单独做一个保持点群对称性的单点计算，根据单点计算的结果手动指认
   - opt+freq 计算中的结构优化步骤支持在非 C(1) 点群下计算，但数值频率计算步骤仍然必须在 C(1) 群下计算

3. **收敛标准**：
   - TDDFT 梯度计算需要更严格的收敛标准（`crit_vec 1.d-6`、`crit_e 1.d-8`）
   - 结构优化的收敛标准可以通过 `tolgrad` 和 `tolstep` 调整
   - 默认收敛限：
     - Force-RMS: `0.2000E-03` Hartree/Bohr
     - Force-Max: `0.3000E-03` Hartree/Bohr
     - Step-RMS: `0.8000E-03` Bohr
     - Step-Max: `0.1200E-02` Bohr

4. **虚频问题**：
   - 优化极小值点结构时，虚频数目应为 0
   - 优化过渡态时，虚频数目应为 1
   - 可以使用 `rmimag` 关键词自动消除多余的虚频
   - 详见"几何优化常见问题"部分

5. **优化不收敛**：
   - 可以尝试使用 `restart` 关键词从上次优化的结构继续
   - 可以减小置信半径（`trust`）
   - 对于过渡态优化，可以使用 `recalchess` 定期重新计算 Hessian
   - 可以改用 DL-Find 优化器（`solver 0`）
   - 详见"几何优化常见问题"部分

6. **内存管理**：
   - 解析 Hessian 计算的内存由 `OMP_STACKSIZE` 和 `RESP` 模块的 `maxmem` 关键词控制
   - 建议：`OMP_STACKSIZE*OMP_NUM_THREADS + maxmem <= 物理内存*80%`
   - 对于解析 Hessian 计算，建议 `OMP_STACKSIZE*OMP_NUM_THREADS` 为 `maxmem` 的 1/3~1/10 左右，但若这使得 `OMP_STACKSIZE` 小于 1G，则设置 `OMP_STACKSIZE=1G`

7. **并行计算**：
   - 可以使用 `ParHess` 关键词进行完美并行梯度计算（适用于大体系、多核计算）
   - 可以使用 `NCorePerGrad` 指定每个梯度计算使用的核数
   - `ParHess` 关键字仅在 2025 年 7 月及以后的 BDF 版本中可用，且要求用户安装 Python3、NumPy 和 SciPy

8. **输出文件**：
   - `.out` 文件：只包含 `COMPASS` 和 `BDFOPT` 模块的输出，可以用来监测结构优化的进程
   - `.out.tmp` 文件：包含 SCF 迭代、布居分析等详细信息
   - `.optgeom` 文件：优化后的分子结构的笛卡尔坐标（单位：Bohr）
   - `.hess` 文件：Hessian 矩阵（用于频率计算）
   - `.scanpes` 文件：柔性扫描结果汇总信息
   - `.irc` 文件：IRC 计算每一步的信息
   - `.trj` 文件：IRC 计算的轨迹文件

9. **冗余内坐标**：
   - BDF 使用冗余内坐标进行结构优化（`solver=1` 时）
   - 当分子里有的键角接近或等于 180 度时，基于冗余内坐标的优化算法经常会出现数值不稳定性问题
   - 程序会自动重新构建冗余内坐标并自动重启优化，总共允许优化器重启 10 次
   - 如果 10 次重启机会用完仍然遇到问题，可以改用 DL-Find 优化器（`solver 0`）在直角坐标下进行优化

## YAML 输入示例

### 基本结构优化

```yaml
task:
  type: optimize
  description: "CH3Cl geometry optimization"

molecule:
  name: "CH3Cl"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  2.67184328  0.03549756  -3.40353093
    - H  2.05038141  -0.21545378  -2.56943947
    - H  2.80438882  1.09651909  -3.44309081
    - H  3.62454948  -0.43911916  -3.29403269
    - Cl 1.90897396  -0.51627638  -4.89053325
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: def2-sv(p)

settings:
  geometry_optimization:
    solver: 1  # BDF 自带优化器
    max_iterations: 100
    tolerance:
      gradient: 3.0e-4
      step: 1.2e-3
```

### 结构优化 + 频率计算

```yaml
task:
  type: optimize
  description: "CH3Cl optimization and frequency"

molecule:
  name: "CH3Cl"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  2.67184328  0.03549756  -3.40353093
    - H  2.05038141  -0.21545378  -2.56943947
    - H  2.80438882  1.09651909  -3.44309081
    - H  3.62454948  -0.43911916  -3.29403269
    - Cl 1.90897396  -0.51627638  -4.89053325
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: def2-sv(p)

settings:
  geometry_optimization:
    solver: 1
    hessian:
      mode: final  # opt+freq
```

### 过渡态优化

```yaml
task:
  type: optimize
  description: "HCN <-> HNC transition state"

molecule:
  name: "HCN"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.00000000  0.00000000
    - N  0.00000000  0.00000000  1.14838000
    - H  1.58536000  0.00000000  1.14838000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: def2-svp

settings:
  geometry_optimization:
    solver: 1
    optimization_type: transition_state  # iopt=10
    hessian:
      mode: init+final  # 计算初始和最终 Hessian
```

### 限制性优化

```yaml
task:
  type: optimize
  description: "Constrained optimization"

molecule:
  name: "Molecule"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  0.00000000  0.70678098  -0.40492819
    - C  0.00000000  -0.70678098  -0.40492819
    - O  0.00000000  0.00000000  0.95133348
    - H  0.86041653  1.24388179  -0.74567167
    - H  -0.86041653  1.24388179  -0.74567167
    - H  0.86041653  -1.24388179  -0.74567167
    - H  -0.86041653  -1.24388179  -0.74567167
  units: angstrom

method:
  type: dft
  functional: m062x
  basis: 6-31+g(d,p)

settings:
  geometry_optimization:
    solver: 1
    constraints:
      - type: bond
        atoms: [2, 3]
        value: 2.0  # 限制键长为 2.0 Angstrom
```

### TDDFT 激发态结构优化

```yaml
task:
  type: optimize
  description: "Butadiene first excited state optimization"

molecule:
  name: "C4H6"
  charge: 0
  multiplicity: 1
  coordinates:
    - C  -1.85874726  -0.13257980  0.00000000
    - H  -1.95342119  -1.19838319  0.00000000
    - H  -2.73563916  0.48057645  0.00000000
    - C  -0.63203020  0.44338226  0.00000000
    - H  -0.53735627  1.50918564  0.00000000
    - C  0.63203020  -0.44338226  0.00000000
    - H  0.53735627  -1.50918564  0.00000000
    - C  1.85874726  0.13257980  0.00000000
    - H  1.95342119  1.19838319  0.00000000
    - H  2.73563916  -0.48057645  0.00000000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: cc-pvdz

settings:
  geometry_optimization:
    solver: 1
  tddft:
    n_states: 1
    store_wavefunction: 1
    crit_vec: 1.0e-6
    crit_e: 1.0e-8
  resp:
    method: 2  # TDDFT gradient
    nfiles: 1
    iroot: 1
```

## 实现建议

### 转换器中的处理

1. **基本结构优化**：
   ```python
   if task_type == 'optimize':
       blocks.append(self.generate_compass_block(config))
       blocks.append(self.generate_bdfopt_block(config))
       blocks.append(self.generate_xuanyuan_block(config))
       blocks.append(self.generate_scf_block(config))
       blocks.append(self.generate_resp_block(config, method=1))
   ```

2. **TDDFT 结构优化**：
   ```python
   if task_type == 'optimize' and settings.get('tddft'):
       blocks.append(self.generate_compass_block(config))
       blocks.append(self.generate_bdfopt_block(config))
       blocks.append(self.generate_xuanyuan_block(config))
       blocks.append(self.generate_scf_block(config))
       blocks.append(self.generate_tddft_block(config, istore=1))
       blocks.append(self.generate_resp_block(config, method=2, nfiles=1, iroot=1))
   ```

3. **频率计算**：
   ```python
   if task_type == 'frequency':
       blocks.append(self.generate_compass_block(config))
       blocks.append(self.generate_bdfopt_block(config, hess='only'))
       blocks.append(self.generate_xuanyuan_block(config))
       blocks.append(self.generate_scf_block(config))
       blocks.append(self.generate_resp_block(config, norder=2))
   ```

## 结构优化算法

BDF 支持多种结构优化算法：

1. **最速下降法（Steepest descent）**：沿着负梯度的方向进行线搜索，对于远离极小点的结构效率高，但临近极小点时收敛慢，容易震荡

2. **共轭梯度法（Conjugate gradient）**：最速下降法的改良，每步优化方向与前一步的优化方向相组合，能一定程度缓解震荡问题

3. **牛顿法（Newton method）**：收敛很快，对于二次函数一步就可以走到极小点，但需要求解 Hessian 矩阵，计算非常昂贵

4. **准牛顿法（Quasi-Newton method）**：通过近似方法构建 Hessian 矩阵，最常用的是 BFGS 法。由于 Hessian 是近似构建的，达到收敛所需步数较牛顿法更多，但每一步耗时大为降低，所以优化总耗时显著减少

BDF 的结构优化是由 BDFOPT 模块来实现的，支持基于牛顿法和准牛顿法来进行极小值点结构和过渡态结构的优化。

## 结构优化中的溶剂化效应

BDF 支持在结构优化中考虑溶剂化效应。对于基态结构优化，在 SCF 模块中设置溶剂即可；对于激发态结构优化，需要在 TDDFT 和 RESP 模块中设置平衡溶剂化效应。

### 基态结构优化（溶剂化）

```bdf
$COMPASS
[geometry and basis]
$END

$BDFOPT
solver
 1
$END

$XUANYUAN
$END

$SCF
rks
dft functional
  b3lyp
solvent
  water
solmodel
  smd
Charge
 0
Spin
 1
$END

$RESP
geom
$END
```

### 激发态结构优化（溶剂化）

```bdf
$COMPASS
[geometry and basis]
$END

$BDFOPT
solver
 1
$END

$XUANYUAN
$END

$SCF
dft functional
  gb3lyp
rks
solModel
  iefpcm
solvent
  water
Charge
 0
Spin
 1
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

**说明**：
- 对于几何优化过程，溶剂有足够的时间进行响应，应考虑平衡溶剂效应
- 需要在 TDDFT 以及 RESP 模块中加入 `soleqlr` 关键词来表示平衡溶剂效应的计算
- 详细说明参见：`research/module_organization/SOLVENT_MODELS.md`

## 参考文档

- BDF 结构优化手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Optimization.rst`
- BDF 溶剂化模型手册：`/Users/bsuo/bdf/BDFManual/data/BDF-Manual-zhcn/source/guide/Solvent-Model.rst`
- BDFOPT 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (bdfopt 部分)
- RESP 模块关键词：`research/mapping_tables/keyword_mapping.yaml` (resp 部分)
- TDDFT 结构优化：`research/module_organization/TDDFT.md`
- SCF 单点能量计算：`research/module_organization/SCF_ENERGY.md`
- 溶剂化模型：`research/module_organization/SOLVENT_MODELS.md`

