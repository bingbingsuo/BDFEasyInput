#!/usr/bin/env python3
"""
测试基组列表生成工具

创建一个测试用的基组名文件，测试生成功能
"""

import tempfile
import os
from pathlib import Path
from generate_basis_list import read_bdf_basis_file, generate_basis_mapping

def create_test_basis_file():
    """创建测试用的基组名文件"""
    test_content = """# BDF 基组名文件（测试）
# 格式: 基组名  相对论优化  有效核势
cc-pvdz    no    no
cc-pvtz    no    no
6-31G      no    no
6-31G*     no    no
def2-SVP   yes   no
def2-TZVP  yes   no
LANL2DZ    no    yes
SDD        no    yes
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.basisname') as f:
        f.write(test_content)
        return f.name

def test_generator():
    """测试生成器"""
    print("创建测试文件...")
    test_file = create_test_basis_file()
    
    try:
        print(f"测试文件: {test_file}")
        
        # 读取
        basis_list = read_bdf_basis_file(test_file)
        print(f"\n读取到 {len(basis_list)} 个基组:")
        for basis in basis_list:
            print(f"  - {basis['name']:15s} 相对论: {basis['relativistic']:3s}  ECP: {basis['ecp']:3s}")
        
        # 生成映射
        mapping = generate_basis_mapping(basis_list)
        print(f"\n生成的映射包含 {len(mapping['basis_sets'])} 个基组")
        
        print("\n✅ 测试通过")
        
    finally:
        # 清理
        os.unlink(test_file)
        print(f"\n清理测试文件: {test_file}")

if __name__ == "__main__":
    test_generator()

