#!/usr/bin/env python3
"""
测试新格式的不可约表示信息解析
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

def test_new_format():
    """测试新格式的不可约表示信息提取"""
    
    # 新格式测试用例
    test_content = """
         Symmetry adapted orbital                   

  Total number of basis functions:     114     114

  Number of irreps:   8
  Irrep :   Ag        B1g       B2g       B3g       Au        B1u       B2u       B3u     
  Norb  :     24        18         9         6         6         9        18        24
"""
    
    parser = BDFOutputParser()
    
    print("=" * 70)
    print("新格式不可约表示信息提取测试")
    print("=" * 70)
    print()
    
    result = parser.extract_irrep_info(test_content)
    
    if result:
        print("✓ 成功提取不可约表示信息")
        print()
        print("提取结果：")
        print(f"  - 总基函数数: {result.get('total_basis_functions', 'N/A')}")
        print(f"  - 不可约表示数目: {result.get('number_of_irreps', 'N/A')}")
        print(f"  - 总轨道数: {result.get('total_orbitals', 'N/A')}")
        irrep_list = result.get('irreps', [])
        if irrep_list:
            print(f"  - 不可约表示数量: {len(irrep_list)}")
            print("  - 不可约表示分布:")
            for irrep_data in irrep_list:
                irrep_name = irrep_data.get('irrep', '')
                norb = irrep_data.get('norb', 0)
                print(f"    * {irrep_name}: {norb} 个轨道")
            
            # 验证
            expected_irreps = ['Ag', 'B1g', 'B2g', 'B3g', 'Au', 'B1u', 'B2u', 'B3u']
            expected_norbs = [24, 18, 9, 6, 6, 9, 18, 24]
            
            print()
            print("验证:")
            if len(irrep_list) == len(expected_irreps):
                all_match = True
                for i, (irrep_data, exp_irrep, exp_norb) in enumerate(zip(irrep_list, expected_irreps, expected_norbs)):
                    actual_irrep = irrep_data.get('irrep', '')
                    actual_norb = irrep_data.get('norb', 0)
                    if actual_irrep == exp_irrep and actual_norb == exp_norb:
                        print(f"  ✓ {actual_irrep}: {actual_norb} (正确)")
                    else:
                        print(f"  ✗ {actual_irrep}: {actual_norb} (期望: {exp_irrep}: {exp_norb})")
                        all_match = False
                if all_match:
                    print()
                    print("  ✓ 所有不可约表示和轨道数都正确匹配！")
            else:
                print(f"  ✗ 不可约表示数量不匹配: 期望{len(expected_irreps)}，实际{len(irrep_list)}")
        else:
            print("  ✗ 未找到不可约表示列表")
    else:
        print("✗ 未能提取不可约表示信息")
    
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
            irreps = parsed_data.get('properties', {}).get('irreps')
            if irreps:
                print("✓ 成功从实际文件提取不可约表示信息")
                print(f"  - 总基函数数: {irreps.get('total_basis_functions', 'N/A')}")
                print(f"  - 不可约表示数目: {irreps.get('number_of_irreps', 'N/A')}")
                print(f"  - 总轨道数: {irreps.get('total_orbitals', 'N/A')}")
                irrep_list = irreps.get('irreps', [])
                if irrep_list:
                    print(f"  - 不可约表示数量: {len(irrep_list)}")
                    print("  - 前5个不可约表示:")
                    for irrep_data in irrep_list[:5]:
                        irrep_name = irrep_data.get('irrep', '')
                        norb = irrep_data.get('norb', 0)
                        print(f"    * {irrep_name}: {norb} 个轨道")
            else:
                print("⚠️  未找到不可约表示信息")
        except Exception as e:
            print(f"✗ 解析失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️  输出文件不存在: {output_file}")

if __name__ == "__main__":
    test_new_format()
