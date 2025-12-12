"""
Prompt Templates for AI Task Planning

This module contains prompt templates for generating BDF calculation tasks.
"""

from typing import Optional, Dict, Any, List


SYSTEM_PROMPT = """你是一个量子化学计算专家，专门帮助用户规划 BDF 量子化学计算任务。

你的任务是根据用户的自然语言描述，生成标准的 YAML 格式计算输入文件。

你的输出应该是有效的 YAML 格式，包含以下部分：
1. task: 计算类型（energy, optimize, frequency, tddft 等）
2. molecule: 分子结构（坐标、电荷、自旋多重度）
3. method: 计算方法（DFT 泛函、基组等）
4. settings: 计算设置（收敛标准、迭代次数等）

**重要提醒 - 自旋多重度（multiplicity）**：
- **必须提醒用户设置自旋多重度**，这是计算的关键参数
- 自旋多重度 = 2S + 1，其中 S 是总自旋量子数
- 如果用户未指定，BDF 将按以下默认规则处理：
  * 偶数电子数 → 自旋多重度 = 1（闭壳层）
  * 奇数电子数 → 自旋多重度 = 2（开壳层）
- **强烈建议**：在生成 YAML 时，如果用户未明确指定，应该：
  1. 根据分子化学式推断合理的自旋多重度
  2. 如果无法确定，在 YAML 中添加注释提醒用户检查
  3. 对于自由基、激发态等特殊情况，必须明确询问用户

请遵循以下原则：
- 如果用户没有指定方法，推荐合适的方法和基组
- **如果用户没有指定自旋多重度，必须根据分子特征推断或提醒用户**
- 确保参数合理且兼容
- 对于复杂体系，给出专业建议
- 输出必须是有效的 YAML 格式

支持的 DFT 泛函：PBE, PBE0, B3LYP, M06-2X 等
支持的基组：cc-pVDZ, cc-pVTZ, 6-31G*, def2-SVP 等

**输出要求**：
- 只输出 YAML 格式的内容，不要添加额外的说明文字
- YAML 必须是有效的、可以直接使用的格式
- 坐标格式：每行一个原子，格式为 "原子符号 X Y Z"（列表项）
- 单位：默认使用 angstrom
"""


EXAMPLES: List[Dict[str, str]] = [
    {
        "user_query": "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组",
        "yaml_output": """task:
  type: energy
  description: "H2O single point energy calculation"

molecule:
  name: "Water"
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z (单位: angstrom)
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom

method:
  type: dft
  functional: pbe0
  basis: cc-pvdz

settings:
  scf:
    convergence: 1e-8
    max_iterations: 100"""
    },
    {
        "user_query": "优化苯分子的几何结构，使用 B3LYP 方法",
        "yaml_output": """task:
  type: optimize
  description: "Benzene geometry optimization"

molecule:
  name: "Benzene"
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z (单位: angstrom)
    - C  0.0000 1.3970 0.0000
    - C  1.2098 0.6985 0.0000
    - C  1.2098 -0.6985 0.0000
    - C  0.0000 -1.3970 0.0000
    - C -1.2098 -0.6985 0.0000
    - C -1.2098 0.6985 0.0000
    - H  0.0000 2.4810 0.0000
    - H  2.1473 1.2405 0.0000
    - H  2.1473 -1.2405 0.0000
    - H  0.0000 -2.4810 0.0000
    - H -2.1473 -1.2405 0.0000
    - H -2.1473 1.2405 0.0000
  units: angstrom

method:
  type: dft
  functional: b3lyp
  basis: 6-31g*

settings:
  scf:
    convergence: 1e-8
    max_iterations: 100
  optimization:
    max_iterations: 100
    convergence: 1e-8"""
    },
    {
        "user_query": "计算一个过渡金属配合物的激发态",
        "yaml_output": """task:
  type: tddft
  description: "Transition metal complex excited state calculation"

molecule:
  name: "Transition metal complex"
  charge: 0
  multiplicity: 1
  coordinates:
    # 注意：这里需要用户提供具体的分子坐标
    # 对于过渡金属配合物，建议使用相对论基组
  units: angstrom

method:
  type: dft
  functional: pbe0
  basis: def2-tzvp
  # 对于过渡金属，建议使用相对论效应

settings:
  scf:
    convergence: 1e-8
    max_iterations: 200
  tddft:
    nstates: 10
    singlet: true
    triplet: false"""
    },
]


def build_system_prompt(include_examples: bool = True) -> str:
    """
    Build the system prompt for task planning.
    
    Args:
        include_examples: Whether to include few-shot examples.
    
    Returns:
        Complete system prompt string.
    """
    prompt = SYSTEM_PROMPT
    
    if include_examples:
        examples_text = "\n\n**示例**：\n\n"
        for i, example in enumerate(EXAMPLES, 1):
            examples_text += f"示例 {i}:\n"
            examples_text += f"用户: {example['user_query']}\n\n"
            examples_text += "输出:\n```yaml\n"
            examples_text += example['yaml_output']
            examples_text += "\n```\n\n"
        
        prompt += examples_text
    
    return prompt


def build_user_prompt(
    user_query: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build the user prompt from the user's query.
    
    Args:
        user_query: User's natural language query.
        context: Optional context information (e.g., previous conversation).
    
    Returns:
        Formatted user prompt.
    """
    prompt = f"请根据以下描述生成 YAML 配置：\n\n{user_query}"
    
    if context:
        prompt += "\n\n上下文信息："
        for key, value in context.items():
            prompt += f"\n- {key}: {value}"
    
    prompt += "\n\n请输出有效的 YAML 格式："
    
    return prompt


def get_examples() -> List[Dict[str, str]]:
    """
    Get example queries and their expected YAML outputs.
    
    Returns:
        List of example dictionaries with 'user_query' and 'yaml_output' keys.
    """
    return EXAMPLES.copy()


def get_method_recommendations(molecule_info: Dict[str, Any]) -> str:
    """
    Generate method recommendations based on molecule information.
    
    Args:
        molecule_info: Dictionary containing molecule information (elements, size, etc.).
    
    Returns:
        Recommendation text.
    """
    recommendations = []
    
    # Check for transition metals
    transition_metals = [
        "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
        "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
        "La", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"
    ]
    
    elements = molecule_info.get("elements", [])
    has_transition_metal = any(elem in transition_metals for elem in elements)
    
    num_atoms = molecule_info.get("num_atoms", 0)
    
    if has_transition_metal:
        recommendations.append("- 检测到过渡金属元素，建议使用相对论基组（如 def2-TZVP）")
        recommendations.append("- 建议使用 PBE0 或 B3LYP 泛函")
    
    if num_atoms > 50:
        recommendations.append("- 体系较大，建议使用较小的基组以提高计算效率")
    
    if not recommendations:
        recommendations.append("- 对于一般有机分子，建议使用 PBE0/cc-pVDZ 或 B3LYP/6-31G*")
    
    return "\n".join(recommendations) if recommendations else ""

