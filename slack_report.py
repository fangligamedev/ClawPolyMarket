#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

API_KEY = "BRKuCVqYU8k53mAA"

def get_status():
    try:
        resp = requests.get('https://api.torn.com/user/', 
            params={'key': API_KEY, 'selections': 'basic,bars,money'},
            timeout=10)
        data = resp.json()
        if 'name' in data:
            bars = data.get('bars', {})
            return {
                'name': data['name'],
                'level': data.get('level', 1),
                'cash': data.get('money_onhand', 0),
                'energy': bars.get('energy', {}).get('current', 0),
                'nerve': bars.get('nerve', {}).get('current', 0),
                'life': bars.get('life', {}).get('current', 0)
            }
    except:
        pass
    return None

status = get_status()
if status:
    print(f"🎮 Torn 状态 | {datetime.now().strftime('%H:%M')}")
    print(f"👤 {status['name']} (Lv.{status['level']})")
    print(f"💰 ${status['cash']:,} | 🔋{status['energy']} | ⚡{status['nerve']} | ❤️ {status['life']}")
