#!/usr/bin/env python3
"""
简单测试 OpenRouter - 检查配置和基本连接
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("OpenRouter 配置测试")
print("=" * 70)
print()

# 1. 检查配置
print("1. 检查配置...")
try:
    from bdfeasyinput.config import load_config, merge_config_with_defaults, get_ai_config
    config = load_config()
    config = merge_config_with_defaults(config)
    ai_config = get_ai_config(config)
    
    print(f"   ✓ 配置文件加载成功")
    print(f"   ✓ 默认提供商: {ai_config.get('default_provider')}")
    
    openrouter = ai_config.get('providers', {}).get('openrouter', {})
    print(f"   ✓ OpenRouter 启用: {openrouter.get('enabled')}")
    print(f"   ✓ 模型: {openrouter.get('model')}")
    
    api_key_env = openrouter.get('api_key_env', 'OPENAI_API_KEY')
    api_key = os.getenv(api_key_env)
    if api_key:
        print(f"   ✓ API Key 已设置 ({len(api_key)} 字符)")
    else:
        print(f"   ✗ API Key 未设置")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ 配置加载失败: {e}")
    sys.exit(1)

print()

# 2. 检查依赖
print("2. 检查依赖...")
try:
    from openai import OpenAI
    import openai
    print(f"   ✓ openai 包已安装 (版本: {openai.__version__})")
    
    # 检查是否是新版本 API
    try:
        client_test = OpenAI(api_key="test")
        print(f"   ✓ OpenAI 1.x API 可用")
    except:
        print(f"   ⚠️  OpenAI API 版本可能不兼容")
except ImportError as e:
    print(f"   ✗ openai 包未安装: {e}")
    print(f"   请运行: pip3 install openai>=1.0.0")
    sys.exit(1)

print()

# 3. 创建客户端
print("3. 创建 OpenRouter 客户端...")
try:
    from bdfeasyinput.ai.client import OpenRouterClient
    
    client = OpenRouterClient(
        model=openrouter.get('model', 'openai/gpt-4'),
        api_key=api_key,
        base_url=openrouter.get('base_url')
    )
    print(f"   ✓ 客户端创建成功")
    print(f"   ✓ 客户端类型: {type(client).__name__}")
except Exception as e:
    print(f"   ✗ 客户端创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 4. 测试 API 调用
print("4. 测试 API 调用...")
print("   注意: OpenRouter 需要在 https://openrouter.ai/settings/privacy 配置数据隐私策略")
print("   如果遇到 404 错误，请访问上述链接配置隐私设置")
print()

try:
    messages = [{"role": "user", "content": "Hello, please respond with 'OK'"}]
    print("   发送测试消息...")
    response = client.chat(messages, temperature=0.7, max_tokens=20)
    print(f"   ✓ API 调用成功!")
    print(f"   ✓ 响应: {response[:100]}")
    print()
    print("=" * 70)
    print("🎉 所有测试通过！OpenRouter 配置工作正常！")
    print("=" * 70)
except Exception as e:
    error_msg = str(e)
    print(f"   ✗ API 调用失败")
    print(f"   错误: {error_msg[:200]}")
    print()
    
    if "404" in error_msg and "data policy" in error_msg.lower():
        print("   ⚠️  需要配置 OpenRouter 数据隐私策略:")
        print("      1. 访问 https://openrouter.ai/settings/privacy")
        print("      2. 配置数据使用策略")
        print("      3. 重新运行测试")
    elif "403" in error_msg:
        print("   ⚠️  API Key 可能无效或没有权限")
        print("      请检查 API Key 是否正确")
    elif "401" in error_msg:
        print("   ⚠️  认证失败")
        print("      请检查 API Key 是否正确设置")
    else:
        print("   ⚠️  其他错误，请检查网络连接和 API 配置")
    
    print()
    print("=" * 70)
    print("⚠️  测试未完全通过，但配置基本正确")
    print("=" * 70)
    sys.exit(1)

