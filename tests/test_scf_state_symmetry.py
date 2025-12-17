#!/usr/bin/env python3
"""
测试SCF State symmetry解析功能
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis.report.report_generator import AnalysisReportGenerator

def test_scf_state_symmetry():
    """测试SCF State symmetry提取"""
    
    # 测试用例
    test_content = """
 Beta        6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00

 SCF State symmetry : Ag

 [Orbital energies:]
"""
    
    parser = BDFOutputParser()
    
    print("=" * 70)
    print("SCF State symmetry 提取测试")
    print("=" * 70)
    print()
    
    result = parser.extract_scf_state_symmetry(test_content)
    
    if result:
        print("✓ 成功提取SCF State symmetry")
        print()
        print("提取结果：")
        print(f"  - 不可约表示: {result.get('irrep', 'N/A')}")
        print(f"  - 描述: {result.get('description', 'N/A')}")
        print()
        
        # 测试报告生成
        print("生成测试报告...")
        try:
            parsed_data = {
                'properties': {
                    'scf_state_symmetry': result
                }
            }
            
            report_generator = AnalysisReportGenerator(format="markdown", language="zh")
            report = report_generator.generate(
                {'summary': 'SCF State symmetry测试'},
                parsed_data=parsed_data,
                output_file=str(project_root / "docs" / "dev" / "scf_state_symmetry_test_report.md")
            )
            print("  ✓ 报告生成成功")
            print(f"  报告文件: docs/dev/scf_state_symmetry_test_report.md")
        except Exception as e:
            print(f"  ✗ 报告生成失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ 未能提取SCF State symmetry")
    
    print()
    print("=" * 70)
    
    # 测试实际文件
    print()
    print("=" * 70)
    print("测试实际输出文件: debug/c6h6.out")
    print("=" * 70)
    print()
    
    output_file = project_root / "debug" / "c6h6.out"
    if output_file.exists():
        try:
            parsed_data = parser.parse(str(output_file))
            scf_state_symmetry = parsed_data.get('properties', {}).get('scf_state_symmetry')
            if scf_state_symmetry:
                print("✓ 成功从实际文件提取SCF State symmetry")
                print(f"  - 不可约表示: {scf_state_symmetry.get('irrep', 'N/A')}")
                print()
                
                # 生成完整报告
                report_generator = AnalysisReportGenerator(format="markdown", language="zh")
                report = report_generator.generate(
                    {'summary': 'c6h6.out完整解析测试'},
                    parsed_data=parsed_data,
                    output_file=str(project_root / "docs" / "dev" / "c6h6_out_analysis_report.md")
                )
                print("✓ 完整报告生成成功")
                print(f"  报告文件: docs/dev/c6h6_out_analysis_report.md")
            else:
                print("⚠️  未找到SCF State symmetry信息")
        except Exception as e:
            print(f"✗ 解析失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️  输出文件不存在: {output_file}")

if __name__ == "__main__":
    test_scf_state_symmetry()
