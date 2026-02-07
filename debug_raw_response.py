import os
import json
from dashscope import Generation
import dashscope

# 设置API密钥
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

messages = [
    {"role": "user", "content": "搜索投早期的VC信息"}
]

try:
    response = Generation.call(
        model="qwen3-max-2026-01-23",
        messages=messages,
        result_format="message"
    )
    
    print("状态码:", response.status_code)
    print("完整响应对象类型:", type(response))
    print("响应对象属性:", dir(response))
    
    # 尝试不同的方式访问数据
    if hasattr(response, 'output'):
        print("Output exists")
        print("Output type:", type(response.output))
        if hasattr(response.output, 'choices'):
            print("Choices exists")
            choice = response.output.choices[0]
            print("Choice type:", type(choice))
            print("Choice attributes:", dir(choice))
            
            if hasattr(choice, 'message'):
                message = choice.message
                print("Message attributes:", dir(message))
                print("Message content:", getattr(message, 'content', 'No content'))
                
                # 检查是否有 tool_calls
                if hasattr(message, 'tool_calls'):
                    print("Tool calls found:", message.tool_calls)
                else:
                    print("No tool_calls attribute")
                    # 尝试直接访问字典
                    if isinstance(message, dict):
                        print("Message as dict:", message)
                    else:
                        print("Message is not a dict")
        else:
            print("No choices in output")
            print("Output content:", response.output)
    else:
        print("No output in response")
        print("Response content:", response)
        
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()