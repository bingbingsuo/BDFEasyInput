#!/usr/bin/env python3
"""
BDF 基组列表生成工具

从 BDF 基组名文件中读取基组信息，生成基组列表 YAML 文件。

使用方法：
    python generate_basis_list.py [basisname_file] [output_file]

参数：
    basisname_file: BDF 基组名文件路径（默认：~/bdf/bdf-pkg-full/basis_library/basisname）
    output_file: 输出的 YAML 文件路径（默认：../mapping_tables/bdf_basis_list.yaml）
"""

import sys
from pathlib import Path
from typing import List, Dict
import yaml


def parse_basisname_file(file_path: str) -> List[Dict]:
    """
    解析 BDF 基组名文件
    
    文件格式：
        第一列：基组名
        第二列：相对论优化标志（yes/no）
        第三列：有效核势标志（yes/no）
    
    Args:
        file_path: 基组名文件路径
    
    Returns:
        基组信息列表
    """
    basis_list = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                # 跳过注释行（以 # 开头或包含注释标记如 "a.e. rel."）
                if line.startswith('#') or 'a.e. rel.' in line or 'ecp' in line.lower() and 'the maximum' in line.lower():
                continue
            
                # 解析行（使用空格分隔，可能有多个空格）
                # 格式：基组名    相对论标志    有效核势标志
                # 示例：STO-3G                          no          no
                parts = [p for p in line.split() if p]  # 移除空字符串
            if len(parts) < 1:
                continue
            
            basis_name = parts[0]
                
                # 解析相对论和 ECP 标志
                # 第二列是相对论标志，第三列是 ECP 标志
                relativistic = False
                ecp = False
                
                if len(parts) >= 2:
                    rel_flag = parts[1].lower()
                    if rel_flag in ['yes', 'no']:
                        relativistic = (rel_flag == 'yes')
                
                if len(parts) >= 3:
                    ecp_flag = parts[2].lower()
                    if ecp_flag in ['yes', 'no']:
                        ecp = (ecp_flag == 'yes')
                
                basis_info = {
                    'bdf_name': basis_name,
                    'relativistic': relativistic,
                    'ecp': ecp,
                    'source': 'bdf_basis_library'
                }
                
                basis_list.append(basis_info)
                
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：解析文件时出错 - {e}")
        sys.exit(1)
    
    return basis_list


def generate_yaml_mapping(basis_list: List[Dict]) -> Dict:
    """
    生成 YAML 映射结构
    
    Args:
        basis_list: 基组信息列表
    
    Returns:
        YAML 字典结构
    """
    mapping = {
        'version': '1.0',
        'source': 'BDF basis library',
        'total_basis_sets': len(basis_list),
        'basis_sets': {}
    }
    
    for basis in basis_list:
        bdf_name = basis['bdf_name']
        
        # 生成标准名称（用于 YAML 中的键）
        # 将 BDF 名称转换为小写，替换特殊字符
        standard_name = bdf_name.lower().replace('*', 'star').replace('-', '_')
        
        mapping['basis_sets'][standard_name] = {
            'bdf_name': bdf_name,
            'relativistic': basis['relativistic'],
            'ecp': basis['ecp'],
            'aliases': [bdf_name],  # 可以添加别名
            'notes': []
        }
        
        # 添加注释
        if basis['relativistic']:
            mapping['basis_sets'][standard_name]['notes'].append('相对论优化基组')
        if basis['ecp']:
            mapping['basis_sets'][standard_name]['notes'].append('包含有效核势')
    
    return mapping


def main():
    """主函数"""
    # 默认文件路径
    default_basisname_file = Path.home() / 'bdf' / 'bdf-pkg-full' / 'basis_library' / 'basisname'
    default_output_file = Path(__file__).parent.parent / 'mapping_tables' / 'bdf_basis_list.yaml'
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        basisname_file = sys.argv[1]
    else:
        basisname_file = str(default_basisname_file)
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = str(default_output_file)
    
    print(f"读取基组名文件: {basisname_file}")
    print(f"输出文件: {output_file}")
    
    # 检查输入文件是否存在
    if not Path(basisname_file).exists():
        print(f"警告：基组名文件不存在: {basisname_file}")
        print("请确保 BDF 已安装，或提供正确的文件路径")
        sys.exit(1)
    
    # 解析基组名文件
    print("正在解析基组名文件...")
    basis_list = parse_basisname_file(basisname_file)
    print(f"找到 {len(basis_list)} 个基组")
    
    # 生成映射
    print("正在生成映射...")
    mapping = generate_yaml_mapping(basis_list)
    
    # 写入 YAML 文件
    print(f"正在写入 {output_file}...")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(mapping, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"✅ 成功生成基组列表，共 {len(basis_list)} 个基组")
    print(f"   输出文件: {output_file}")
    
    # 统计信息
    relativistic_count = sum(1 for b in basis_list if b['relativistic'])
    ecp_count = sum(1 for b in basis_list if b['ecp'])
    
    print(f"\n统计信息:")
    print(f"  - 总基组数: {len(basis_list)}")
    print(f"  - 相对论优化基组: {relativistic_count}")
    print(f"  - 包含 ECP 的基组: {ecp_count}")


if __name__ == '__main__':
    main()
