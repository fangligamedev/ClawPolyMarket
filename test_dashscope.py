import os
from dashscope import Generation
import dashscope

# 设置API配置
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'

# 测试消息
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "搜索一下中国知名的早期投资VC机构有哪些？"}
]

try:
    response = Generation.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model="qwen3-max-2026-01-23",
        messages=messages,
        result_format="message",
        enable_thinking=True,
        # 启用工具调用
        tools=[
            {
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
            }
        ]
    )
    
    if response.status_code == 200:
        print("=" * 20 + "完整回复" + "=" * 20)
        print(response.output.choices[0].message.content)
        if hasattr(response.output.choices[0].message, 'tool_calls'):
            print("=" * 20 + "工具调用" + "=" * 20)
            print(response.output.choices[0].message.tool_calls)
    else:
        print(f"HTTP返回码：{response.status_code}")
        print(f"错误码：{response.code}")
        print(f"错误信息：{response.message}")
        
except Exception as e:
    print(f"异常：{e}")