"""
Quantum Chemistry Result Analyzer

This module provides AI-powered analysis of BDF calculation results.
"""

from typing import Dict, Optional, Any, List
from pathlib import Path

from ..parser.output_parser import BDFOutputParser
from ..prompt.analysis_prompts import (
    QUANTUM_CHEMISTRY_EXPERT_SYSTEM_PROMPT,
    build_analysis_prompt,
    get_system_prompt,
    Language,
)

try:
    from ...ai.client import AIClient
except ImportError:
    AIClient = None


class QuantumChemistryAnalyzer:
    """量子化学专家级结果分析器"""
    
    def __init__(self, ai_client: AIClient):
        """
        初始化分析器
        
        Args:
            ai_client: AI 客户端实例
        """
        if AIClient is None:
            raise ImportError(
                "AI client is not available. "
                "Please install required dependencies or ensure AI module is available."
            )
        
        if not isinstance(ai_client, AIClient):
            raise TypeError(f"ai_client must be an instance of AIClient, got {type(ai_client)}")
        
        self.ai_client = ai_client
        self.output_parser = BDFOutputParser()
    
    def analyze(
        self,
        output_file: str,
        input_file: Optional[str] = None,
        error_file: Optional[str] = None,
        task_type: Optional[str] = None,
        language: Language = "zh"
    ) -> Dict[str, Any]:
        """
        分析计算结果
        
        Args:
            output_file: BDF 输出文件路径
            input_file: BDF 输入文件路径（可选）
            error_file: 错误文件路径（可选）
            task_type: 计算任务类型（可选，如 'energy', 'optimize', 'frequency'）
            language: 分析语言，'zh' 表示中文，'en' 表示英文
        
        Returns:
            分析结果字典：
            {
                'summary': str,              # 简要总结
                'energy_analysis': str,      # 能量分析
                'geometry_analysis': str,    # 几何结构分析
                'convergence_analysis': str, # 收敛性分析
                'recommendations': List[str], # 建议
                'warnings': List[str],       # 警告
                'expert_insights': str,      # 专家见解
                'raw_analysis': str,         # 原始 AI 分析文本
            }
        """
        # 1. 解析输出文件
        parsed_data = self.output_parser.parse(output_file)
        
        # 2. 构建分析提示词
        prompt = build_analysis_prompt(
            parsed_data=parsed_data,
            input_file=input_file,
            error_file=error_file,
            task_type=task_type,
            language=language
        )
        
        # 3. 调用 AI 分析
        system_prompt = get_system_prompt(language)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.ai_client.chat(messages)
            raw_analysis = response if isinstance(response, str) else response.get('content', '')
        except Exception as e:
            if language == "en":
                raw_analysis = f"AI analysis failed: {str(e)}"
            else:
                raw_analysis = f"AI 分析失败: {str(e)}"
        
        # 4. 解析 AI 响应（简单版本，直接返回原始文本）
        result = self._parse_analysis_response(raw_analysis, parsed_data)
        
        return result
    
    def _parse_analysis_response(
        self,
        ai_response: str,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        解析 AI 分析响应
        
        这是一个简化版本，直接返回原始文本。
        未来可以改进为结构化解析。
        """
        result = {
            'summary': '',
            'energy_analysis': '',
            'geometry_analysis': '',
            'convergence_analysis': '',
            'recommendations': [],
            'warnings': parsed_data.get('warnings', []),
            'expert_insights': '',
            'raw_analysis': ai_response,
        }
        
        # 简单解析：尝试提取各个部分
        # 这是一个基础实现，可以根据需要改进
        
        # 提取总结（第一个段落或标题后的内容）
        summary_match = self._extract_section(ai_response, r'计算总结|总结|Summary', max_lines=5)
        if summary_match:
            result['summary'] = summary_match
        
        # 提取能量分析
        energy_match = self._extract_section(ai_response, r'能量分析|Energy', max_lines=10)
        if energy_match:
            result['energy_analysis'] = energy_match
        
        # 提取几何结构分析
        geometry_match = self._extract_section(ai_response, r'几何结构|Geometry', max_lines=10)
        if geometry_match:
            result['geometry_analysis'] = geometry_match
        
        # 提取收敛性分析
        convergence_match = self._extract_section(ai_response, r'收敛性|Convergence', max_lines=10)
        if convergence_match:
            result['convergence_analysis'] = convergence_match
        
        # 提取建议
        recommendations_match = self._extract_section(ai_response, r'建议|Recommendations', max_lines=20)
        if recommendations_match:
            # 尝试提取列表项
            import re
            items = re.findall(r'[-*]\s*(.+)', recommendations_match)
            result['recommendations'] = items if items else [recommendations_match]
        
        # 提取专家见解
        insights_match = self._extract_section(ai_response, r'专家见解|Expert|Insights', max_lines=15)
        if insights_match:
            result['expert_insights'] = insights_match
        
        # 如果没有提取到特定部分，将整个响应作为总结
        if not result['summary'] and ai_response:
            # 取前 500 字符作为总结
            result['summary'] = ai_response[:500] + ('...' if len(ai_response) > 500 else '')
        
        return result
    
    def _extract_section(self, text: str, pattern: str, max_lines: int = 10) -> str:
        """提取文本中的特定部分"""
        import re
        
        # 查找匹配的标题
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return ''
        
        start_pos = match.end()
        
        # 查找下一个标题或段落结束
        next_section = re.search(r'\n##?\s+', text[start_pos:])
        if next_section:
            end_pos = start_pos + next_section.start()
        else:
            end_pos = start_pos + 2000  # 限制长度
        
        section = text[start_pos:end_pos].strip()
        
        # 限制行数
        lines = section.split('\n')
        if len(lines) > max_lines:
            section = '\n'.join(lines[:max_lines]) + '...'
        
        return section

