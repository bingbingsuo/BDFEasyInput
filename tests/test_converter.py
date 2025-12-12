#!/usr/bin/env python3
"""
测试转换器：生成水分子 SCF 单点能计算的 BDF 输入文件
"""

import sys
from pathlib import Path
from bdfeasyinput import BDFConverter

def main():
    """生成测试文件并评估效果"""
    
    converter = BDFConverter()
    
    # 测试文件列表
    test_files = [
        'examples/h2o_rhf.yaml',
        'examples/h2o_pbe0.yaml',
        'examples/h2o_b3lyp.yaml',
        'examples/h2o_frequency.yaml',  # Frequency calculation
        'examples/ch3cl_frequency.yaml',  # Frequency calculation (CH3Cl)
    ]
    
    print("=" * 60)
    print("BDFEasyInput 转换器测试")
    print("=" * 60)
    print()
    
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    for yaml_file in test_files:
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            print(f"❌ 文件不存在: {yaml_file}")
            continue
        
        print(f"📄 处理文件: {yaml_file}")
        
        # 生成输出文件名（确保有 .inp 扩展名）
        stem = yaml_path.stem.replace('.yaml', '').replace('.yml', '')
        output_file = output_dir / f"{stem}.inp"
        
        try:
            # 转换
            result_path = converter.convert_file(str(yaml_path), str(output_file))
            print(f"✅ 成功生成: {result_path}")
            
            # 显示前几行预览
            with open(result_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                preview_lines = lines[:15]  # 前15行
                print("   预览:")
                for line in preview_lines:
                    print(f"   {line.rstrip()}")
                if len(lines) > 15:
                    print(f"   ... (共 {len(lines)} 行)")
            
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()

