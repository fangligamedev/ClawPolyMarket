import os
import json
from dashscope import Generation
import dashscope

# 设置API密钥
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

messages = [
    {"role": "user", "content": "搜索投早期的VC信息，做一个表格给我"}
]

try:
    response = Generation.call(
        model="qwen3-max-2026-01-23",
        messages=messages,
        result_format="message",
        enable_thinking=True,  # 启用深度思考
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
    
    print("Status code:", response.status_code)
    if response.status_code == 200:
        print("Response output:", str(response.output))
        print("Full response:", str(response))
    else:
        print(f"Error: {response.code} - {response.message}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()