"""
Analysis Report Generator

This module provides functionality to generate analysis reports in various formats.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class AnalysisReportGenerator:
    """分析报告生成器"""
    
    def __init__(self, format: str = "markdown"):
        """
        初始化报告生成器
        
        Args:
            format: 报告格式，支持 'markdown', 'html', 'text'
        """
        self.format = format.lower()
        if self.format not in ['markdown', 'html', 'text']:
            raise ValueError(f"Unsupported format: {format}. Supported: markdown, html, text")
    
    def generate(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        生成分析报告
        
        Args:
            analysis_result: AI 分析结果
            parsed_data: 解析后的原始数据（可选）
            output_file: 输出文件路径（可选）
        
        Returns:
            报告内容字符串
        """
        if self.format == 'markdown':
            report = self._generate_markdown(analysis_result, parsed_data)
        elif self.format == 'html':
            report = self._generate_html(analysis_result, parsed_data)
        else:
            report = self._generate_text(analysis_result, parsed_data)
        
        # 如果指定了输出文件，写入文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def _generate_markdown(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成 Markdown 格式报告"""
        lines = []
        
        # 标题
        lines.append("# BDF 计算结果分析报告")
        lines.append("")
        lines.append(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 计算总结
        summary = analysis_result.get('summary', '')
        if summary:
            lines.append("## 计算总结")
            lines.append("")
            lines.append(summary)
            lines.append("")
        
        # 能量分析
        energy_analysis = analysis_result.get('energy_analysis', '')
        if energy_analysis:
            lines.append("## 能量分析")
            lines.append("")
            lines.append(energy_analysis)
            lines.append("")
        
        # 几何结构分析
        geometry_analysis = analysis_result.get('geometry_analysis', '')
        if geometry_analysis:
            lines.append("## 几何结构分析")
            lines.append("")
            lines.append(geometry_analysis)
            lines.append("")
        
        # 收敛性分析
        convergence_analysis = analysis_result.get('convergence_analysis', '')
        if convergence_analysis:
            lines.append("## 收敛性分析")
            lines.append("")
            lines.append(convergence_analysis)
            lines.append("")
        
        # 原始数据（如果提供）
        if parsed_data:
            lines.append("## 原始数据")
            lines.append("")
            
            energy = parsed_data.get('energy')
            if energy is not None:
                lines.append(f"- **总能量**：{energy:.10f} Hartree")
            
            scf_energy = parsed_data.get('scf_energy')
            if scf_energy is not None and scf_energy != energy:
                lines.append(f"- **SCF 能量**：{scf_energy:.10f} Hartree")
            
            converged = parsed_data.get('converged', False)
            lines.append(f"- **收敛状态**：{'已收敛' if converged else '未收敛'}")
            
            frequencies = parsed_data.get('frequencies', [])
            if frequencies:
                lines.append(f"- **振动频率数量**：{len(frequencies)}")
            
            lines.append("")
        
        # 建议
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            lines.append("## 专业建议")
            lines.append("")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # 警告
        warnings = analysis_result.get('warnings', [])
        if warnings:
            lines.append("## 警告信息")
            lines.append("")
            for i, warning in enumerate(warnings, 1):
                lines.append(f"{i}. {warning}")
            lines.append("")
        
        # 专家见解
        expert_insights = analysis_result.get('expert_insights', '')
        if expert_insights:
            lines.append("## 专家见解")
            lines.append("")
            lines.append(expert_insights)
            lines.append("")
        
        # 如果没有结构化内容，显示原始分析
        raw_analysis = analysis_result.get('raw_analysis', '')
        if raw_analysis and not (summary or energy_analysis or geometry_analysis):
            lines.append("## AI 分析结果")
            lines.append("")
            lines.append(raw_analysis)
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成 HTML 格式报告"""
        # 先生成 Markdown，然后转换为 HTML（简化版本）
        markdown = self._generate_markdown(analysis_result, parsed_data)
        
        # 简单的 Markdown 到 HTML 转换
        html_lines = []
        html_lines.append("<!DOCTYPE html>")
        html_lines.append("<html>")
        html_lines.append("<head>")
        html_lines.append('<meta charset="utf-8">')
        html_lines.append("<title>BDF 计算结果分析报告</title>")
        html_lines.append('<style>')
        html_lines.append('body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }')
        html_lines.append('h1 { color: #333; }')
        html_lines.append('h2 { color: #666; margin-top: 30px; }')
        html_lines.append('pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }')
        html_lines.append('</style>')
        html_lines.append("</head>")
        html_lines.append("<body>")
        
        # 简单的 Markdown 转换
        import re
        html_content = markdown
        
        # 标题转换
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        
        # 粗体
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        
        # 列表
        html_content = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html_content, flags=re.MULTILINE)
        
        # 段落
        paragraphs = html_content.split('\n\n')
        html_paragraphs = []
        for para in paragraphs:
            if para.strip() and not para.startswith('<'):
                html_paragraphs.append(f'<p>{para}</p>')
            else:
                html_paragraphs.append(para)
        
        html_lines.append('\n'.join(html_paragraphs))
        html_lines.append("</body>")
        html_lines.append("</html>")
        
        return "\n".join(html_lines)
    
    def _generate_text(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成纯文本格式报告"""
        # 先生成 Markdown，然后去除 Markdown 标记
        markdown = self._generate_markdown(analysis_result, parsed_data)
        
        # 简单的 Markdown 到文本转换
        import re
        
        # 移除标题标记
        text = re.sub(r'^#+\s+', '', markdown, flags=re.MULTILINE)
        
        # 移除粗体标记
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        
        # 移除代码块标记
        text = re.sub(r'```[\w]*\n', '', text)
        
        return text

