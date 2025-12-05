"""
全局配置文件使用示例

演示如何使用全局配置文件 config.yaml
"""

from pathlib import Path
from bdfeasyinput import load_config, get_execution_config, get_ai_config, get_analysis_config
from bdfeasyinput.execution import create_runner


def example_1_load_config():
    """示例 1: 加载全局配置"""
    
    print("=" * 70)
    print("示例 1: 加载全局配置")
    print("=" * 70)
    print()
    
    try:
        # 加载配置文件
        config = load_config()
        print(f"✓ 配置文件加载成功")
        print()
        
        # 获取各个部分的配置
        execution_config = get_execution_config(config)
        ai_config = get_ai_config(config)
        analysis_config = get_analysis_config(config)
        
        print("执行配置:")
        print(f"  类型: {execution_config.get('type', '未设置')}")
        if execution_config.get('type') == 'direct':
            direct = execution_config.get('direct', {})
            print(f"  BDF 安装目录: {direct.get('bdf_home', '未设置')}")
        print()
        
        print("AI 配置:")
        print(f"  启用: {ai_config.get('enabled', False)}")
        print(f"  默认提供商: {ai_config.get('default_provider', '未设置')}")
        print()
        
        print("分析配置:")
        print(f"  启用: {analysis_config.get('enabled', False)}")
        print(f"  输出格式: {analysis_config.get('output', {}).get('format', '未设置')}")
        
    except FileNotFoundError as e:
        print(f"✗ 配置文件未找到: {e}")
        print("  请创建 config/config.yaml 文件")
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        import traceback
        traceback.print_exc()


def example_2_create_runner_from_config():
    """示例 2: 从配置创建执行器"""
    
    print()
    print("=" * 70)
    print("示例 2: 从配置创建执行器")
    print("=" * 70)
    print()
    
    try:
        # 加载配置
        config = load_config()
        
        # 从配置创建执行器
        runner = create_runner(config=config)
        print(f"✓ 执行器创建成功: {type(runner).__name__}")
        
        execution_config = get_execution_config(config)
        if execution_config.get('type') == 'direct':
            direct = execution_config.get('direct', {})
            print(f"  BDF 安装目录: {direct.get('bdf_home', '未设置')}")
        elif execution_config.get('type') == 'bdfautotest':
            bdfautotest = execution_config.get('bdfautotest', {})
            print(f"  BDFAutotest 路径: {bdfautotest.get('path', '未设置')}")
        
    except Exception as e:
        print(f"✗ 创建执行器失败: {e}")
        import traceback
        traceback.print_exc()


def example_3_minimal_config():
    """示例 3: 最小配置示例"""
    
    print()
    print("=" * 70)
    print("示例 3: 最小配置示例")
    print("=" * 70)
    print()
    
    minimal_config = """
# 最小配置文件示例
execution:
  type: direct
  direct:
    bdf_home: "/path/to/bdf"  # 只需设置 BDF 安装路径

ai:
  enabled: true
  default_provider: "ollama"
  providers:
    ollama:
      enabled: true
      base_url: "http://localhost:11434"
      model: "llama3"

analysis:
  enabled: true
"""
    
    print("最小配置内容:")
    print(minimal_config)
    print("=" * 70)
    print("只需设置必要的参数即可开始使用！")


if __name__ == "__main__":
    # 运行示例
    example_1_load_config()
    example_2_create_runner_from_config()
    example_3_minimal_config()

