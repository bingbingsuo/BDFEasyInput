#!/usr/bin/env python3
"""
测试test006.inp的不可约表示解析功能

由于test006.inp包含多个计算任务，我们需要测试解析器能否正确提取每个任务的不可约表示信息
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis.report.report_generator import AnalysisReportGenerator

def create_mock_output():
    """创建模拟的BDF输出内容，包含多个计算任务的不可约表示信息"""
    
    # 模拟test006.inp的输出，包含多个不同对称群的计算
    mock_output = """
gsym: D06H, noper=   24
 Exiting zgeomsort....
 Representation generated
  Point group name D(6H)   
  User set point group as D(6H)   
  Largest Abelian Subgroup D(2H)                       8
 Representation generated
 D|6|H|                    6
 Symmetry check OK

Total number of basis functions:     108     108

  Irrep :     A1G
  Norb  :     18
  Irrep :     A2G
  Norb  :     12
  Irrep :     E1G
  Norb  :     24
  Irrep :     E2G
  Norb  :     20
  Irrep :     A1U
  Norb  :     10
  Irrep :     A2U
  Norb  :     8
  Irrep :     E1U
  Norb  :     16

Final scf result
  E_tot =               -230.72165345
  E_ele =               -461.23456789
  E_nn  =                230.51291444
Congratulations! BDF normal termination

================================================================================
Next calculation: D(3H) symmetry
================================================================================

gsym: D06H, noper=   24
 Exiting zgeomsort....
 Representation generated
  Point group name D(6H)   
  User set point group as D(3H)   
  Largest Abelian Subgroup D(2H)                       8
 Representation generated
 D|3|H|                    3
 Symmetry check OK

Total number of basis functions:     108     108

  Irrep :     A1'
  Norb  :     20
  Irrep :     A2'
  Norb  :     15
  Irrep :     E'
  Norb  :     35
  Irrep :     A1''
  Norb  :     12
  Irrep :     A2''
  Norb  :     10
  Irrep :     E''
  Norb  :     16

Final scf result
  E_tot =               -230.72165345
  E_ele =               -461.23456789
  E_nn  =                230.51291444
Congratulations! BDF normal termination
"""
    return mock_output

def test_irrep_parsing():
    """测试不可约表示解析"""
    print("=" * 70)
    print("test006.inp 不可约表示解析测试")
    print("=" * 70)
    print()
    
    # 创建模拟输出
    mock_output = create_mock_output()
    
    # 保存到临时文件
    temp_file = project_root / "debug" / "test006_mock.out"
    temp_file.parent.mkdir(exist_ok=True)
    with open(temp_file, 'w') as f:
        f.write(mock_output)
    
    print(f"✓ 创建模拟输出文件: {temp_file}")
    print()
    
    # 解析
    print("1. 解析输出文件...")
    try:
        parser = BDFOutputParser()
        parsed_data = parser.parse(str(temp_file))
        print("   ✓ 解析成功")
        print()
        
        # 显示对称群信息
        symmetry = parsed_data.get('properties', {}).get('symmetry')
        if symmetry:
            print("2. 对称群信息:")
            print(f"   - 检测到的对称群: {symmetry.get('detected_group', 'N/A')}")
            print(f"   - 用户设定的对称群: {symmetry.get('user_set_group', 'N/A')}")
            print(f"   - 对称操作数: {symmetry.get('noper', 'N/A')}")
            print()
        
        # 显示不可约表示信息
        irreps = parsed_data.get('properties', {}).get('irreps')
        if irreps:
            print("3. 不可约表示信息:")
            print(f"   - 总基函数数: {irreps.get('total_basis_functions', 'N/A')}")
            print(f"   - 总轨道数: {irreps.get('total_orbitals', 'N/A')}")
            irrep_list = irreps.get('irreps', [])
            if irrep_list:
                print(f"   - 不可约表示数量: {len(irrep_list)}")
                print("   - 不可约表示分布:")
                for irrep_data in irrep_list:
                    irrep_name = irrep_data.get('irrep', '')
                    norb = irrep_data.get('norb', 0)
                    print(f"     * {irrep_name}: {norb} 个轨道")
            print()
        else:
            print("   ⚠️  未找到不可约表示信息")
            print()
        
        # 生成报告
        print("4. 生成分析报告...")
        try:
            report_generator = AnalysisReportGenerator(format="markdown", language="zh")
            report = report_generator.generate(
                {'summary': '测试报告'},
                parsed_data=parsed_data,
                output_file=str(project_root / "docs" / "dev" / "test006_irrep_test_report.md")
            )
            print("   ✓ 报告生成成功")
            print(f"   报告文件: docs/dev/test006_irrep_test_report.md")
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
    sys.exit(test_irrep_parsing())
