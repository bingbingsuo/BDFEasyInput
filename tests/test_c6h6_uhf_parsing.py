#!/usr/bin/env python3
"""
测试c6h6.inp (UHF计算) 的解析功能

验证：
1. SCF方法提取（应该是UHF）
2. 轨道占据信息提取（应该包含alpha和beta占据数）
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser
from bdfeasyinput.analysis.report.report_generator import AnalysisReportGenerator

def main():
    """主函数"""
    print("=" * 70)
    print("c6h6.inp (UHF计算) 解析测试")
    print("=" * 70)
    print()
    
    # 1. 定位输出文件
    output_file = str(project_root / "debug" / "c6h6.log")
    output_path = Path(output_file)
    
    if not output_path.exists():
        print(f"✗ 输出文件不存在: {output_file}")
        print("   需要先运行BDF计算")
        return 1
    
    print(f"✓ 输出文件: {output_file}")
    print(f"  文件大小: {output_path.stat().st_size} 字节")
    print()
    
    # 2. 解析输出文件
    print("1. 解析输出文件...")
    try:
        parser = BDFOutputParser()
        parsed_data = parser.parse(output_file)
        print("   ✓ 解析成功")
        print()
        
        # 显示解析结果摘要
        print("2. 解析结果摘要:")
        if parsed_data.get('energy') is not None:
            print(f"   - 总能量: {parsed_data['energy']:.10f} Hartree")
        if parsed_data.get('scf_energy') is not None:
            print(f"   - SCF 能量: {parsed_data['scf_energy']:.10f} Hartree")
        print(f"   - 收敛状态: {'已收敛' if parsed_data.get('converged') else '未收敛'}")
        print()
        
        # SCF方法信息
        scf_method = parsed_data.get('properties', {}).get('scf_method')
        if scf_method:
            print("3. SCF方法信息:")
            method = scf_method.get('method', 'N/A')
            print(f"   - 方法类型: {method}")
            print(f"   - 是否为限制性: {scf_method.get('is_restricted', False)}")
            print(f"   - 是否为非限制性: {scf_method.get('is_unrestricted', False)}")
            print(f"   - 是否为DFT: {scf_method.get('is_dft', False)}")
            print(f"   - 是否为HF: {scf_method.get('is_hf', False)}")
            print()
        else:
            print("   ⚠️  未找到SCF方法信息")
            print()
        
        # 对称群信息
        symmetry = parsed_data.get('properties', {}).get('symmetry')
        if symmetry:
            print("4. 对称群信息:")
            print(f"   - 检测到的对称群: {symmetry.get('detected_group', 'N/A')}")
            print(f"   - 用户设定的对称群: {symmetry.get('user_set_group', 'N/A')}")
            print()
        
        # 轨道占据信息
        occupation = parsed_data.get('properties', {}).get('occupation')
        if occupation:
            print("5. 轨道占据信息:")
            irreps = occupation.get('irreps', [])
            alpha_occ = occupation.get('alpha_occupation', [])
            beta_occ = occupation.get('beta_occupation', [])
            total_alpha = occupation.get('total_alpha_electrons')
            total_beta = occupation.get('total_beta_electrons')
            total_electrons = occupation.get('total_electrons')
            ground_state_irrep = occupation.get('ground_state_irrep')
            is_restricted = occupation.get('is_restricted', False)
            
            print(f"   - 不可约表示数量: {len(irreps)}")
            if irreps:
                print(f"   - 不可约表示: {', '.join(irreps[:5])}{'...' if len(irreps) > 5 else ''}")
            print(f"   - Alpha占据数数量: {len(alpha_occ)}")
            if alpha_occ:
                print(f"   - Alpha占据数: {alpha_occ[:5]}{'...' if len(alpha_occ) > 5 else ''}")
            print(f"   - Beta占据数数量: {len(beta_occ)}")
            if beta_occ:
                print(f"   - Beta占据数: {beta_occ[:5]}{'...' if len(beta_occ) > 5 else ''}")
            print(f"   - Alpha电子总数: {total_alpha if total_alpha is not None else 'N/A'}")
            print(f"   - Beta电子总数: {total_beta if total_beta is not None else 'N/A'}")
            print(f"   - 总电子数: {total_electrons if total_electrons is not None else 'N/A'}")
            print(f"   - 基态波函数对称性: {ground_state_irrep if ground_state_irrep else 'N/A'}")
            print(f"   - 是否为限制性方法: {is_restricted}")
            
            # 验证UHF计算
            if scf_method and scf_method.get('method') == 'UHF':
                if beta_occ and len(beta_occ) > 0:
                    # 检查alpha和beta是否不同（UHF应该不同）
                    if alpha_occ and beta_occ and len(alpha_occ) == len(beta_occ):
                        are_different = any(abs(a - b) > 0.01 for a, b in zip(alpha_occ, beta_occ))
                        if are_different:
                            print(f"   ✓ UHF验证: Alpha和Beta占据数不同（符合预期）")
                        else:
                            print(f"   ⚠️  UHF验证: Alpha和Beta占据数相同（可能有问题）")
                    else:
                        print(f"   ✓ UHF验证: 成功提取Alpha和Beta占据数")
                else:
                    print(f"   ✗ UHF验证失败: 未找到Beta占据数")
            
            print()
        else:
            print("   ⚠️  未找到轨道占据信息")
            print()
        
    except Exception as e:
        print(f"   ✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 3. 生成报告
    print("6. 生成分析报告...")
    try:
        report_generator = AnalysisReportGenerator(format="markdown", language="zh")
        report = report_generator.generate(
            {'summary': 'c6h6 UHF计算分析'},
            parsed_data=parsed_data,
            output_file=str(project_root / "docs" / "dev" / "c6h6_uhf_analysis_report.md")
        )
        print("   ✓ 报告生成成功")
        print(f"   报告文件: docs/dev/c6h6_uhf_analysis_report.md")
        print()
    except Exception as e:
        print(f"   ✗ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("=" * 70)
    print("测试完成！")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
