#!/usr/bin/env python3
"""
直接测试 OpenRouter AI（跳过可用性检查）

此脚本直接测试 OpenRouter API 调用，不依赖可用性检查
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bdfeasyinput.config import load_config, merge_config_with_defaults, get_ai_config
from bdfeasyinput.ai.client import OpenRouterClient
from bdfeasyinput.ai import TaskPlanner


def test_direct_api():
    """直接测试 API 调用"""
    print("=" * 70)
    print("OpenRouter 直接 API 测试")
    print("=" * 70)
    print()
    
    # 1. 加载配置
    print("步骤 1: 加载配置...")
    try:
        config = load_config()
        config = merge_config_with_defaults(config)
        ai_config = get_ai_config(config)
        
        openrouter_config = ai_config.get('providers', {}).get('openrouter', {})
        model = openrouter_config.get('model', 'openai/gpt-4')
        api_key_env = openrouter_config.get('api_key_env', 'OPENAI_API_KEY')
        api_key = os.getenv(api_key_env)
        base_url = openrouter_config.get('base_url')
        
        if not api_key:
            print(f"✗ API Key 未设置 (环境变量: {api_key_env})")
            return False
        
        print(f"✓ 配置加载成功")
        print(f"  模型: {model}")
        print(f"  API Key: {'*' * 20}...{api_key[-4:] if len(api_key) > 4 else '****'}")
        print()
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False
    
    # 2. 创建客户端（跳过可用性检查）
    print("步骤 2: 创建 OpenRouter 客户端...")
    try:
        client = OpenRouterClient(
            model=model,
            api_key=api_key,
            base_url=base_url
        )
        print(f"✓ 客户端创建成功")
        print(f"  客户端类型: {type(client).__name__}")
        print()
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 测试简单对话
    print("步骤 3: 测试简单对话...")
    try:
        messages = [
            {"role": "user", "content": "请用一句话回答：1+1等于几？"}
        ]
        
        print("  发送测试消息...")
        response = client.chat(messages, temperature=0.7, max_tokens=50)
        
        print(f"✓ 收到响应:")
        print(f"  {response}")
        print()
    except Exception as e:
        print(f"✗ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 测试任务规划
    print("步骤 4: 测试任务规划...")
    try:
        planner = TaskPlanner(ai_client=client, validate_output=False)
        
        query = "计算水分子的单点能，使用 PBE0 方法"
        print(f"  查询: {query}")
        print("  正在规划...")
        
        task_config = planner.plan(query)
        
        print(f"✓ 任务规划成功")
        print(f"  任务类型: {task_config.get('task', {}).get('type', 'N/A')}")
        
        # 显示部分配置
        if 'molecule' in task_config:
            mol = task_config['molecule']
            print(f"  分子: 电荷={mol.get('charge', 'N/A')}, 自旋={mol.get('multiplicity', 'N/A')}")
        
        if 'method' in task_config:
            method = task_config['method']
            print(f"  方法: {method.get('type', 'N/A')}")
            if 'functional' in method:
                print(f"  泛函: {method.get('functional', 'N/A')}")
        
        print()
    except Exception as e:
        print(f"✗ 任务规划失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print("🎉 所有测试通过！OpenRouter 配置工作正常！")
    print()
    print("您现在可以使用以下命令：")
    print("  bdfeasyinput ai plan \"您的计算任务\" -o task.yaml")
    print("  bdfeasyinput ai chat")
    print("  bdfeasyinput workflow \"您的计算任务\" --run --analyze")
    print()
    
    return True


if __name__ == "__main__":
    success = test_direct_api()
    sys.exit(0 if success else 1)

