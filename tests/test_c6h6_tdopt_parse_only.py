#!/usr/bin/env python3
"""
仅解析c6h6_tdopt计算结果（跳过计算）

此脚本将：
1. 直接解析 c6h6_tdopt.out.tmp 输出文件
2. 使用 AI 进行分析
3. 生成分析报告（包含resp梯度信息）
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput import load_config
from bdfeasyinput.analysis.parser import BDFOutputParser
from bdfeasyinput.analysis import QuantumChemistryAnalyzer
from bdfeasyinput.analysis.report import AnalysisReportGenerator
from bdfeasyinput.cli import get_ai_client_from_config


def main():
    """主函数"""
    print("=" * 70)
    print("c6h6_tdopt 结果解析与分析（仅解析，跳过计算）")
    print("=" * 70)
    print()
    
    # 1. 定位输出文件
    output_file = str(project_root / "debug" / "c6h6_tdopt.out.tmp")
    output_path = Path(output_file)
    
    if not output_path.exists():
        print(f"✗ 输出文件不存在: {output_file}")
        return 1
    
    print(f"✓ 输出文件: {output_file}")
    print(f"  文件大小: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print()
    
    # 2. 加载配置
    print("1. 加载配置文件...")
    try:
        config = load_config()
        print("   ✓ 配置文件加载成功")
        print()
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 3. 解析输出结果
    print("2. 解析输出结果...")
    try:
        parser = BDFOutputParser()
        parsed_data = parser.parse(output_file)
        print("   ✓ 输出解析成功")
        print()
        
        # 显示解析结果摘要
        print("   解析结果摘要:")
        if parsed_data.get('energy') is not None:
            print(f"     - 总能量: {parsed_data['energy']:.10f} Hartree")
        print(f"     - 收敛状态: {'已收敛' if parsed_data.get('converged') else '未收敛'}")
        
        # 优化信息
        optimization = parsed_data.get('optimization', {})
        if optimization:
            opt_converged = optimization.get('converged', False)
            opt_iterations = optimization.get('iterations', 0)
            print(f"     - 结构优化: {'已收敛' if opt_converged else '未收敛'}, 迭代次数: {opt_iterations}")
        
        # TDDFT 信息
        tddft = parsed_data.get('tddft', [])
        if tddft:
            print(f"     - TDDFT 计算块数量: {len(tddft)}")
        
        # RESP梯度信息
        props = parsed_data.get('properties', {})
        resp_gradient = props.get('resp_gradient')
        if resp_gradient:
            primary_root = resp_gradient.get('primary_root')
            root_counts = resp_gradient.get('root_counts', {})
            total_calcs = resp_gradient.get('total_gradient_calculations', 0)
            print(f"     - RESP梯度计算:")
            print(f"       * 主要计算的激发态: Root {primary_root}")
            print(f"       * 总梯度计算次数: {total_calcs}")
            for root_num, count in sorted(root_counts.items()):
                print(f"       * Root {root_num}: {count} 次迭代")
        
        # 溶剂效应信息
        solvent = props.get('solvent', {})
        if solvent:
            print(f"     - 溶剂效应: {solvent.get('solvent', '未知')}, 模型: {solvent.get('method', '未知')}")
        
        print()
        
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 4. AI 分析（可选，可能耗时）
    print("3. AI 分析结果...")
    analysis_result = {}
    try:
        # 获取 AI 客户端
        config_file_path = project_root / "config" / "config.yaml"
        ai_client = get_ai_client_from_config(str(config_file_path) if config_file_path.exists() else None)
        
        # 创建分析器
        analyzer = QuantumChemistryAnalyzer(ai_client=ai_client)
        
        # Get language setting from config
        analysis_config = config.get('analysis', {})
        ai_config = analysis_config.get('ai', {})
        language = ai_config.get('language', 'zh')
        
        input_file = str(project_root / "debug" / "c6h6_tdopt.inp")
        print(f"   正在使用 AI 分析（语言: {language}），请稍候...")
        analysis_result = analyzer.analyze(
            output_file=output_file,
            input_file=input_file if Path(input_file).exists() else None,
            error_file=None,
            task_type="optimize",
            language=language
        )
        print("   ✓ AI 分析完成")
        print()
    except Exception as e:
        print(f"   ⚠️ AI 分析跳过: {e}")
        print()
    
    # 5. 生成报告
    print("4. 生成分析报告...")
    try:
        analysis_config = config.get('analysis', {})
        output_config = analysis_config.get('output', {})
        report_format = output_config.get('format', 'markdown')
        ai_config = analysis_config.get('ai', {})
        language = ai_config.get('language', 'zh')
        
        report_generator = AnalysisReportGenerator(format=report_format, language=language)
        
        # 生成报告
        report = report_generator.generate(
            analysis_result=analysis_result,
            parsed_data=parsed_data,
            output_file=None
        )
        
        print("   ✓ 报告生成成功")
        print()
        
        # 保存报告到文件
        report_file = project_root / "docs" / "dev" / "c6h6_tdopt_analysis_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_generator.generate(
            analysis_result=analysis_result,
            parsed_data=parsed_data,
            output_file=str(report_file)
        )
        print(f"   ✓ 报告已保存: {report_file}")
        print()
        
        # 显示报告的一部分（resp梯度信息部分）
        print("=" * 70)
        print("报告中的 RESP 梯度信息部分:")
        print("=" * 70)
        report_lines = report.split('\n')
        in_resp_section = False
        resp_lines = []
        for i, line in enumerate(report_lines):
            if 'RESP' in line and '梯度' in line or 'Gradient' in line:
                in_resp_section = True
            if in_resp_section:
                resp_lines.append(line)
                # 显示接下来20行
                if len(resp_lines) > 20 or (i < len(report_lines) - 1 and report_lines[i+1].startswith('##') and not report_lines[i+1].startswith('###')):
                    break
        
        if resp_lines:
            print('\n'.join(resp_lines))
        else:
            print("未找到RESP梯度信息部分")
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ 生成报告失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("✓ 所有步骤完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
