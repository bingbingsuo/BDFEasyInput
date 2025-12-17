#!/usr/bin/env python3
"""
运行 test006.inp 计算并进行分析

test006.inp 包含多个C6H6分子的SCF能量计算，使用不同的对称群
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput import load_config
from bdfeasyinput.execution import create_runner
from bdfeasyinput.analysis.parser import BDFOutputParser
from bdfeasyinput.analysis import QuantumChemistryAnalyzer
from bdfeasyinput.analysis.report import AnalysisReportGenerator
from bdfeasyinput.cli import get_ai_client_from_config


def main():
    """主函数"""
    print("=" * 70)
    print("test006.inp 计算与分析（C6H6 不同对称群的SCF能量计算）")
    print("=" * 70)
    print()
    
    # 1. 定位 test006.inp 文件
    input_file = str(project_root / "debug" / "test006.inp")
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"✗ 输入文件不存在: {input_file}")
        return 1
    
    print(f"✓ 输入文件: {input_file}")
    print(f"  文件大小: {input_path.stat().st_size} 字节")
    print()
    
    # 2. 检查输出文件
    output_file = str(project_root / "debug" / "test006.out")
    output_path = Path(output_file)
    
    if not output_path.exists():
        print(f"⚠️  输出文件不存在: {output_file}")
        print("   需要先运行BDF计算")
        print()
        print("   运行命令:")
        print(f"   bdf {input_file} > {output_file}")
        print()
        return 1
    
    print(f"✓ 输出文件: {output_file}")
    print(f"  文件大小: {output_path.stat().st_size} 字节")
    print()
    
    # 3. 解析输出文件
    print("3. 解析输出文件...")
    try:
        parser = BDFOutputParser()
        parsed_data = parser.parse(output_file)
        print("   ✓ 输出解析成功")
        print()
        
        # 显示解析结果摘要
        print("   解析结果摘要:")
        if parsed_data.get('energy') is not None:
            print(f"     - 总能量: {parsed_data['energy']:.10f} Hartree")
        if parsed_data.get('scf_energy') is not None:
            print(f"     - SCF 能量: {parsed_data['scf_energy']:.10f} Hartree")
        print(f"     - 收敛状态: {'已收敛' if parsed_data.get('converged') else '未收敛'}")
        
        # 对称群信息
        symmetry = parsed_data.get('properties', {}).get('symmetry')
        if symmetry:
            print(f"     - 检测到的对称群: {symmetry.get('detected_group', 'N/A')}")
            print(f"     - 用户设定的对称群: {symmetry.get('user_set_group', 'N/A')}")
        
        # 不可约表示信息
        irreps = parsed_data.get('properties', {}).get('irreps')
        if irreps:
            print(f"     - 总基函数数: {irreps.get('total_basis_functions', 'N/A')}")
            print(f"     - 总轨道数: {irreps.get('total_orbitals', 'N/A')}")
            irrep_list = irreps.get('irreps', [])
            if irrep_list:
                print(f"     - 不可约表示数量: {len(irrep_list)}")
                for irrep_data in irrep_list[:5]:  # 只显示前5个
                    print(f"       * {irrep_data.get('irrep')}: {irrep_data.get('norb')} 个轨道")
        
        print()
        
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 4. AI 分析
    print("4. AI 分析结果...")
    try:
        # 获取 AI 客户端
        config_file_path = project_root / "config" / "config.yaml"
        ai_client = get_ai_client_from_config(str(config_file_path))
        
        if not ai_client:
            print("   ⚠️  未配置AI客户端，跳过AI分析")
            print()
        else:
            analyzer = QuantumChemistryAnalyzer(ai_client)
            analysis_result = analyzer.analyze(parsed_data)
            print("   ✓ AI 分析完成")
            print()
    except Exception as e:
        print(f"   ⚠️  AI 分析失败: {e}")
        analysis_result = {}
        print()
    
    # 5. 生成报告
    print("5. 生成分析报告...")
    try:
        report_generator = AnalysisReportGenerator(format="markdown", language="zh")
        report = report_generator.generate(
            analysis_result,
            parsed_data=parsed_data,
            output_file=str(project_root / "docs" / "dev" / "test006_analysis_report.md")
        )
        print("   ✓ 报告生成成功")
        print(f"   报告文件: docs/dev/test006_analysis_report.md")
        print()
    except Exception as e:
        print(f"   ✗ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
