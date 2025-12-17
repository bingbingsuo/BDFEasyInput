#!/usr/bin/env python3
"""
执行 ch2o 计算并进行 AI 分析

此脚本将：
1. 运行 ch2o.inp 计算（包含隐式溶剂效应）
2. 解析输出结果
3. 使用 AI 进行分析
4. 生成分析报告
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput import load_config
from bdfeasyinput.execution import create_runner
from bdfeasyinput.analysis.parser import BDFOutputParser
from bdfeasyinput.analysis import QuantumChemistryAnalyzer
from bdfeasyinput.analysis.report import AnalysisReportGenerator
from bdfeasyinput.cli import get_ai_client_from_config


def main():
    """主函数"""
    print("=" * 70)
    print("ch2o 计算与分析（隐式溶剂效应）")
    print("=" * 70)
    print()
    
    # 1. 定位 ch2o.inp 文件
    input_file = str(project_root / "debug" / "ch2o.inp")
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"✗ 输入文件不存在: {input_file}")
        return 1
    
    print(f"✓ 输入文件: {input_file}")
    print(f"  文件大小: {input_path.stat().st_size} 字节")
    
    # 检查文件是否已经在 debug 目录中
    use_debug_dir = not str(input_path).startswith(str(project_root / "debug"))
    if not use_debug_dir:
        print("  注意: 文件已在 debug 目录中，将直接使用")
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
    
    # 3. 创建执行器并运行计算
    print("2. 创建执行器...")
    try:
        runner = create_runner(config=config)
        print(f"   ✓ 执行器创建成功: {type(runner).__name__}")
        print()
    except Exception as e:
        print(f"✗ 创建执行器失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 4. 运行计算
    print("3. 运行 BDF 计算...")
    print(f"   输入文件: {input_file}")
    print("   正在执行，请稍候...")
    print()
    
    try:
        result = runner.run(input_file, timeout=3600, use_debug_dir=use_debug_dir)
        
        print("   计算完成!")
        print(f"   状态: {result['status']}")
        print(f"   退出码: {result.get('exit_code', 'N/A')}")
        print(f"   执行时间: {result.get('execution_time', 0):.2f} 秒")
        print()
        
        output_file = result.get('output_file')
        error_file = result.get('error_file')
        
        # BDFAutotest 可能将输出文件放在输入文件所在目录
        # 检查多个可能的位置
        possible_output_files = []
        if output_file:
            possible_output_files.append(Path(output_file))
        # 检查输入文件所在目录
        input_dir = input_path.parent
        for ext in ['.log', '.out']:
            candidate = input_dir / input_path.with_suffix(ext).name
            if candidate.exists():
                possible_output_files.append(candidate)
        
        # 使用第一个存在的文件
        actual_output_file = None
        for candidate in possible_output_files:
            if candidate.exists():
                actual_output_file = str(candidate)
                size = candidate.stat().st_size
                print(f"   ✓ 输出文件: {actual_output_file}")
                print(f"     文件大小: {size} 字节")
                break
        
        if not actual_output_file:
            print(f"   ⚠️  输出文件不存在，尝试查找...")
            print(f"      已检查: {[str(p) for p in possible_output_files]}")
            # 即使找不到，也尝试继续，可能解析器能找到
            if output_file:
                actual_output_file = output_file
            else:
                actual_output_file = str(input_dir / input_path.with_suffix('.log').name)
        
        output_file = actual_output_file
        
        if error_file:
            error_path = Path(error_file)
            if error_path.exists():
                size = error_path.stat().st_size
                print(f"   {'✓' if size == 0 else '⚠️'} 错误文件: {error_file}")
                print(f"     文件大小: {size} 字节")
                if size > 0:
                    print("     注意: 错误文件不为空")
        print()
        
        if result['status'] != 'success':
            print("⚠️  计算未成功完成，但将继续解析输出文件...")
            print()
        
    except Exception as e:
        print(f"✗ 运行计算失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 5. 解析输出结果
    print("4. 解析输出结果...")
    if not output_file or not Path(output_file).exists():
        print("✗ 输出文件不存在，无法解析")
        return 1
    
    try:
        parser = BDFOutputParser()
        parsed_data = parser.parse(output_file)
        print("   ✓ 输出解析成功")
        print()
        
        # 显示解析结果摘要
        print("   解析结果摘要:")
        if parsed_data.get('energy') is not None:
            print(f"     - 总能量: {parsed_data['energy']:.10f} Hartree")
        if parsed_data.get('scf_energy') is not None:
            print(f"     - SCF 能量: {parsed_data['scf_energy']:.10f} Hartree")
        print(f"     - 收敛状态: {'已收敛' if parsed_data.get('converged') else '未收敛'}")
        
        # TDDFT 信息
        tddft = parsed_data.get('tddft', [])
        if tddft:
            print(f"     - TDDFT 计算块数量: {len(tddft)}")
            for idx, calc in enumerate(tddft, 1):
                itda = calc.get('itda')
                approx_method = calc.get('approximation_method', '未知')
                states_count = len(calc.get('states', []))
                print(f"       * 块 {idx}: ITDA={itda}, 方法={approx_method}, 激发态数={states_count}")
        
        print()
        
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 6. AI 分析
    print("5. AI 分析结果...")
    try:
        # 获取 AI 客户端 - 传递配置文件路径而不是配置字典
        config_file_path = project_root / "config" / "config.yaml"
        ai_client = get_ai_client_from_config(str(config_file_path) if config_file_path.exists() else None)
        
        # 创建分析器
        analyzer = QuantumChemistryAnalyzer(ai_client=ai_client)
        
        # Get language setting from config
        analysis_config = config.get('analysis', {})
        ai_config = analysis_config.get('ai', {})
        language = ai_config.get('language', 'zh')  # Default to Chinese
        
        print(f"   正在使用 AI 分析（语言: {language}），请稍候...")
        analysis_result = analyzer.analyze(
            output_file=output_file,
            input_file=input_file,
            error_file=error_file,
            task_type="scf",  # 可能是 SCF 计算，也可能是其他类型
            language=language
        )
        print("   ✓ AI 分析完成")
        print()
        
    except Exception as e:
        print(f"✗ AI 分析失败: {e}")
        import traceback
        traceback.print_exc()
        # 即使 AI 分析失败，也生成基础报告
        analysis_result = {}
    
    # 7. 生成报告
    print("6. 生成分析报告...")
    try:
        analysis_config = config.get('analysis', {})
        output_config = analysis_config.get('output', {})
        report_format = output_config.get('format', 'markdown')
        ai_config = analysis_config.get('ai', {})
        language = ai_config.get('language', 'zh')  # Get language from config
        
        report_generator = AnalysisReportGenerator(format=report_format, language=language)
        
        # 生成报告
        report = report_generator.generate(
            analysis_result=analysis_result,
            parsed_data=parsed_data,
            output_file=None  # 不写入文件，先显示
        )
        
        print("   ✓ 报告生成成功")
        print()
        
        # 保存报告到文件
        report_file = project_root / "ch2o_analysis_report.md"
        report_generator.generate(
            analysis_result=analysis_result,
            parsed_data=parsed_data,
            output_file=str(report_file)
        )
        print(f"   ✓ 报告已保存: {report_file}")
        print()
        
        # 显示报告
        print("=" * 70)
        print("分析报告")
        print("=" * 70)
        print()
        print(report)
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
