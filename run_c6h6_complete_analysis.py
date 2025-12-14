#!/usr/bin/env python3
"""
执行 c6h6.inp 计算并进行完整的输出信息提取及AI分析

此脚本将：
1. 运行 c6h6.inp 计算（UHF计算）
2. 解析输出结果（包括所有新增的解析功能）
3. 使用 AI 进行分析
4. 生成完整的分析报告
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
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
    print("c6h6.inp 完整计算与分析（UHF计算 + 完整信息提取）")
    print("=" * 70)
    print()
    
    # 1. 定位输入文件
    input_file = str(project_root / "debug" / "c6h6.inp")
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"✗ 输入文件不存在: {input_file}")
        return 1
    
    print(f"✓ 输入文件: {input_file}")
    print(f"  文件大小: {input_path.stat().st_size} 字节")
    print()
    
    # 2. 检查输出文件
    output_file = str(project_root / "debug" / "c6h6.out")
    output_path = Path(output_file)
    
    # 检查是否需要重新计算
    need_rerun = False
    if not output_path.exists():
        print(f"⚠️  输出文件不存在: {output_file}")
        print("   需要运行BDF计算")
        need_rerun = True
    else:
        print(f"✓ 输出文件已存在: {output_file}")
        print(f"  文件大小: {output_path.stat().st_size} 字节")
        print("  将使用现有输出文件进行分析")
        print("  （如需重新计算，请删除输出文件后重新运行）")
        print()
    
    # 3. 如果需要，运行计算
    if need_rerun:
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
        
        print("3. 运行 BDF 计算...")
        print(f"   输入文件: {input_file}")
        print("   正在执行，请稍候...")
        print()
        
        try:
            result = runner.run(input_file, timeout=3600, use_debug_dir=True)
            
            print("   计算完成!")
            print(f"   状态: {result['status']}")
            print(f"   退出码: {result.get('exit_code', 'N/A')}")
            print(f"   执行时间: {result.get('execution_time', 0):.2f} 秒")
            print()
            
            if result.get('status') != 'success':
                print("   ✗ 计算失败，但将继续尝试解析现有输出文件")
                print()
            
            # 更新输出文件路径
            if result.get('output_file'):
                output_file = result.get('output_file')
                output_path = Path(output_file)
        
        except Exception as e:
            print(f"   ✗ 计算执行失败: {e}")
            print("   将尝试解析现有输出文件（如果存在）")
            print()
    
    # 4. 检查输出文件是否存在
    if not output_path.exists():
        print(f"✗ 输出文件不存在: {output_file}")
        print("   无法进行分析")
        return 1
    
    print(f"✓ 使用输出文件: {output_file}")
    print()
    
    # 5. 解析输出文件
    print("4. 解析输出文件...")
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
        
        # SCF方法信息
        scf_method = parsed_data.get('properties', {}).get('scf_method')
        if scf_method:
            print(f"     - SCF方法: {scf_method.get('method', 'N/A')}")
        
        # 对称群信息
        symmetry = parsed_data.get('properties', {}).get('symmetry')
        if symmetry:
            print(f"     - 检测到的对称群: {symmetry.get('detected_group', 'N/A')}")
            print(f"     - 用户设定的对称群: {symmetry.get('user_set_group', 'N/A')}")
        
        # 不可约表示信息
        irreps = parsed_data.get('properties', {}).get('irreps')
        if irreps:
            print(f"     - 不可约表示数目: {irreps.get('number_of_irreps', 'N/A')}")
            print(f"     - 总基函数数: {irreps.get('total_basis_functions', 'N/A')}")
            print(f"     - 总轨道数: {irreps.get('total_orbitals', 'N/A')}")
        
        # 轨道占据信息
        occupation = parsed_data.get('properties', {}).get('occupation')
        if occupation:
            print(f"     - Alpha电子总数: {occupation.get('total_alpha_electrons', 'N/A')}")
            print(f"     - Beta电子总数: {occupation.get('total_beta_electrons', 'N/A')}")
            print(f"     - 基态波函数对称性: {occupation.get('ground_state_irrep', 'N/A')}")
        
        # SCF State symmetry
        scf_state_symmetry = parsed_data.get('properties', {}).get('scf_state_symmetry')
        if scf_state_symmetry:
            print(f"     - SCF State symmetry: {scf_state_symmetry.get('irrep', 'N/A')}")
        
        print()
        
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 6. AI 分析
    print("5. AI 分析结果...")
    try:
        # 获取 AI 客户端
        config_file_path = project_root / "config" / "config.yaml"
        ai_client = get_ai_client_from_config(str(config_file_path))
        
        if not ai_client:
            print("   ⚠️  未配置AI客户端，跳过AI分析")
            print("   将只生成包含原始数据的报告")
            analysis_result = {}
        else:
            analyzer = QuantumChemistryAnalyzer(ai_client)
            # analyzer.analyze() 可以接受文件路径或已解析的数据
            # 如果传入的是字典，应该使用analyze_parsed_data方法（如果存在）
            # 或者直接传入文件路径
            try:
                # 尝试使用analyze方法，传入文件路径
                analysis_result = analyzer.analyze(output_file)
            except (TypeError, AttributeError):
                # 如果失败，尝试直接使用parsed_data
                try:
                    analysis_result = analyzer.analyze_parsed_data(parsed_data)
                except AttributeError:
                    # 如果方法不存在，创建空的分析结果
                    print("   ⚠️  AI分析器接口不兼容，跳过AI分析")
                    analysis_result = {}
            print("   ✓ AI 分析完成")
            print()
    except Exception as e:
        print(f"   ⚠️  AI 分析失败: {e}")
        import traceback
        traceback.print_exc()
        analysis_result = {}
        print()
    
    # 7. 生成报告
    print("6. 生成完整的分析报告...")
    try:
        report_generator = AnalysisReportGenerator(format="markdown", language="zh")
        report_file = str(project_root / "docs" / "dev" / "c6h6_complete_analysis_report.md")
        report = report_generator.generate(
            analysis_result,
            parsed_data=parsed_data,
            output_file=report_file
        )
        print("   ✓ 报告生成成功")
        print(f"   报告文件: docs/dev/c6h6_complete_analysis_report.md")
        print()
    except Exception as e:
        print(f"   ✗ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    print()
    print("报告包含以下信息：")
    print("  - 计算总结（AI分析）")
    print("  - 能量分析")
    print("  - 几何结构")
    print("  - 对称群信息")
    print("  - 不可约表示信息（包括数目、分布）")
    print("  - 分子轨道占据信息")
    print("  - SCF State Symmetry信息")
    print("  - SCF方法类型")
    print("  - 其他性质（HOMO-LUMO、偶极矩等）")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
