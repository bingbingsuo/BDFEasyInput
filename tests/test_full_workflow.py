"""
完整工作流测试：YAML → BDF 输入 → 执行计算

测试从 YAML 文件转换到 BDF 输入，然后执行计算的完整流程
"""

import sys
from pathlib import Path
from bdfeasyinput import BDFConverter, load_config
from bdfeasyinput.execution import create_runner


def main():
    """测试完整工作流"""
    
    print("=" * 70)
    print("BDFEasyInput 完整工作流测试")
    print("=" * 70)
    print()
    
    # 1. 选择 YAML 输入文件
    yaml_file = "examples/h2o_rhf.yaml"
    yaml_path = Path(yaml_file)
    
    if not yaml_path.exists():
        print(f"✗ YAML 文件不存在: {yaml_file}")
        return 1
    
    print(f"1. 读取 YAML 输入文件: {yaml_file}")
    print(f"   ✓ 文件存在")
    print()
    
    # 2. 转换 YAML 到 BDF
    print("2. 转换 YAML 到 BDF 输入...")
    try:
        converter = BDFConverter()
        
        # 输出文件路径
        output_dir = Path("/Users/bsuo/check/bdf")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 从 YAML 文件名生成 BDF 输入文件名
        bdf_input_file = output_dir / "h2o_rhf.inp"
        
        # 转换
        bdf_content = converter.convert_file(yaml_file, str(bdf_input_file))
        
        print(f"   ✓ BDF 输入文件已生成: {bdf_input_file}")
        print(f"   文件大小: {bdf_input_file.stat().st_size} 字节")
        print()
        
        # 显示 BDF 输入文件内容（前30行）
        print("   BDF 输入文件内容（前30行）:")
        print("   " + "-" * 66)
        with open(bdf_input_file, 'r') as f:
            lines = f.readlines()[:30]
            for i, line in enumerate(lines, 1):
                print(f"   {i:3d}| {line.rstrip()}")
        if len(bdf_content.split('\n')) > 30:
            print("   ... (更多内容)")
        print("   " + "-" * 66)
        print()
        
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 3. 加载配置
    print("3. 加载配置文件...")
    try:
        config = load_config()
        print(f"   ✓ 配置文件加载成功")
        print()
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        return 1
    
    # 4. 创建执行器
    print("4. 创建执行器...")
    try:
        runner = create_runner(config=config)
        print(f"   ✓ 执行器创建成功: {type(runner).__name__}")
        print()
    except Exception as e:
        print(f"✗ 创建执行器失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 5. 运行 BDF 计算
    print("5. 运行 BDF 计算...")
    print(f"   输入文件: {bdf_input_file}")
    print("   正在执行，请稍候...")
    print()
    
    try:
        result = runner.run(str(bdf_input_file), timeout=3600)
        
        print("6. 计算结果:")
        print(f"   状态: {result['status']}")
        print(f"   退出码: {result['exit_code']}")
        print(f"   执行时间: {result['execution_time']:.2f} 秒")
        print()
        
        # 输出文件信息
        output_file = result.get('output_file')
        error_file = result.get('error_file')
        
        if output_file:
            output_path = Path(output_file)
            if output_path.exists():
                size = output_path.stat().st_size
                print(f"   ✓ 输出文件: {output_file}")
                print(f"     文件大小: {size:,} 字节")
                
                # 检查计算是否成功
                if size > 0:
                    # 读取最后几行，查找关键信息
                    with open(output_path, 'r') as f:
                        lines = f.readlines()
                        # 查找能量和终止信息
                        for line in reversed(lines[-50:]):
                            if "normal termination" in line.lower():
                                print(f"     ✓ 计算正常终止")
                                break
                            if "RHF=" in line or "RKS=" in line or "UHF=" in line:
                                print(f"     能量信息: {line.strip()[:80]}")
                                break
            else:
                print(f"   ⚠️  输出文件不存在: {output_file}")
        
        if error_file:
            error_path = Path(error_file)
            if error_path.exists():
                size = error_path.stat().st_size
                if size == 0:
                    print(f"   ✓ 错误文件: {error_file} (0 字节，无错误)")
                else:
                    print(f"   ⚠️  错误文件: {error_file} ({size} 字节)")
                    print("     注意: 错误文件不为空，请检查计算是否有错误")
                    # 显示错误内容（前10行）
                    with open(error_path, 'r') as f:
                        error_lines = f.readlines()[:10]
                        print("     错误内容（前10行）:")
                        for line in error_lines:
                            print(f"     {line.rstrip()}")
        
        print()
        
        # 检查执行状态
        if result['status'] == 'success':
            print("   ✅ 计算成功完成！")
            print()
            print("=" * 70)
            print("完整工作流测试成功！")
            print("=" * 70)
            print()
            print("工作流验证:")
            print("  ✓ YAML 文件读取")
            print("  ✓ YAML → BDF 转换")
            print("  ✓ BDF 输入文件生成")
            print("  ✓ BDF 计算执行")
            print("  ✓ 输出文件生成")
            return 0
        elif result['status'] == 'timeout':
            print("   ✗ 计算超时")
            return 1
        else:
            print("   ✗ 计算失败")
            if result.get('stderr'):
                stderr = result['stderr']
                if stderr:
                    print(f"   错误信息（前500字符）:")
                    print(f"   {stderr[:500]}")
            return 1
        
    except Exception as e:
        print(f"✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

