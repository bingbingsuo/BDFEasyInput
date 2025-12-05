"""
BDF 执行模块使用示例

演示如何使用 BDFAutotestRunner 运行 BDF 计算。
"""

from pathlib import Path
from bdfeasyinput import BDFConverter
from bdfeasyinput.execution import BDFAutotestRunner


def example_1_convert_and_run():
    """示例 1: 转换 YAML 并运行 BDF 计算"""
    
    print("=" * 70)
    print("示例 1: 转换 YAML 并运行 BDF 计算")
    print("=" * 70)
    print()
    
    # 1. 转换 YAML 到 BDF
    converter = BDFConverter()
    yaml_file = "examples/h2o_rhf.yaml"
    bdf_input = "output/h2o_rhf.inp"
    
    print(f"1. 转换 YAML 文件: {yaml_file}")
    bdf_content = converter.convert_file(yaml_file, bdf_input)
    print(f"   ✓ BDF 输入文件已生成: {bdf_input}")
    print()
    
    # 2. 运行 BDF 计算
    # 注意：需要设置正确的 BDFAutotest 路径
    bdfautotest_path = os.getenv("BDFAUTOTEST_PATH", "/path/to/BDFAutoTest")
    
    if not Path(bdfautotest_path).exists():
        print(f"⚠️  BDFAutotest 路径不存在: {bdfautotest_path}")
        print("   请设置环境变量 BDFAUTOTEST_PATH 或修改代码中的路径")
        return
    
    print(f"2. 运行 BDF 计算")
    print(f"   BDFAutotest 路径: {bdfautotest_path}")
    
    try:
        runner = BDFAutotestRunner(bdfautotest_path)
        
        # 检查 BDF 安装
        check_result = runner.check_bdf_installation()
        print(f"   BDFHOME: {check_result.get('bdf_home')}")
        print(f"   BDF 可执行文件存在: {check_result.get('bdf_executable_exists', False)}")
        print()
        
        # 运行计算
        result = runner.run(bdf_input, timeout=3600)
        
        print(f"3. 计算结果:")
        print(f"   状态: {result['status']}")
        print(f"   退出码: {result['exit_code']}")
        print(f"   执行时间: {result['execution_time']:.2f} 秒")
        print(f"   输出文件: {result['output_file']}")
        
        if result.get('error_file'):
            print(f"   错误文件: {result['error_file']}")
        
        if result['status'] == 'success':
            print("   ✓ 计算成功完成！")
        else:
            print("   ✗ 计算失败")
            if result.get('stderr'):
                print(f"   错误信息: {result['stderr'][:200]}")
        
    except Exception as e:
        print(f"   ✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()


def example_2_direct_run():
    """示例 2: 直接运行已有的 BDF 输入文件"""
    
    print()
    print("=" * 70)
    print("示例 2: 直接运行已有的 BDF 输入文件")
    print("=" * 70)
    print()
    
    bdf_input = "output/h2o_rhf.inp"
    
    if not Path(bdf_input).exists():
        print(f"⚠️  BDF 输入文件不存在: {bdf_input}")
        print("   请先运行示例 1 生成输入文件")
        return
    
    bdfautotest_path = os.getenv("BDFAUTOTEST_PATH", "/path/to/BDFAutoTest")
    
    if not Path(bdfautotest_path).exists():
        print(f"⚠️  BDFAutotest 路径不存在: {bdfautotest_path}")
        return
    
    try:
        runner = BDFAutotestRunner(bdfautotest_path)
        result = runner.run(bdf_input)
        
        print(f"计算状态: {result['status']}")
        print(f"输出文件: {result['output_file']}")
        
    except Exception as e:
        print(f"执行失败: {e}")


if __name__ == "__main__":
    import os
    
    # 确保输出目录存在
    Path("output").mkdir(exist_ok=True)
    
    # 运行示例
    example_1_convert_and_run()
    # example_2_direct_run()

