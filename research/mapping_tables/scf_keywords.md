# BDF SCF 模块关键词列表（来自 `scf_input`）

> 来源：`/Users/bsuo/bdf/BDFAutoTest/bdf-pkg-full/source/scf_util/scfutil.F90` 中子程序 `scf_input`。
>
> 说明：`scf_input` 通过读取一行字符串 `cmd`，然后依次比较 `cmd(1:lenc).eq."KEYWORD"` 或 `cmd(1:n).eq."KEY"` 来解析 SCF 模块输入。
> 下表按功能大致分组列出所有关键词，便于 BDFEasyInput 做映射与校验。

---

## 1. SCF 类型（方法选择）

- **RHF**: 限制性 Hartree–Fock
- **UHF**: 非限制性 Hartree–Fock
- **ROHF**: 受限开壳层 Hartree–Fock
- **RKS**: 限制性 Kohn–Sham DFT
- **UKS**: 非限制性 Kohn–Sham DFT
- **ROKS**: 受限开壳层 Kohn–Sham DFT
- **UNDMOL**: 与 undmol 接口（`interface_und=1`）
- **MCCEPA**: 与 mccepa 接口（`interface_und=2`）

---

## 2. DFT / 交换-相关泛函与色散

- **DFT**: 读取一行交换/相关泛函名，传入 `bdf_setfunctional(fun_exchange, fun_correlation)`
- **RSALPHABETA**: Range-separated 参数 `rsalpha`, `rsbeta`
- **XCFUN** / **IXCFUN**: 选择 XCFUN / libxc 函数编号 `ixcfun`
- **HFEXCH**: 设定 HF 交换比例 `hfexchange`
- **D3**, **D3(BJ)**, **D2**, **D3ZERO**, **D3MZERO**, **D3MBJ**: DFT-D 色散选项，设置 `idftd3` / `iversion`
- **VERSION** / **DFTDVERSION**: 显式设置 `iversion`

---

## 3. 电荷 / 自旋 / 占据数控制

- **SPINMULTI**: 设置多重度 `toptask%task(18)`（2S+1）
- **SPIN**: 同上，设置自旋多重度
- **CHARGE**: 设置分子电荷 `toptask%task(17)`
- **OCCUP**: 总占据数，读取实数占据并映射为整占据 `nscls`, `nsalp`, `nsbet`
- **ALPHA**: Alpha 电子占据数
- **BETA**: Beta 电子占据数
- **IFPAIR**: MOM pair（delta-SCF）开关
- **HPOCCUP**: HOMO–LUMO 粒子–空穴占据控制（整体）
- **HPALPHA** / **HPBETA**: Alpha/Beta 通道的粒子–空穴占据控制
- **PINALPHA** / **PINBETA**: 固定 Alpha/Beta 轨道占据（pinned occupation）

---

## 4. 收敛与迭代控制

- **MAXITER** / **MAXCYCLE**: 最大迭代次数 `maxiter`
- **THRESHCONV** / **THRESHCONVERG**: 能量 / 密度收敛阈值 `thresh_ene`, `thresh_den`
- **THRENE**: 能量收敛阈值
- **THRDEN**: 密度收敛阈值
- **THRDIIS**: DIIS 残差收敛阈值 `thresh_diis`
- **VSHIFT**: 轨道能量 level shift；与 Fermi smearing 互斥
- **DAMP**: 密度混合阻尼参数
- **ICHECK**: 调试输出级别 `icheck`
- **IAUFBAU**: 自洽场占据按 Aufbau 原则（或不按）
- **DEFORM**: 变形阈值 `thrd_deform`
- **IFNODELTAP** / **NODELTAP**: 关闭 ΔP 迭代（与 `ifdeltap` 相关）
- **FIXDIF**: 控制 Fock 差分修正 `Fixdif`
- **IROFOCK**: ROHF Fock 耦合参数选择
- **FCA**, **FOA**, **FVA**: ROFOCK 耦合参数（核心/占据/虚轨）

---

## 5. 数值积分 / 网格 / Coulomb / COSX

> 这些关键词大多由 `numint_input` 和 `pcm_input_read` 进一步解释，这里只列出在 SCF 模块中出现的关键字。

- **MAXMEM**: DFT 数值积分可用最大内存 `maxmem`
- **UPDEN**: 密度更新控制 `upden`
- **FULLVXC**: 控制是否使用全 v_xc `fullvxc`
- **RSALPHABETA**: Range-separated 参数（见上）
- **THRPCOSX**: COSX 阈值 `thresh_pcosx`
- **PSNXYZ**: Vex 网格点数目
- **PSXYZ**: 网格边界（坐标范围）
- **XCFUN** / **IXCFUN**: 选择 XCFUN / libxc 函数编号
- **HFEXCH**: HF 交换比例

---

## 6. 直接 / 非直接 SCF 与积分筛选

- **OPTSCR**: 积分筛选选项 `optscreen`
- **JENGIN**: 选择特殊 J 引擎实现 `jengine`
- **NOK2PR**: 关闭 primitive K 积分筛选 `k2primscreen=.false.`
- **RUDENB**: `rudenberg` 开关（Ruedenberg 相关分析）
- **FMM**: 启用 FMM 相关控制 `fmm_control%fmm_enable`
- **WSIND**: FMM wsindex 选择

