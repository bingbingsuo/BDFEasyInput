"""
测试 BDF 执行功能

使用全局配置文件运行 BDF 计算
"""

import sys
from pathlib import Path
from bdfeasyinput import load_config
from bdfeasyinput.execution import create_runner


def main():
    """运行 BDF 计算测试"""
    
    print("=" * 70)
    print("BDF 执行测试")
    print("=" * 70)
    print()
    
    # 输入文件
    input_file = "/Users/bsuo/check/bdf/h2ohess.inp"
    
    # 检查输入文件是否存在
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"✗ 输入文件不存在: {input_file}")
        return 1
    
    print(f"✓ 输入文件: {input_file}")
    print(f"  文件大小: {input_path.stat().st_size} 字节")
    print()
    
    # 加载配置
    try:
        print("1. 加载配置文件...")
        config = load_config()
        print(f"   ✓ 配置文件加载成功")
        
        execution_config = config.get('execution', {})
        exec_type = execution_config.get('type', 'direct')
        print(f"   执行类型: {exec_type}")
        
        if exec_type == 'direct':
            direct = execution_config.get('direct', {})
            bdf_home = direct.get('bdf_home')
            print(f"   BDF 安装目录: {bdf_home}")
            if bdf_home and not Path(bdf_home).exists():
                print(f"   ⚠️  警告: BDF 安装目录不存在: {bdf_home}")
        
        print()
        
    except FileNotFoundError as e:
        print(f"✗ 配置文件未找到: {e}")
        print("  请创建 config/config.yaml 文件")
        return 1
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 创建执行器
    try:
        print("2. 创建执行器...")
        runner = create_runner(config=config)
        print(f"   ✓ 执行器创建成功: {type(runner).__name__}")
        print()
        
    except Exception as e:
        print(f"✗ 创建执行器失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 运行计算
    try:
        print("3. 运行 BDF 计算...")
        print(f"   输入文件: {input_file}")
        print("   正在执行，请稍候...")
        print()
        
        result = runner.run(input_file, timeout=3600)
        
        print("4. 计算结果:")
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
                print(f"     文件大小: {size} 字节")
            else:
                print(f"   ⚠️  输出文件不存在: {output_file}")
        
        if error_file:
            error_path = Path(error_file)
            if error_path.exists():
                size = error_path.stat().st_size
                print(f"   {'✓' if size == 0 else '⚠️'} 错误文件: {error_file}")
                print(f"     文件大小: {size} 字节")
                if size > 0:
                    print("     注意: 错误文件不为空，请检查计算是否有错误")
            else:
                print(f"   ✓ 错误文件不存在（正常，表示没有错误）")
        
        print()
        
        # 检查执行状态
        if result['status'] == 'success':
            print("   ✓ 计算成功完成！")
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

