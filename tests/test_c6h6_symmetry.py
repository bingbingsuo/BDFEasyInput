#!/usr/bin/env python3
"""
测试C6H6分子不同对称群的SCF能量计算

创建多个计算任务，使用不同的对称群子群进行SCF能量计算
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.converter import BDFConverter
from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis.report.report_generator import AnalysisReportGenerator

def create_c6h6_input(group=None):
    """创建C6H6的YAML输入文件"""
    
    # C6H6 (苯) 的坐标 (D6h对称性)
    # 使用标准苯环结构
    c6h6_config = {
        "task": {
            "type": "energy",
            "description": f"C6H6 SCF energy calculation{' with group ' + group if group else ''}"
        },
        "molecule": {
            "name": "Benzene",
            "charge": 0,
            "multiplicity": 1,
            "coordinates": [
                # 苯环结构，D6h对称性
                "C  0.0000  1.3970  0.0000",
                "C  1.2112  0.6985  0.0000",
                "C  1.2112 -0.6985  0.0000",
                "C  0.0000 -1.3970  0.0000",
                "C -1.2112 -0.6985  0.0000",
                "C -1.2112  0.6985  0.0000",
                "H  0.0000  2.4810  0.0000",
                "H  2.1500  1.2405  0.0000",
                "H  2.1500 -1.2405  0.0000",
                "H  0.0000 -2.4810  0.0000",
                "H -2.1500 -1.2405  0.0000",
                "H -2.1500  1.2405  0.0000",
            ],
            "units": "angstrom"
        },
        "method": {
            "type": "hf",
            "basis": "sto-3g"  # 使用小基组以便快速测试
        },
        "settings": {
            "scf": {
                "convergence": 1e-6,
                "max_iterations": 100
            }
        }
    }
    
    if group:
        c6h6_config["settings"]["compass"] = {
            "symmetry": {
                "group": group
            }
        }
    
    return c6h6_config

def main():
    """主函数"""
    print("=" * 60)
    print("C6H6 对称群解析测试")
    print("=" * 60)
    print()
    
    # 测试不同的对称群
    test_groups = [
        None,  # 使用BDF自动检测的对称群
        "D(6H)",  # 使用检测到的对称群
        "D(2H)",  # 使用子群
        "C(2V)",  # 使用更小的子群
    ]
    
    converter = BDFConverter()
    parser = BDFOutputParser()
    
    results = []
    
    for group in test_groups:
        group_name = group if group else "Auto"
        print(f"处理对称群: {group_name}")
        
        # 创建YAML配置
        config = create_c6h6_input(group)
        
        # 转换为BDF输入
        try:
            bdf_input = converter.convert(config)
            print(f"  ✓ BDF输入生成成功")
            
            # 保存输入文件（用于参考）
            input_file = project_root / f"test_c6h6_{group_name.replace('(', '').replace(')', '').replace('/', '_')}.inp"
            with open(input_file, 'w') as f:
                f.write(bdf_input)
            print(f"  ✓ 输入文件已保存: {input_file.name}")
            
        except Exception as e:
            print(f"  ✗ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        print()
    
    print("=" * 60)
    print("注意：要测试完整的解析功能，需要运行BDF计算")
    print("生成的输入文件已保存，可以手动运行BDF进行计算")
    print("=" * 60)

if __name__ == "__main__":
    main()
