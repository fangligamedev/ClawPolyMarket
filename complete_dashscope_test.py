import os
from dashscope import Generation
import dashscope
import json

# 配置 DashScope
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'

def handle_tool_call(tool_calls):
    """处理工具调用"""
    results = []
    for tool_call in tool_calls:
        if tool_call['function']['name'] == 'web_search':
            # 这里应该实际执行搜索，但我们需要模拟或使用其他方式
            # 由于我们无法直接执行 web_search，返回一个占位符
            results.append({
                "tool_call_id": tool_call['id'],
                "output": "由于环境限制，无法直接执行 web_search 工具调用。需要通过 DashScope 的完整工具调用流程来处理。"
            })
    return results

messages = [
    {"role": "system", "content": "You are a helpful assistant with access to web search tools."},
    {"role": "user", "content": "搜索投早期的VC信息，做一个表格给我"}
]

# 第一次调用 - 获取工具调用请求
response = Generation.call(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen3-max-2026-01-23",
    messages=messages,
    result_format="message",
    enable_thinking=True,
    tools=[{
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }]
)

if response.status_code == 200:
    message = response.output.choices[0].message
    
    # 检查是否有工具调用
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print("检测到工具调用请求:")
        print(json.dumps(message.tool_calls, indent=2, ensure_ascii=False))
        
        # 处理工具调用（这里需要实际的搜索实现）
        tool_results = handle_tool_call(message.tool_calls)
        
        # 准备下一轮消息
        next_messages = messages + [
            {"role": "assistant", "tool_calls": message.tool_calls},
            {"role": "tool", "tool_call_id": tool_results[0]["tool_call_id"], "content": tool_results[0]["output"]}
        ]
        
        # 第二次调用 - 提供工具结果
        final_response = Generation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-max-2026-01-23",
            messages=next_messages,
            result_format="message",
            enable_thinking=True
        )
        
        if final_response.status_code == 200:
            print("\n最终回复:")
            print(final_response.output.choices[0].message.content)
        else:
            print(f"最终调用失败: {final_response.code} - {final_response.message}")
    else:
        # 直接回复
        print("直接回复:")
        print(message.content)
else:
    print(f"HTTP返回码：{response.status_code}")
    print(f"错误码：{response.code}")
    print(f"错误信息：{response.message}")