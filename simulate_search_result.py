import os
import json
from dashscope import Generation
import dashscope

# 设置API密钥
os.environ['DASHSCOPE_API_KEY'] = 'sk-4602f5f3248249728db8b44347ff7ab6'
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 模拟搜索结果（这应该是DashScope服务器执行搜索后返回的内容）
search_results = """
根据最新信息，中国早期投资VC机构包括：

1. 红杉资本中国 - 专注种子轮到A轮，投资领域包括科技、消费、医疗，代表项目：阿里巴巴、京东、拼多多
2. 真格基金 - 专注天使轮，投资领域包括互联网、AI、消费升级，代表项目：美团、小红书、依图科技  
3. 创新工场 - 专注天使轮到A轮，投资领域包括AI、SaaS、移动互联网，代表项目：美图、知乎、旷视科技
4. 晨兴资本 - 专注种子轮到A轮，投资领域包括科技、消费、企业服务，代表项目：小米、快手、携程
5. 启明创投 - 专注A轮到B轮，投资领域包括医疗健康、TMT，代表项目：美团点评、小米、Bilibili
6. 高榕资本 - 专注A轮到B轮，投资领域包括消费互联网、企业服务，代表项目：美团、拼多多、虎牙
7. 源码资本 - 专注A轮到B轮，投资领域包括互联网、科技、消费，代表项目：字节跳动、美团、理想汽车
8. 蓝驰创投 - 专注天使轮到A轮，投资领域包括企业服务、硬科技、医疗，代表项目：滴滴、趣店、水滴
"""

messages = [
    {"role": "system", "content": "你是一个专业的投资顾问，需要基于搜索结果提供详细的早期投资VC机构信息表格。"},
    {"role": "user", "content": "搜索投早期的VC信息，做一个表格给我"},
    {"role": "assistant", "content": "", "tool_calls": [{"function": {"arguments": "{\"query\": \"早期投资风险投资公司 VC 信息 投资阶段 领域\"}", "name": "web_search"}, "id": "call_d309516b088b44d6a31ceac3", "index": 0, "type": "function"}]},
    {"role": "tool", "content": search_results, "tool_call_id": "call_d309516b088b44d6a31ceac3"}
]

response = Generation.call(
    model="qwen3-max-2026-01-23",
    messages=messages,
    result_format="message"
)

if response.status_code == 200:
    print("=" * 20 + "基于搜索结果的回答" + "=" * 20)
    print(response.output.choices[0].message.content)
else:
    print(f"请求失败: {response.code} - {response.message}")