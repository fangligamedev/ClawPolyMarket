import os
from dashscope import Generation
import dashscope

# 设置API配置
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'

messages = [
    {"role": "system", "content": "你是一个专业的投资分析师，擅长整理和分析风险投资机构信息。请提供最新的早期投资VC机构详细信息，并制作成表格格式。"},
    {"role": "user", "content": "搜索投早期的VC信息，做一个详细的表格给我，包括机构名称、投资阶段、主要领域、代表项目、总部地点、官网等信息。"}
]

response = Generation.call(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen3-max-2026-01-23",
    messages=messages,
    result_format="message",
    enable_thinking=True,
    # 启用工具调用
    tools=[{
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
    }]
)

if response.status_code == 200:
    # 检查是否有工具调用
    if hasattr(response.output.choices[0].message, 'tool_calls') and response.output.choices[0].message.tool_calls:
        print("检测到工具调用请求:")
        print(response.output.choices[0].message.tool_calls)
    else:
        print("=" * 20 + "完整回复" + "=" * 20)
        print(response.output.choices[0].message.content)
else:
    print(f"HTTP返回码：{response.status_code}")
    print(f"错误码：{response.code}")
    print(f"错误信息：{response.message}")