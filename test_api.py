#!/usr/bin/env python3
import requests

API_KEY = 'BRKuCVqYU8k53mAA'
print('测试 API 连接...')
resp = requests.get('https://api.torn.com/user/', 
    params={'key': API_KEY, 'selections': 'basic,bars,money'},
    timeout=10)
data = resp.json()
if 'name' in data:
    print(f'✅ 连接成功！')
    print(f'玩家: {data["name"]}')
    print(f'现金: ${data.get("money_onhand", 0)}')
    bars = data.get('bars', {})
    print(f'能量: {bars.get("energy", {}).get("current", 0)}')
    print(f'勇气: {bars.get("nerve", {}).get("current", 0)}')
else:
    print(f'❌ 错误: {data}')
