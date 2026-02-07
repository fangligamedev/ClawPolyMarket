import os
import json
from dashscope import Generation
import dashscope

# 设置API密钥
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 第一步：获取工具调用
messages = [
    {"role": "system", "content": "你是一个专业的投资顾问，需要提供最新的早期投资VC机构信息。"},
    {"role": "user", "content": "搜索投早期的VC信息，做一个表格给我"}
]

response = Generation.call(
    model="qwen3-max-2026-01-23",
    messages=messages,
    result_format="message",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]
)

if response.status_code == 200:
    tool_calls = response.output.choices[0].message.tool_calls
    if tool_calls:
        # 提取搜索查询
        search_query = json.loads(tool_calls[0].function.arguments)['query']
        print(f"需要搜索: {search_query}")
        
        # 这里应该执行实际的网络搜索
        # 但由于环境限制，我们模拟一个搜索结果
        print("由于环境限制，无法执行实际的网络搜索。")
        print("在完整环境中，这里会调用搜索引擎API并返回真实结果。")
        
        # 模拟搜索结果处理
        final_messages = messages + [
            {"role": "assistant", "content": "", "tool_calls": tool_calls},
            {"role": "tool", "content": "搜索结果：找到了多个早期投资VC机构的信息，包括红杉资本、真格基金、创新工场等知名机构的最新投资动态和详细信息。", "tool_call_id": tool_calls[0].id}
        ]
        
        # 获取最终回答
        final_response = Generation.call(
            model="qwen3-max-2026-01-23",
            messages=final_messages,
            result_format="message"
        )
        
        if final_response.status_code == 200:
            print("=" * 20 + "最终回答" + "=" * 20)
            print(final_response.output.choices[0].message.content)
        else:
            print(f"最终调用失败: {final_response.code} - {final_response.message}")
    else:
        print("没有工具调用请求")
        print(response.output.choices[0].message.content)
else:
    print(f"请求失败: {response.code} - {response.message}")