import os
import dashscope
from dashscope import Generation

# 设置API密钥
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 定义工具函数
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

messages = [
    {"role": "user", "content": "搜索中国早期投资VC机构的最新信息，包括机构名称、投资阶段、主要领域、代表项目，制作成表格"}
]

response = Generation.call(
    model="qwen3-max-2026-01-23",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

print("Response:")
print(response)