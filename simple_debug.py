import os
from dashscope import Generation
import dashscope

# 设置API密钥
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

messages = [
    {"role": "user", "content": "搜索早期投资VC机构信息"}
]

try:
    response = Generation.call(
        model="qwen3-max-2026-01-23",
        messages=messages,
        result_format="message"
    )
    
    print("状态码:", response.status_code)
    print("响应内容:", str(response))
    
    # 尝试直接访问输出
    if hasattr(response, 'output'):
        print("有output属性")
        output = response.output
        print("output:", output)
        
        if hasattr(output, 'choices'):
            print("有choices")
            choices = output.choices
            print("choices:", choices)
            
            if len(choices) > 0:
                choice = choices[0]
                print("第一个choice:", choice)
                
                if hasattr(choice, 'message'):
                    message = choice.message
                    print("message:", message)
                    
                    # 检查是否有tool_calls
                    if hasattr(message, 'tool_calls'):
                        print("发现tool_calls!")
                        print("tool_calls:", message.tool_calls)
                    else:
                        print("没有tool_calls属性")
                        # 检查字典形式
                        if isinstance(message, dict):
                            print("message keys:", list(message.keys()))
                            if 'tool_calls' in message:
                                print("字典中有tool_calls:", message['tool_calls'])
                        
    else:
        print("没有output属性")
        print("响应所有属性:", dir(response))
        
except Exception as e:
    print("错误:", e)
    import traceback
    traceback.print_exc()