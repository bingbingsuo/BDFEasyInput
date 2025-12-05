"""
直接 BDF 执行示例

演示如何使用 BDFDirectRunner 直接运行 BDF 计算（不通过 BDFAutotest）。
"""

import os
from pathlib import Path
import yaml
from bdfeasyinput import BDFConverter
from bdfeasyinput.execution import BDFDirectRunner, create_runner


def example_1_from_yaml_config():
    """示例 1: 从 YAML 配置创建执行器并运行"""
    
    print("=" * 70)
    print("示例 1: 从 YAML 配置创建执行器并运行")
    print("=" * 70)
    print()
    
    # 1. 读取包含执行配置的 YAML 文件
    yaml_file = "examples/h2o_rhf_with_execution.yaml"
    
    if not Path(yaml_file).exists():
        print(f"⚠️  YAML 文件不存在: {yaml_file}")
        print("   请先创建包含 execution 配置的 YAML 文件")
        return
    
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # 2. 转换 YAML 到 BDF
    converter = BDFConverter()
    bdf_input = "output/h2o_rhf.inp"
    
    print(f"1. 转换 YAML 文件: {yaml_file}")
    bdf_content = converter.convert_file(yaml_file, bdf_input)
    print(f"   ✓ BDF 输入文件已生成: {bdf_input}")
    print()
    
    # 3. 从配置创建执行器
    print("2. 创建 BDF 执行器")
    try:
        runner = create_runner(config=config)
        print(f"   ✓ 执行器类型: {type(runner).__name__}")
        
        execution_config = config.get('execution', {})
        if execution_config.get('type') == 'direct':
            print(f"   BDFHOME: {execution_config.get('bdf_home')}")
            print(f"   BDF_TMPDIR: {execution_config.get('bdf_tmpdir', '系统默认')}")
            print(f"   OMP_NUM_THREADS: {execution_config.get('omp_num_threads', '自动')}")
        print()
        
        # 4. 运行计算
        print("3. 运行 BDF 计算")
        result = runner.run(bdf_input, timeout=3600)
        
        print(f"   状态: {result['status']}")
        print(f"   退出码: {result['exit_code']}")
        print(f"   执行时间: {result['execution_time']:.2f} 秒")
        print(f"   输出文件: {result['output_file']}")
        print(f"   错误文件: {result['error_file']}")
        
        if result['status'] == 'success':
            print("   ✓ 计算成功完成！")
        else:
            print("   ✗ 计算失败")
            if result.get('stderr'):
                print(f"   错误信息: {result['stderr'][:200]}")
        
    except ValueError as e:
        print(f"   ✗ 配置错误: {e}")
        print("   请检查 YAML 文件中的 execution 配置")
    except Exception as e:
        print(f"   ✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()


def example_2_direct_runner():
    """示例 2: 直接使用 BDFDirectRunner"""
    
    print()
    print("=" * 70)
    print("示例 2: 直接使用 BDFDirectRunner")
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
    
    # 2. 创建直接执行器
    bdf_home = os.getenv("BDFHOME", "/path/to/bdf/installation")
    
    if not Path(bdf_home).exists():
        print(f"⚠️  BDF 安装目录不存在: {bdf_home}")
        print("   请设置环境变量 BDFHOME 或修改代码中的路径")
        return
    
    print("2. 创建 BDF 直接执行器")
    try:
        runner = BDFDirectRunner(
            bdf_home=bdf_home,
            bdf_tmpdir="/tmp/bdf_tmp",
            omp_num_threads=8,
            omp_stacksize="512M"
        )
        print(f"   ✓ BDFHOME: {bdf_home}")
        print(f"   ✓ BDF 可执行文件: {runner.bdf_executable}")
        print()
        
        # 3. 运行计算
        print("3. 运行 BDF 计算")
        result = runner.run(bdf_input, timeout=3600)
        
        print(f"   状态: {result['status']}")
        print(f"   退出码: {result['exit_code']}")
        print(f"   执行时间: {result['execution_time']:.2f} 秒")
        print(f"   输出文件: {result['output_file']}")
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


if __name__ == "__main__":
    # 确保输出目录存在
    Path("output").mkdir(exist_ok=True)
    
    # 运行示例
    example_1_from_yaml_config()
    # example_2_direct_runner()

