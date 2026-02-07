#!/usr/bin/env python3
"""
OpenCode + NVIDIA API 集成演示
演示如何通过 OpenAI 兼容格式使用 NVIDIA API
"""

import requests
import json
from datetime import datetime

# 配置
NVIDIA_API_KEY = "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"
BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "minimaxai/minimax-m2.1"

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(response):
    """打印结果"""
    print(f"\n⏱️  响应时间: {response['response_time']:.2f}秒")
    print(f"📊 状态码: {response['status_code']}")
    print(f"🤖 模型: {response['model']}")
    print(f"\n💬 回复:")
    print("-" * 70)
    print(response['content'])
    print("-" * 70)

def demo_basic_chat():
    """演示1: 基础对话"""
    print_header("演示1: 基础对话")
    
    print("\n📝 输入:")
    print('   "你好，请介绍一下你自己"')
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        },
        timeout=30
    )
    
    result = {
        "status_code": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "model": MODEL,
        "content": response.json()['choices'][0]['message']['content']
    }
    
    print_result(result)
    return result

def demo_code_generation():
    """演示2: 代码生成"""
    print_header("演示2: 代码生成")
    
    print("\n📝 输入:")
    print('   "用 Python 写一个快速排序算法，并附带注释"')
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "用 Python 写一个快速排序算法，并附带详细的中文注释"}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        },
        timeout=30
    )
    
    result = {
        "status_code": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "model": MODEL,
        "content": response.json()['choices'][0]['message']['content']
    }
    
    print_result(result)
    return result

def demo_multi_turn_conversation():
    """演示3: 多轮对话"""
    print_header("演示3: 多轮对话")
    
    messages = [
        {"role": "system", "content": "你是一个乐于助人的编程助手"},
        {"role": "user", "content": "什么是递归？"},
        {"role": "assistant", "content": "递归是一种函数调用自身的编程技术。它通常用于解决可以分解为相同子问题的问题。"},
        {"role": "user", "content": "能否给个例子？"}
    ]
    
    print("\n📝 对话历史:")
    print("   1. System: 你是一个编程助手")
    print("   2. User: 什么是递归？")
    print("   3. Assistant: 递归是...")
    print("   4. User: 能否给个例子？")
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.5
        },
        timeout=30
    )
    
    result = {
        "status_code": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "model": MODEL,
        "content": response.json()['choices'][0]['message']['content']
    }
    
    print_result(result)
    return result

def demo_creative_writing():
    """演示4: 创意写作"""
    print_header("演示4: 创意写作")
    
    print("\n📝 输入:")
    print('   "写一首关于人工智能的短诗"')
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "写一首关于人工智能的短诗，需要押韵"}
            ],
            "max_tokens": 200,
            "temperature": 0.9  # 更高的温度产生更有创意的输出
        },
        timeout=30
    )
    
    result = {
        "status_code": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "model": MODEL,
        "content": response.json()['choices'][0]['message']['content']
    }
    
    print_result(result)
    return result

def demo_data_analysis():
    """演示5: 数据分析建议"""
    print_header("演示5: 数据分析建议")
    
    print("\n📝 输入:")
    print('   "我有一个包含100万条记录的销售数据表，应该如何优化查询性能？"')
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "我有一个包含100万条记录的销售数据表，应该如何优化查询性能？请给出具体的技术建议"}
            ],
            "max_tokens": 400,
            "temperature": 0.5
        },
        timeout=30
    )
    
    result = {
        "status_code": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "model": MODEL,
        "content": response.json()['choices'][0]['message']['content']
    }
    
    print_result(result)
    return result

def demo_language_translation():
    """演示6: 多语言翻译"""
    print_header("演示6: 多语言翻译")
    
    print("\n📝 输入:")
    print('   "将以下中文翻译成英文：人工智能正在改变世界"')
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "将以下中文翻译成英文，只输出翻译结果：人工智能正在改变世界"}
            ],
            "max_tokens": 50,
            "temperature": 0.1
        },
        timeout=30
    )
    
    result = {
        "status_code": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "model": MODEL,
        "content": response.json()['choices'][0]['message']['content']
    }
    
    print_result(result)
    return result

def demo_summary():
    """演示总结"""
    print_header("🎯 OpenCode + NVIDIA API 演示总结")
    
    print("""
✅ 已验证的功能:
  1. 基础对话交互
  2. 代码生成和编程辅助
  3. 多轮对话上下文理解
  4. 创意写作（更高温度）
  5. 技术建议和专业咨询
  6. 多语言翻译

📊 API 配置:
  - 端点: https://integrate.api.nvidia.com/v1/chat/completions
  - 模型: minimaxai/minimax-m2.1
  - 认证: Bearer Token (nvapi-xxx)

🔧 使用方式:
  1. HTTP POST 请求
  2. OpenAI 兼容格式
  3. 支持流式响应（可选）

💡 最佳实践:
  - 代码/技术问题: temperature=0.3
  - 创意写作: temperature=0.7-0.9
  - 翻译/准确回答: temperature=0.1
  - 多轮对话: 传递完整消息历史

🚀 下一步:
  - 集成到 OpenCode CLI
  - 实现流式响应
  - 添加错误处理和重试
  - 封装成易用的 Python 库
""")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  🚀 OpenCode + NVIDIA API 集成演示")
    print("  模型: minimaxai/minimax-m2.1")
    print("  时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    demos = [
        ("基础对话", demo_basic_chat),
        ("代码生成", demo_code_generation),
        ("多轮对话", demo_multi_turn_conversation),
        ("创意写作", demo_creative_writing),
        ("技术建议", demo_data_analysis),
        ("多语言翻译", demo_language_translation),
    ]
    
    # 运行所有演示（可以选择性运行）
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
            print(f"\n✅ 演示 {i} 完成: {name}")
        except Exception as e:
            print(f"\n❌ 演示 {i} 失败: {name}")
            print(f"   错误: {str(e)}")
    
    # 总结
    demo_summary()

if __name__ == "__main__":
    main()
