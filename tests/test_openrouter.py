#!/usr/bin/env python3
"""
测试 OpenRouter AI 配置

此脚本用于测试 OpenRouter 配置是否正确工作
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.config import load_config, merge_config_with_defaults, get_ai_config
from bdfeasyinput.cli import get_ai_client_from_config
from bdfeasyinput.ai import TaskPlanner


def test_config_loading():
    """测试配置加载"""
    print("=" * 70)
    print("测试 1: 配置加载")
    print("=" * 70)
    
    try:
        config = load_config()
        config = merge_config_with_defaults(config)
        ai_config = get_ai_config(config)
        
        print(f"✓ 配置文件加载成功")
        print(f"  默认提供商: {ai_config.get('default_provider')}")
        print(f"  AI 功能启用: {ai_config.get('enabled')}")
        
        providers = ai_config.get('providers', {})
        openrouter_config = providers.get('openrouter', {})
        
        print(f"\n  OpenRouter 配置:")
        print(f"    启用: {openrouter_config.get('enabled')}")
        print(f"    模型: {openrouter_config.get('model')}")
        print(f"    API Key 环境变量: {openrouter_config.get('api_key_env')}")
        
        # 检查 API key
        api_key_env = openrouter_config.get('api_key_env', 'OPENROUTER_API_KEY')
        api_key = os.getenv(api_key_env)
        if api_key:
            print(f"    API Key: {'*' * 20}...{api_key[-4:] if len(api_key) > 4 else '****'}")
        else:
            print(f"    ⚠️  API Key 未设置 (环境变量: {api_key_env})")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client_creation():
    """测试客户端创建"""
    print("\n" + "=" * 70)
    print("测试 2: AI 客户端创建")
    print("=" * 70)
    
    try:
        client = get_ai_client_from_config()
        print(f"✓ AI 客户端创建成功")
        print(f"  客户端类型: {type(client).__name__}")
        
        # 测试可用性
        print("\n  检查客户端可用性...")
        is_available = client.is_available()
        if is_available:
            print("  ✓ 客户端可用")
        else:
            print("  ⚠️  客户端不可用（可能 API key 无效或网络问题）")
        
        return client, is_available
        
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None, False


def test_simple_chat(client):
    """测试简单对话"""
    print("\n" + "=" * 70)
    print("测试 3: 简单对话测试")
    print("=" * 70)
    
    try:
        messages = [
            {"role": "user", "content": "请用一句话回答：1+1等于几？"}
        ]
        
        print("  发送测试消息...")
        response = client.chat(messages, temperature=0.7, max_tokens=50)
        
        print(f"✓ 收到响应:")
        print(f"  {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_planning(client):
    """测试任务规划"""
    print("\n" + "=" * 70)
    print("测试 4: 任务规划测试")
    print("=" * 70)
    
    try:
        planner = TaskPlanner(ai_client=client, validate_output=False)
        
        query = "计算水分子的单点能，使用 PBE0 方法"
        print(f"  查询: {query}")
        print("  正在规划...")
        
        task_config = planner.plan(query)
        
        print(f"✓ 任务规划成功")
        print(f"  任务类型: {task_config.get('task', {}).get('type', 'N/A')}")
        print(f"  方法: {task_config.get('method', {}).get('type', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 任务规划失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("OpenRouter AI 配置测试")
    print("=" * 70)
    print()
    
    results = []
    
    # 测试 1: 配置加载
    if not test_config_loading():
        print("\n❌ 配置加载失败，停止测试")
        return
    
    # 测试 2: 客户端创建
    client, is_available = test_client_creation()
    if not client:
        print("\n❌ 客户端创建失败，停止测试")
        return
    
    if not is_available:
        print("\n⚠️  客户端不可用，但继续测试...")
    
    # 测试 3: 简单对话
    if client:
        results.append(("简单对话", test_simple_chat(client)))
    
    # 测试 4: 任务规划
    if client:
        results.append(("任务规划", test_task_planning(client)))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查配置和网络连接")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

