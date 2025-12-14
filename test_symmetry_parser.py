#!/usr/bin/env python3
"""
测试对称群解析功能

创建一个简单的测试，验证解析器能否正确提取对称群信息
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser

def test_symmetry_extraction():
    """测试对称群信息提取"""
    
    # 创建一个模拟的BDF输出内容，包含对称群信息
    test_content = """
gsym: D06H, noper=   24
 Exiting zgeomsort....
 Representation generated
  Point group name D(6H)   
  User set point group as D(6H)   
  Largest Abelian Subgroup D(2H)                       8
 Representation generated
 D|6|H|                    6
 Symmetry check OK
"""
    
    parser = BDFOutputParser()
    symmetry_info = parser.extract_symmetry_info(test_content)
    
    print("=" * 60)
    print("对称群信息提取测试")
    print("=" * 60)
    print()
    
    if symmetry_info:
        print("✓ 成功提取对称群信息")
        print()
        print("提取结果：")
        for key, value in symmetry_info.items():
            print(f"  - {key}: {value}")
    else:
        print("✗ 未能提取对称群信息")
    
    print()
    print("=" * 60)
    
    # 测试不同的格式
    test_cases = [
        {
            "name": "测试1: 标准格式",
            "content": """
gsym: D06H, noper=   24
 Point group name D(6H)   
 User set point group as D(6H)   
 Largest Abelian Subgroup D(2H)                       8
 Symmetry check OK
"""
        },
        {
            "name": "测试2: 只有检测到的群",
            "content": """
gsym: C2V, noper=   4
 Point group name C(2V)   
 Symmetry check OK
"""
        },
        {
            "name": "测试3: 用户设定子群",
            "content": """
gsym: D06H, noper=   24
 Point group name D(6H)   
 User set point group as D(2H)   
 Largest Abelian Subgroup D(2H)                       8
 Symmetry check OK
"""
        },
    ]
    
    print()
    print("=" * 60)
    print("多个测试用例")
    print("=" * 60)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{test_case['name']}:")
        result = parser.extract_symmetry_info(test_case['content'])
        if result:
            print("  ✓ 提取成功")
            for key, value in result.items():
                print(f"    - {key}: {value}")
        else:
            print("  ✗ 提取失败")
        print()

if __name__ == "__main__":
    test_symmetry_extraction()
