#!/usr/bin/env python3
"""
测试c6h6.inp (UHF计算) 的解析功能
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis.report.report_generator import AnalysisReportGenerator

def test_c6h6_uhf():
    """测试c6h6.inp的UHF计算解析"""
    
    print("=" * 70)
    print("c6h6.inp (UHF计算) 解析测试")
    print("=" * 70)
    print()
    
    # 检查输入文件
    input_file = project_root / "debug" / "c6h6.inp"
    if not input_file.exists():
        print(f"✗ 输入文件不存在: {input_file}")
        return 1
    
    print(f"✓ 输入文件: {input_file}")
    print()
    
    # 检查输出文件
    output_file = project_root / "debug" / "c6h6.out"
    if not output_file.exists():
        print(f"⚠️  输出文件不存在: {output_file}")
        print("   需要先运行BDF计算")
        print()
        print("   运行命令:")
        print(f"   bdf {input_file} > {output_file}")
        print()
        return 1
    
    print(f"✓ 输出文件: {output_file}")
    print(f"  文件大小: {output_file.stat().st_size} 字节")
    print()
    
    # 解析输出文件
    print("1. 解析输出文件...")
    try:
        parser = BDFOutputParser()
        parsed_data = parser.parse(str(output_file))
        print("   ✓ 解析成功")
        print()
        
        # 显示SCF方法信息
        scf_method = parsed_data.get('properties', {}).get('scf_method')
        if scf_method:
            print("2. SCF方法信息:")
            print(f"   - 方法类型: {scf_method.get('method', 'N/A')}")
            print(f"   - 限制性方法: {scf_method.get('is_restricted', False)}")
            print(f"   - 非限制性方法: {scf_method.get('is_unrestricted', False)}")
            print(f"   - DFT方法: {scf_method.get('is_dft', False)}")
            print(f"   - HF方法: {scf_method.get('is_hf', False)}")
            print()
        
        # 显示轨道占据信息
        occupation = parsed_data.get('properties', {}).get('occupation')
        if occupation:
            print("3. 轨道占据信息:")
            print(f"   - 不可约表示: {occupation.get('irreps', [])}")
            print(f"   - Alpha占据数: {occupation.get('alpha_occupation', [])}")
            print(f"   - Beta占据数: {occupation.get('beta_occupation', [])}")
            print(f"   - Alpha电子总数: {occupation.get('total_alpha_electrons', 'N/A')}")
            print(f"   - Beta电子总数: {occupation.get('total_beta_electrons', 'N/A')}")
            print(f"   - 总电子数: {occupation.get('total_electrons', 'N/A')}")
            print(f"   - 限制性方法: {occupation.get('is_restricted', False)}")
            print(f"   - 基态波函数对称性: {occupation.get('ground_state_irrep', 'N/A')}")
            if 'warning' in occupation:
                print(f"   - 警告: {occupation['warning']}")
            print()
        else:
            print("   ⚠️  未找到轨道占据信息")
            print()
        
        # 显示能量信息
        print("4. 能量信息:")
        if parsed_data.get('energy') is not None:
            print(f"   - 总能量: {parsed_data['energy']:.10f} Hartree")
        if parsed_data.get('scf_energy') is not None:
            print(f"   - SCF能量: {parsed_data['scf_energy']:.10f} Hartree")
        print()
        
        # 生成报告
        print("5. 生成分析报告...")
        try:
            report_generator = AnalysisReportGenerator(format="markdown", language="zh")
            report = report_generator.generate(
                {'summary': 'c6h6 UHF计算分析'},
                parsed_data=parsed_data,
                output_file=str(project_root / "docs" / "dev" / "c6h6_uhf_analysis_report.md")
            )
            print("   ✓ 报告生成成功")
            print(f"   报告文件: docs/dev/c6h6_uhf_analysis_report.md")
            print()
        except Exception as e:
            print(f"   ✗ 报告生成失败: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"   ✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("=" * 70)
    print("测试完成！")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(test_c6h6_uhf())
