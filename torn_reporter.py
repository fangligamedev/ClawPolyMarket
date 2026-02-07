#!/usr/bin/env python3
"""
Torn 游戏状态汇报器
定时向 Slack 发送游戏状态
"""

import requests
import json
import os
from datetime import datetime

# API 配置
API_KEY = "BRKuCVqYU8k53mAA"
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL', '')  # 如果有 Slack webhook

def get_game_status():
    """获取游戏状态"""
    try:
        resp = requests.get(
            'https://api.torn.com/user/',
            params={'key': API_KEY, 'selections': 'bars,money,basic,stats'},
            timeout=10
        )
        data = resp.json()
        
        if 'error' in data:
            return None
        
        bars = data.get('bars', {})
        return {
            'name': data.get('name'),
            'level': data.get('level'),
            'energy': bars.get('energy', {}).get('current', 0),
            'nerve': bars.get('nerve', {}).get('current', 0),
            'happy': bars.get('happy', {}).get('current', 0),
            'life': bars.get('life', {}).get('current', 0),
            'cash': data.get('money_onhand', 0),
            'bank': data.get('money_bank', 0),
            'stats': data.get('stats', {})
        }
    except Exception as e:
        print(f"获取状态失败: {e}")
        return None

def generate_report():
    """生成游戏报告"""
    status = get_game_status()
    if not status:
        return "❌ 无法获取游戏状态"
    
    # 加载游戏数据
    game_data = {}
    if os.path.exists('torn_game_data.json'):
        with open('torn_game_data.json', 'r') as f:
            game_data = json.load(f)
    
    total = status['cash'] + status['bank']
    
    report = f"""
🎮 **Torn 游戏状态汇报** 
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

👤 **玩家**: {status['name']} (Level {status['level']})

💰 **资产状况**:
• 现金: ${status['cash']:,}
• 银行: ${status['bank']:,}
• 总计: ${total:,}

🔋 **状态条**:
• 能量: {status['energy']}/100
• 勇气: {status['nerve']}/10
• 生命: {status['life']}/100
• 快乐: {status['happy']}/100

💪 **属性**:
• 力量: {status['stats'].get('strength', 0):,}
• 速度: {status['stats'].get('speed', 0):,}
• 防御: {status['stats'].get('defense', 0):,}
• 灵巧: {status['stats'].get('dexterity', 0):,}

📊 **今日统计**:
• 会话次数: {game_data.get('session_count', 0)}
• 执行犯罪: {game_data.get('crimes_done', 0)}
• 训练次数: {game_data.get('training_done', 0)}
• 累计收益: ${game_data.get('total_earnings', 0):,}

🤖 **自动状态**: 运行中 ✅
    """
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(report)
