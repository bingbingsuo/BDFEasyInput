"""
Analysis Prompt Templates

This module provides prompt templates for AI-powered analysis of BDF results.
Supports both Chinese and English languages.
"""

from typing import Dict, List, Optional, Any

# Language type (compatible with Python 3.7+)
try:
    from typing import Literal
    Language = Literal["zh", "en"]
except ImportError:
    # Python 3.7 compatibility: use typing_extensions if available
    try:
        from typing_extensions import Literal
        Language = Literal["zh", "en"]
    except ImportError:
        Language = str  # Fallback to str if typing_extensions not available
    Language = str  # Fallback to str for older Python versions

# ============================================================================
# System Prompts
# ============================================================================

QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_ZH = """你是一位资深的量子化学计算专家，专门分析 BDF 量子化学计算软件的输出结果。

你的任务是：
1. 分析计算结果的质量和可靠性
2. 解释计算结果的意义
3. 识别潜在的问题和警告
4. 提供专业的建议和见解
5. 用通俗易懂的语言向用户解释复杂的量子化学概念

分析重点：
- **能量分析**：总能量、SCF 能量、相对能量等
- **几何结构**：键长、键角、二面角、对称性等
- **收敛性**：SCF 收敛、几何优化收敛等
- **电子结构**：轨道能量、HOMO-LUMO 能隙、电子密度等
- **振动分析**：频率、红外强度、热力学性质等
- **方法评估**：计算方法的适用性、基组质量等

输出要求：
- 使用专业但易懂的语言
- 提供具体的数值和单位
- 给出明确的结论和建议
- 指出需要注意的问题
- 使用 Markdown 格式组织内容
"""

# Backward compatibility: use Chinese as default
QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT = QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_ZH

# Import English prompts
try:
    from .analysis_prompts_en import (
        QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_EN,
        format_geometry_en,
        format_frequencies_en,
        format_tddft_calculations_en,
        build_analysis_prompt_en,
    )
except ImportError:
    QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_EN = None
    format_geometry_en = None
    format_frequencies_en = None
    format_tddft_calculations_en = None
    build_analysis_prompt_en = None


def get_system_prompt(language: Language = "zh") -> str:
    """
    Get system prompt based on language
    
    Args:
        language: Language code, "zh" for Chinese, "en" for English
    
    Returns:
        System prompt string
    """
    if language == "en":
        if QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_EN is None:
            raise ValueError("English prompts not available. Please ensure analysis_prompts_en.py is properly imported.")
        return QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_EN
    else:
        return QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT_ZH


def format_geometry(geometry: List[Dict[str, Any]]) -> str:
    """格式化几何结构为字符串"""
    if not geometry:
        return "未找到几何结构信息"
    
    # 检测单位（从第一个原子获取，假设所有原子使用相同单位）
    units = geometry[0].get('units', 'bohr').lower() if geometry else 'bohr'
    
    # 根据单位选择标签
    if units == 'bohr':
        unit_label = "Bohr（原子单位，1 Bohr ≈ 0.529177 Å）"
    elif units == 'angstrom' or units == 'ang':
        unit_label = "Angstrom（Å）"
    else:
        unit_label = f"{units}（未指定）"
    
    lines = [f"原子坐标（单位：{unit_label}）："]
    lines.append("")
    lines.append("  原子      X              Y              Z")
    lines.append("  " + "-" * 50)
    for atom in geometry:
        element = atom.get('element', '?')
        x = atom.get('x', 0.0)
        y = atom.get('y', 0.0)
        z = atom.get('z', 0.0)
        lines.append(f"  {element:3s}  {x:12.6f}  {y:12.6f}  {z:12.6f}")
    
    lines.append("")
    lines.append(f"  注：BDF 输出中的坐标单位为 Bohr（从 'Cartcoord(Bohr)' 部分提取）")
    
    return "\n".join(lines)


