#!/usr/bin/env python3
"""
测试轨道占据信息解析功能
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis.report.report_generator import AnalysisReportGenerator

def test_occupation_extraction():
    """测试轨道占据信息提取"""
    
    # 测试用例：RHF/RKS计算
    test_content = """
[Final occupation pattern: ]

 Irreps:        Ag      B1g     B2g     B3g     Au      B1u     B2u     B3u 

 detailed occupation for iden/irep:      1   1
    1.00 1.00 1.00 1.00 1.00 1.00 0.00 0.00 0.00 0.00
    0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
    0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   2
    1.00 1.00 1.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
    0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   3
    1.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   4
    1.00 0.00 0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   5
    0.00 0.00 0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   6
    1.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   7
    1.00 1.00 1.00 1.00 0.00 0.00 0.00 0.00 0.00 0.00
    0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
 detailed occupation for iden/irep:      1   8
    1.00 1.00 1.00 1.00 1.00 0.00 0.00 0.00 0.00 0.00
    0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
    0.00 0.00 0.00 0.00
 Alpha       6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00
"""
    
    parser = BDFOutputParser()
    
    print("=" * 70)
    print("轨道占据信息提取测试")
    print("=" * 70)
    print()
    
    result = parser.extract_occupation_info(test_content)
    
    if result:
        print("✓ 成功提取轨道占据信息")
        print()
        print("提取结果：")
        print(f"  - 不可约表示: {result.get('irreps', [])}")
        print(f"  - Alpha占据数: {result.get('alpha_occupation', [])}")
        print(f"  - Beta占据数: {result.get('beta_occupation', [])}")
        print(f"  - Alpha电子总数: {result.get('total_alpha_electrons', 'N/A')}")
        print(f"  - Beta电子总数: {result.get('total_beta_electrons', 'N/A')}")
        print(f"  - 总电子数: {result.get('total_electrons', 'N/A')}")
        print(f"  - 是否为RHF/RKS: {result.get('is_rhf_rks', False)}")
        print(f"  - 基态波函数对称性: {result.get('ground_state_irrep', 'N/A')}")
        print()
        
        # 测试报告生成
        print("生成测试报告...")
        try:
            # 创建模拟的parsed_data
            parsed_data = {
                'properties': {
                    'occupation': result
                }
            }
            
            report_generator = AnalysisReportGenerator(format="markdown", language="zh")
            report = report_generator.generate(
                {'summary': '轨道占据信息测试'},
                parsed_data=parsed_data,
                output_file=str(project_root / "docs" / "dev" / "occupation_test_report.md")
            )
            print("  ✓ 报告生成成功")
            print(f"  报告文件: docs/dev/occupation_test_report.md")
        except Exception as e:
            print(f"  ✗ 报告生成失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ 未能提取轨道占据信息")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    test_occupation_extraction()