---

## 7. 轨道 / 初始猜测 / 线性相关检查

- **ATOMGUESSHF**: 使用原子 HF 初始猜测
- **GUESS**: 初始猜测选择（NDDO/Hückel 等）
- **MOLDEN**: 输出 MOLDEN 轨道文件
- **PYSCFORB**: 输出 PySCF 兼容轨道文件
- **NOSCFORB**: 不输出 SCF 轨道
- **OUTAOOVERLAP**: 输出 AO 重叠矩阵
- **KRATZWF**: 读取 Kratzer 波函数
- **CHECKLIN**: 检查基组线性相关
- **TOLLIN**: 线性相关容差
- **LOWDINLIN**: 使用 Löwdin 正交化方式处理线性相关
- **SKIPAOLIN**: 跳过 AO 线性相关检查
- **WRITEMAT**: 输出矩阵（Fock / 密度等）
- **IPRTMO**: 控制 MO 输出详细程度 `iprtmo`
- **IPRT**: 一般打印级别 `iprt`
- **IGNORERR** / **IGNOREERR**: 忽略某些错误继续运行

---

## 8. DFT-D / 近似 / 混合参数

- **D3**, **D3(BJ)**, **D2**, **D3ZERO**, **D3MZERO**, **D3MBJ**: DFT-D 相关关键词（控制 `idftd3` 与 `iversion`）
- **VERSION** / **DFTDVERSION**: 显式设置 DFT-D 版本参数
- **FACEX**: 修正 HF 交换比例（`rscfctrl(8)`）
- **FACCO**: 修正相关部分比例（`rscfctrl(9)`）

---

## 9. 压缩 / 片段 / FLMO（Localized MOs）

- **FLMO**: 启用 fragment-local MOs（FLMO）
- **EMBEDFRAG**: 片段嵌入控制 `ictrl_fragscf`
- **THRSLMOTAI**: LMO 尾部阈值 `thrs_lmotail`
- **CUTLMOTAIL**: 是否截断 LMO 尾部
- **DIAGFLMOFO**: 是否对 FLMO Fock 进行对角化
- **FVLDP**: FLMO/fragment 相关参数（`ldp_v` 等）
- **FLMOMAP**: 控制 FLMO 映射输出
- **NOREORDERFLMO**: 禁止重新排序 FLMO

---

## 10. 对称性与特殊 SCF 模式

- **SO3Z**: 针对单原子 SO(3) 对称 SCF
- **LZSYM**: 线性分子 Lz 对称
- **LZCLEAN**: 清理 Lz 对称 Fock
- **MCDENSYM**: MCSCF/CASSCF 密度矩阵对称化选项
- **NOTOPT** / **ONEITER**: 仅单次迭代、不做真正优化
- **FOCKONLY**: 只构造 Fock，不做 SCF
- **ATOMONLY**: 仅原子计算
- **ATOMORB**: 仅原子轨道
- **ATOMMP2**: 原子 MP2 相关设置

---

## 11. PCM / 溶剂相关

- **PCMSOL**: PCM 溶剂开关（结合 `pcm_input_read` 与 `solvent_input`）

（更完整的 PCM / 溶剂参数由 `solvent_input` 与 `pcm_input_read` 解析，这里只标记 SCF 层的入口关键字。）

---

## 12. iOI / 环境嵌入相关关键词

- **IOI**: 启用 iOI 功能
- **IOIITER**: iOI 迭代次数
- **IOITOT** / **IOISUB**: 总体系 / 子体系标记
- **IOINOENV** / **IOINSUB**: 环境 / 子系统设置
- **IOIENVTYPE**: 环境类型
- **IOICOMPARETYPE**: 比较类型
- **IOITHRESHFOCK**: Fock 阈值
- **IOIDIRECT**: 直接模式
- **IOISAVEGRID** / **IOIREADGRID**: 网格保存 / 读取
- **IOIUSETOTCOUL**: 使用总 Coulomb 势
- **IOIZW** / **IOIZWCOULPOT**: iOIZW 相关选项

---

## 13. SQM / SMH / 其它控制

- **SQM**: SQM 相关控制 `logic_sqm`
- **NOPOP**: 不做 population 分析
- **NOMULTIPOLE**: 不做多极矩分析
- **SEPEJK**: 分离 EJK（electrostatic/J/K）计算
- **SEPEXC**: 分离 exchange–correlation 计算
- **NOORTHGUESS**: 不对初始猜测做正交化
- **SMH**: 启用 SMH（默认已开启）
- **NOSMH**: 禁用 SMH

---

## 14. DFT 相关内部控制（不直接暴露给用户，但在输入中可设置）

- **ROMIGA** / **ROMEGA** / **OMEGA** / **RS**: 某些 range-separated / 经验参数（通过 `romiga`、`rsalpha`、`rsbeta` 控制）
- **PCC**: picture-change correction 相关开关

---

## 15. 结束标记

- **$END**: 结束 SCF 模块输入（`cmd(1:lenc).eq."$END"`）

---

本文件仅基于 `scf_input` 的 Fortran 解析逻辑进行关键词抽取，适合作为：

- BDFEasyInput → BDF 翻译器中 SCF 关键词白名单 / 参考；
- 文档自动生成的基础；
- 将来做高级校验（比如检测不兼容组合）时的输入源。


