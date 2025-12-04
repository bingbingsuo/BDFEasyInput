#!/usr/bin/env python3
"""
查询 BDF 基组信息

从生成的基组列表中查询基组信息
"""

import sys
import yaml
from pathlib import Path

def load_basis_list():
    """加载基组列表"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    basis_file = project_root / "research" / "mapping_tables" / "bdf_basis_list.yaml"
    
    with open(basis_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_basis_name(name: str) -> str:
    """标准化基组名称（用于查找）"""
    return name.lower().replace("-", "_").replace("*", "_star")

def find_basis(basis_name: str, basis_data: dict) -> dict:
    """查找基组信息"""
    normalized = normalize_basis_name(basis_name)
    basis_sets = basis_data.get("basis_sets", {})
    
    # 精确匹配
    if normalized in basis_sets:
        return basis_sets[normalized]
    
    # 大小写不敏感匹配
    for key, value in basis_sets.items():
        if key.lower() == normalized:
            return value
    
    # 模糊匹配（包含）
    matches = []
    for key, value in basis_sets.items():
        if normalized in key or key in normalized:
            matches.append((key, value))
    
    return matches if matches else None

def main():
    if len(sys.argv) < 2:
        print("用法: python query_basis.py <基组名>")
        print("示例: python query_basis.py cc-pvdz")
        sys.exit(1)
    
    basis_name = sys.argv[1]
    
    # 加载数据
    try:
        basis_data = load_basis_list()
    except FileNotFoundError:
        print("错误：未找到基组列表文件")
        print("请先运行: python generate_basis_list.py")
        sys.exit(1)
    
    # 查找
    result = find_basis(basis_name, basis_data)
    
    if result is None:
        print(f"未找到基组: {basis_name}")
        sys.exit(1)
    
    if isinstance(result, list):
        print(f"找到 {len(result)} 个匹配的基组:")
        for key, value in result:
            print(f"\n{key}:")
            print(f"  BDF 名称: {value['bdf_name']}")
            print(f"  相对论优化: {value['relativistic']}")
            print(f"  包含 ECP: {value['ecp']}")
    else:
        print(f"基组信息: {basis_name}")
        print(f"  BDF 名称: {result['bdf_name']}")
        print(f"  相对论优化: {result['relativistic']}")
        print(f"  包含 ECP: {result['ecp']}")
        print(f"  描述: {result['description']}")

if __name__ == "__main__":
    main()

