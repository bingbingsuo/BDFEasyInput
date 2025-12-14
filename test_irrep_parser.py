#!/usr/bin/env python3
"""
测试不可约表示解析功能
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

def test_irrep_extraction():
    """测试不可约表示信息提取"""
    
    # 测试用例1：标准格式
    test_content1 = """
Total number of basis functions:      22      22

  Irrep :     A
  Norb  :     22
"""
    
    # 测试用例2：多个不可约表示
    test_content2 = """
Total number of basis functions:      44      44

  Irrep :     A1
  Norb  :     15
  Irrep :     B1
  Norb  :     12
  Irrep :     B2
  Norb  :     10
  Irrep :     A2
  Norb  :     7
"""
    
    # 测试用例3：表格格式
    test_content3 = """
Total number of basis functions:      30      30

  Irrep    Norb
    A       15
    B1      10
    B2       5
"""
    
    parser = BDFOutputParser()
    
    print("=" * 60)
    print("不可约表示信息提取测试")
    print("=" * 60)
    print()
    
    test_cases = [
        ("测试1: 单个不可约表示", test_content1),
        ("测试2: 多个不可约表示", test_content2),
        ("测试3: 表格格式", test_content3),
    ]
    
    for name, content in test_cases:
        print(f"{name}:")
        result = parser.extract_irrep_info(content)
        if result:
            print("  ✓ 提取成功")
            print(f"  - 总基函数数: {result.get('total_basis_functions', 'N/A')}")
            if 'irreps' in result:
                print(f"  - 不可约表示数量: {len(result['irreps'])}")
                for irrep in result['irreps']:
                    print(f"    * {irrep.get('irrep')}: {irrep.get('norb')} 个轨道")
            print(f"  - 总轨道数: {result.get('total_orbitals', 'N/A')}")
        else:
            print("  ✗ 提取失败")
        print()

if __name__ == "__main__":
    test_irrep_extraction()
