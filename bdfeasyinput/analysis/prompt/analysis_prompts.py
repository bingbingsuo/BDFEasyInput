"""
Analysis Prompt Templates

This module provides prompt templates for AI-powered analysis of BDF results.
"""

from typing import Dict, List, Optional, Any


QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT = """你是一位资深的量子化学计算专家，专门分析 BDF 量子化学计算软件的输出结果。

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


def format_geometry(geometry: List[Dict[str, Any]]) -> str:
    """格式化几何结构为字符串"""
    if not geometry:
        return "未找到几何结构信息"
    
    lines = ["原子坐标（单位：Angstrom 或 Bohr）："]
    for atom in geometry:
        element = atom.get('element', '?')
        x = atom.get('x', 0.0)
        y = atom.get('y', 0.0)
        z = atom.get('z', 0.0)
        lines.append(f"  {element:3s}  {x:12.6f}  {y:12.6f}  {z:12.6f}")
    
    return "\n".join(lines)


def format_frequencies(frequencies: List[float]) -> str:
    """格式化频率为字符串"""
    if not frequencies:
        return "未找到频率信息"
    
    lines = ["振动频率（单位：cm⁻¹）："]
    for i, freq in enumerate(frequencies, 1):
        lines.append(f"  {i:3d}. {freq:10.2f} cm⁻¹")
    
    return "\n".join(lines)


def build_analysis_prompt(
    parsed_data: Dict[str, Any],
    input_file: Optional[str] = None,
    error_file: Optional[str] = None,
    task_type: Optional[str] = None
) -> str:
    """
    构建分析提示词
    
    Args:
        parsed_data: 解析后的输出数据
        input_file: 输入文件路径（可选）
        error_file: 错误文件路径（可选）
        task_type: 计算任务类型（可选）
    
    Returns:
        完整的分析提示词
    """
    prompt_parts = []
    
    prompt_parts.append("请分析以下 BDF 量子化学计算结果：\n")
    
    # 计算任务类型
    if task_type:
        prompt_parts.append(f"**计算任务类型**：{task_type}\n")
    
    # 能量信息
    energy = parsed_data.get('energy')
    scf_energy = parsed_data.get('scf_energy')
    converged = parsed_data.get('converged', False)
    
    prompt_parts.append("**计算结果**：")
    if energy is not None:
        prompt_parts.append(f"- 总能量：{energy:.10f} Hartree")
    if scf_energy is not None and scf_energy != energy:
        prompt_parts.append(f"- SCF 能量：{scf_energy:.10f} Hartree")
    prompt_parts.append(f"- SCF 收敛：{'是' if converged else '否'}")
    prompt_parts.append(f"- 计算状态：{'成功' if converged else '未收敛或失败'}\n")
    
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
6. **方法评估**：评估计算方法和基组的适用性
7. **专业建议**：提供改进建议和进一步计算建议
8. **专家见解**：提供深度的专业分析

请使用 Markdown 格式组织内容，使用清晰的标题和列表。
""")
    
    return "\n".join(prompt_parts)