def format_frequencies(frequencies: List[float]) -> str:
    """格式化频率为字符串"""
    if not frequencies:
        return "未找到频率信息"
    
    lines = ["振动频率（单位：cm⁻¹）："]
    for i, freq in enumerate(frequencies, 1):
        lines.append(f"  {i:3d}. {freq:10.2f} cm⁻¹")
    
    return "\n".join(lines)


def format_tddft_calculations(tddft: List[Dict[str, Any]]) -> str:
    """格式化 TDDFT 计算结果为字符串"""
    if not tddft:
        return "未找到 TDDFT 计算结果"
    
    lines = []
    for idx, calc in enumerate(tddft, 1):
        lines.append(f"TDDFT 计算块 {idx}：")
        
        # 计算方法说明
        approx_method = calc.get('approximation_method')
        itda = calc.get('itda')
        if approx_method:
            lines.append(f"  - 计算方法：{approx_method}")
        if itda is not None:
            lines.append(f"  - ITDA 参数：{itda}")
            if itda == 1:
                lines.append("    说明：采用 TDA 近似 (Tamm–Dancoff Approximation)")
            elif itda == 0:
                lines.append("    说明：采用普通 TDDFT (Time-Dependent Density Functional Theory)")
        
        # 其他参数
        isf = calc.get('isf')
        if isf is not None:
            spin_dir = calc.get('spin_flip_direction')
            if spin_dir:
                lines.append(f"  - 自旋翻转参数 (ISF)：{isf} ({spin_dir})")
            else:
                lines.append(f"  - 自旋翻转参数 (ISF)：{isf}")
        
        ialda = calc.get('ialda')
        if ialda is not None:
            lines.append(f"  - IALDA 参数：{ialda}")
        
        method = calc.get('method')
        if method:
            lines.append(f"  - 方法：{method}")
        
        # 激发态信息
        states = calc.get('states', [])
        isf = calc.get('isf')
        is_spin_flip = (isf is not None and isf != 0)
        
        if states:
            lines.append(f"  - 激发态数量：{len(states)}")
            if is_spin_flip:
                lines.append("  - ⚠️ 这是 Spin-Flip 计算：ISF ≠ 0，振子强度必为零（正常现象）")
            lines.append("  - 前3个激发态：")
            for state in states[:3]:
                idx_state = state.get('index', '?')
                energy = state.get('energy_ev', 0)
                wavelength = state.get('wavelength_nm', 0)
                osc = state.get('oscillator_strength', 0)
                osc_str = f"{osc:.6f}"
                if is_spin_flip and osc == 0:
                    osc_str += " (spin-flip，正常)"
                lines.append(f"    态 {idx_state}：能量 = {energy:.4f} eV, "
                           f"波长 = {wavelength:.2f} nm, "
                           f"振子强度 = {osc_str}")
        lines.append("")
    
    return "\n".join(lines)


def build_analysis_prompt(
    parsed_data: Dict[str, Any],
    input_file: Optional[str] = None,
    error_file: Optional[str] = None,
    task_type: Optional[str] = None,
    language: Language = "zh"
) -> str:
    """
    构建分析提示词
    
    Args:
        parsed_data: 解析后的输出数据
        input_file: 输入文件路径（可选）
        error_file: 错误文件路径（可选）
        task_type: 计算任务类型（可选）
        language: 语言代码，"zh" 表示中文，"en" 表示英文
    
    Returns:
        完整的分析提示词
    """
    # Use English version if requested
    if language == "en":
        if build_analysis_prompt_en is None:
            raise ValueError("English prompts not available. Please ensure analysis_prompts_en.py is properly imported.")
        return build_analysis_prompt_en(parsed_data, input_file, error_file, task_type)
    
    # Chinese version (default)
    prompt_parts = []
    
    prompt_parts.append("请分析以下 BDF 量子化学计算结果：\n")
    
    # 计算任务类型
    if task_type:
        prompt_parts.append(f"**计算任务类型**：{task_type}\n")
    
    # 能量信息
    energy = parsed_data.get('energy')
    scf_energy = parsed_data.get('scf_energy')
    converged = parsed_data.get('converged', False)
    properties = parsed_data.get('properties', {})
    
    prompt_parts.append("**计算结果**：")
    if energy is not None:
        prompt_parts.append(f"- 总能量 (E_tot)：{energy:.10f} Hartree")
    if scf_energy is not None and scf_energy != energy:
        prompt_parts.append(f"- SCF 能量：{scf_energy:.10f} Hartree")
    prompt_parts.append(f"- SCF 收敛：{'是' if converged else '否'}")
    prompt_parts.append(f"- 计算状态：{'成功' if converged else '未收敛或失败'}\n")
    
    # SCF 能量分量
    if properties:
        prompt_parts.append("**SCF 能量分量说明**：")
        prompt_parts.append("")
        prompt_parts.append("BDF 输出中的关键能量定义：")
        prompt_parts.append("- **E_tot**：BO近似下电子总能量，包含了核排斥能")
        prompt_parts.append("- **E_ele**：电子能量，不含核排斥能")
        prompt_parts.append("- **E_nn**：核排斥能")
        prompt_parts.append("- **关系**：E_tot = E_ele + E_nn")
        prompt_parts.append("")
        prompt_parts.append("- **E_1e**：单电子能量")
        prompt_parts.append("- **E_ne**：原子核对电子的吸引势能")
        prompt_parts.append("- **E_kin**：电子的动能")
        prompt_parts.append("- **关系**：E_1e = E_ne + E_kin")
        prompt_parts.append("")
        prompt_parts.append("- **E_ee**：双电子相互作用能，包括库伦排斥和电子交换能")
        prompt_parts.append("- **E_xc**：电子交换相关能，来自DFT计算")
        prompt_parts.append("- **Virial Ratio**：维里比，对于非相对论全电子体系应该接近2.0")
        prompt_parts.append("")
        
        # 显示实际数值
        e_tot = properties.get('E_tot') or energy
        e_ele = properties.get('E_ele')
        e_nn = properties.get('E_nn')
        e_1e = properties.get('E_1e')
        e_ne = properties.get('E_ne')
        e_kin = properties.get('E_kin')
        e_ee = properties.get('E_ee')
        e_xc = properties.get('E_xc')
        virial_ratio = properties.get('virial_ratio')
        
        if e_tot is not None or e_ele is not None or e_nn is not None:
            prompt_parts.append("实际数值：")
            if e_tot is not None:
                prompt_parts.append(f"  E_tot = {e_tot:.10f} Hartree")
            if e_ele is not None:
                prompt_parts.append(f"  E_ele = {e_ele:.10f} Hartree")
            if e_nn is not None:
                prompt_parts.append(f"  E_nn = {e_nn:.10f} Hartree")
            prompt_parts.append("")
        
        if e_1e is not None or e_ne is not None or e_kin is not None:
            if e_ne is not None:
                prompt_parts.append(f"  E_ne = {e_ne:.10f} Hartree")
            if e_kin is not None:
                prompt_parts.append(f"  E_kin = {e_kin:.10f} Hartree")
            if e_1e is not None:
                prompt_parts.append(f"  E_1e = {e_1e:.10f} Hartree")
            prompt_parts.append("")
        
        if e_ee is not None:
            prompt_parts.append(f"  E_ee = {e_ee:.10f} Hartree")
        if e_xc is not None:
            prompt_parts.append(f"  E_xc = {e_xc:.10f} Hartree")
        if virial_ratio is not None:
            prompt_parts.append(f"  Virial Ratio = {virial_ratio:.6f}")
            if abs(virial_ratio - 2.0) < 0.01:
                prompt_parts.append("  (接近2.0，计算质量良好)")
            else:
                diff = abs(virial_ratio - 2.0)
                prompt_parts.append(f"  (偏离2.0约{diff:.4f}，需检查)")
        prompt_parts.append("")
        
        # SCF 收敛标准
        thresh_ene = properties.get('scf_conv_thresh_ene')
        thresh_den = properties.get('scf_conv_thresh_den')
        final_deltae = properties.get('final_deltae')
        final_deltad = properties.get('final_deltad')
        
        if thresh_ene is not None or thresh_den is not None or final_deltae is not None or final_deltad is not None:
            prompt_parts.append("**SCF 收敛标准与结果**：")
            prompt_parts.append("")
            prompt_parts.append("收敛标准（阈值）：")
            prompt_parts.append("- **THRENE**：能量收敛阈值，能量变化需要小于此值")
            prompt_parts.append("- **THRDEN**：密度矩阵收敛阈值，密度矩阵RMS变化需要小于此值")
            prompt_parts.append("")
            
            if thresh_ene is not None:
                prompt_parts.append(f"  THRENE = {thresh_ene:.2e} Hartree")
            if thresh_den is not None:
                prompt_parts.append(f"  THRDEN = {thresh_den:.2e}")
            prompt_parts.append("")
            
            if final_deltae is not None or final_deltad is not None:
                prompt_parts.append("实际收敛值：")
                if final_deltae is not None:
                    prompt_parts.append(f"  Final DeltaE = {final_deltae:.2e} Hartree")
                if final_deltad is not None:
                    prompt_parts.append(f"  Final DeltaD = {final_deltad:.2e}")
                prompt_parts.append("")
    
    # 几何结构
    geometry = parsed_data.get('geometry', [])
    if geometry:
        prompt_parts.append("**几何结构**：")
        prompt_parts.append(format_geometry(geometry))
        prompt_parts.append("")
    
    # 频率
    frequencies = parsed_data.get('frequencies', [])
    if frequencies:
        prompt_parts.append("**振动频率**：")
        prompt_parts.append(format_frequencies(frequencies))
        prompt_parts.append("")
    
        # TDDFT 信息
        tddft = parsed_data.get('tddft', [])
        if tddft:
            prompt_parts.append("**TDDFT 计算结果**：")
            prompt_parts.append(format_tddft_calculations(tddft))
        
        # 非平衡溶剂化校正
        solvent_corr = properties.get('solvent_noneq_corrections')
        if solvent_corr:
            prompt_parts.append("")
            prompt_parts.append("**非平衡溶剂化（cLR）校正**：")
            for corr in solvent_corr:
                st = corr.get("state_index")
                cv = corr.get("corrected_vertical_energy_ev")
                ne = corr.get("noneq_solvation_free_energy_ev")
                eq = corr.get("eq_solvation_free_energy_ev")
                clr = corr.get("excitation_energy_correction_ev")
                prompt_parts.append(f"- 态 {st}: 校正垂直激发能 = {cv:.4f} eV; "
                                    f"非平衡溶剂化自由能 = {ne:.4f} eV; "
                                    f"平衡溶剂化自由能 = {eq:.4f} eV; "
                                    f"cLR 激发能校正 = {clr:.4f} eV")
        
        # 非平衡溶剂化方法提示
        noneq_method = properties.get('solvent_noneq_method')
        if noneq_method:
            prompt_parts.append("")
            if noneq_method == "clr_linear_response":
                prompt_parts.append("本计算使用 cLR（线性响应）非平衡溶剂化校正。")
            elif noneq_method == "ptSS_state_specific":
                prompt_parts.append("本计算使用 ptSS（态特定，一阶微扰 resp）非平衡溶剂化校正。")
            
            # TDDFT JK 内存信息
            if tddft:
                first_calc = tddft[0]  # 取第一个计算块的内存信息（通常所有块使用相同的设置）
                jk_estimated = first_calc.get('jk_estimated_memory_mb')
                jk_max = first_calc.get('jk_max_memory_mb')
                roots_per_pass = first_calc.get('roots_per_pass')
                n_exit = first_calc.get('n_exit')
                
                if jk_estimated is not None or jk_max is not None or roots_per_pass is not None:
                    prompt_parts.append("")
                    prompt_parts.append("**TDDFT JK 算符内存信息**：")
                    if jk_estimated is not None:
                        prompt_parts.append(f"- 估算的JK算符内存: {jk_estimated:.3f} MB")
                        prompt_parts.append("  - TDDFT先估算需要多少内存来计算JK算符")
                    if jk_max is not None:
                        prompt_parts.append(f"- JK算符最大内存设置: {jk_max:.3f} MB")
                        prompt_parts.append("  - 系统设置的计算JK算符的最大内存")
                    if roots_per_pass is not None:
                        prompt_parts.append(f"- 每次积分计算可计算的根数: {roots_per_pass}")
                        if first_calc.get('itda') == 1:
                            prompt_parts.append("  - 这是TDA计算，TDA可计算的根的数目是RPA计算的2倍")
                        else:
                            prompt_parts.append("  - 这是TDDFT计算")
                    if n_exit is not None:
                        prompt_parts.append(f"- 用户要求的每个不可约表示的根数: {n_exit}")
                        if roots_per_pass is not None and n_exit > roots_per_pass:
                            prompt_parts.append("  - ⚠️ 用户要求的根数大于每次积分计算可计算的根数")
                            prompt_parts.append("  - 建议：使用MEMJKOP关键词增加内存以提高计算效率")
                            prompt_parts.append("  - MEMJKOP参数格式：\"int+M\"，如1024M，表示每OpenMP线程使用1024兆字节")
                            prompt_parts.append("  - 实际使用内存还需乘以OpenMP线程的数目")
    
    # 警告
    warnings = parsed_data.get('warnings', [])
    if warnings:
        prompt_parts.append("**警告信息**：")
        for i, warning in enumerate(warnings, 1):
            prompt_parts.append(f"{i}. {warning}")
        prompt_parts.append("")
    
    # 错误
    errors = parsed_data.get('errors', [])
    if errors:
        prompt_parts.append("**错误信息**：")
        for i, error in enumerate(errors, 1):
            prompt_parts.append(f"{i}. {error}")
        prompt_parts.append("")
    
    # 输入文件信息
    if input_file:
        prompt_parts.append(f"**输入文件**：{input_file}\n")
    
    # 错误文件信息
    if error_file:
        prompt_parts.append(f"**错误文件**：{error_file}\n")
    
    prompt_parts.append("""
请提供以下分析内容：

1. **计算总结**：简要总结计算结果
2. **能量分析**：分析能量的合理性和意义
3. **几何结构分析**（如果适用）：分析键长、键角等结构特征
4. **收敛性分析**：评估收敛质量
5. **振动分析**（如果适用）：分析频率和热力学性质
6. **TDDFT 分析**（如果适用）：分析激发态能量、振子强度、计算方法（TDA vs TDDFT）等
7. **方法评估**：评估计算方法和基组的适用性
8. **专业建议**：提供改进建议和进一步计算建议
9. **专家见解**：提供深度的专业分析

请使用 Markdown 格式组织内容，使用清晰的标题和列表。
""")
    
    return "\n".join(prompt_parts)


# Convenience function to get analysis prompt in specified language
def get_analysis_prompt(
    parsed_data: Dict[str, Any],
    input_file: Optional[str] = None,
    error_file: Optional[str] = None,
    task_type: Optional[str] = None,
    language: Language = "zh"
) -> str:
    """
    Get analysis prompt in specified language
    
    Args:
        parsed_data: Parsed output data
        input_file: Input file path (optional)
        error_file: Error file path (optional)
        task_type: Task type (optional)
        language: Language code, "zh" for Chinese, "en" for English
    
    Returns:
        Complete analysis prompt
    """
    return build_analysis_prompt(parsed_data, input_file, error_file, task_type, language)

