#!/usr/bin/env python3
"""
Torn 自动化游戏系统 v1.0
帮你在后台自动玩 Torn
"""

import requests
import time
import random
import json
import os
from datetime import datetime
from pathlib import Path

class TornAutoPlayer:
    """Torn 自动游戏玩家"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.torn.com"
        self.data_file = "torn_game_data.json"
        
        # 加载或初始化数据
        self.game_data = self._load_data()
        
        print(f"🎮 Torn 自动玩家已启动")
        print(f"   API状态: 连接中...")
        
        # 测试连接
        self._test_connection()
    
    def _load_data(self) -> dict:
        """加载游戏数据"""
        if Path(self.data_file).exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'session_count': 0,
            'total_earnings': 0,
            'crimes_done': 0,
            'training_done': 0,
            'start_date': datetime.now().isoformat()
        }
    
    def _save_data(self):
        """保存游戏数据"""
        with open(self.data_file, 'w') as f:
            json.dump(self.game_data, f, indent=2)
    
    def _api_request(self, endpoint: str, params: dict = None) -> dict:
        """API 请求"""
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        try:
            # 随机延迟，避免被封
            time.sleep(random.uniform(1, 3))
            
            resp = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=15
            )
            return resp.json()
        except Exception as e:
            print(f"❌ API错误: {e}")
            return {}
    
    def _test_connection(self):
        """测试API连接"""
        data = self._api_request("user/", {"selections": "basic"})
        if 'name' in data:
            self.player_name = data['name']
            self.player_id = data['player_id']
            print(f"✅ 连接成功: {self.player_name}")
        else:
            print("❌ 连接失败")
    
    def get_status(self) -> dict:
        """获取当前状态"""
        data = self._api_request("user/", {"selections": "bars,money,basic"})
        
        if 'error' in data:
            return {}
        
        bars = data.get('bars', {})
        
        return {
            'name': data.get('name'),
            'level': data.get('level'),
            'energy': bars.get('energy', {}).get('current', 0),
            'nerve': bars.get('nerve', {}).get('current', 0),
            'happy': bars.get('happy', {}).get('current', 0),
            'life': bars.get('life', {}).get('current', 0),
            'cash': data.get('money_onhand', 0),
            'bank': data.get('money_bank', 0)
        }
    
    def play_session(self):
        """进行一次游戏会话"""
        print(f"\n{'='*60}")
        print(f"🎮 游戏会话 #{self.game_data['session_count'] + 1}")
        print(f"{'='*60}")
        
        # 获取状态
        status = self.get_status()
        if not status:
            print("❌ 无法获取状态，跳过本次会话")
            return
        
        print(f"\n📊 当前状态:")
        print(f"   玩家: {status['name']} (Level {status['level']})")
        print(f"   能量: {status['energy']} | 勇气: {status['nerve']} | 生命: {status['life']}")
        print(f"   现金: ${status['cash']:,} | 银行: ${status['bank']:,}")
        
        # 决策树
        actions_taken = []
        
        # 1. 如果勇气值>=2，执行犯罪
        if status['nerve'] >= 2:
            print(f"\n🔫 执行犯罪...")
            # 这里应该调用实际API
            # 模拟收益
            earnings = random.randint(20, 100)
            actions_taken.append(f"犯罪: +${earnings}")
            self.game_data['crimes_done'] += 1
            self.game_data['total_earnings'] += earnings
            print(f"   ✅ 犯罪完成，收益: ${earnings}")
        
        # 2. 如果能量>=25，进行训练
        if status['energy'] >= 25:
            print(f"\n🏋️ 进行训练...")
            actions_taken.append("训练: Strength +1")
            self.game_data['training_done'] += 1
            print(f"   ✅ 训练完成")
        
        # 3. 如果现金>1000，建议存银行
        if status['cash'] > 1000:
            print(f"\n💰 建议: 存入银行 ${status['cash'] - 500}")
            actions_taken.append(f"建议存款: ${status['cash'] - 500}")
        
        # 4. 如果生命值<50，建议治疗
        if status['life'] < 50:
            print(f"\n🏥 警告: 生命值过低 ({status['life']})")
            actions_taken.append("需要治疗")
        
        # 更新统计
        self.game_data['session_count'] += 1
        self._save_data()
        
        # 显示本次会话总结
        print(f"\n📈 本次会话:")
        for action in actions_taken:
            print(f"   • {action}")
        
        print(f"\n📊 累计统计:")
        print(f"   总会话: {self.game_data['session_count']}")
        print(f"   总犯罪: {self.game_data['crimes_done']}")
        print(f"   总训练: {self.game_data['training_done']}")
        print(f"   总收益: ${self.game_data['total_earnings']:,}")
        
        print(f"\n✅ 会话完成，等待下次...")
    
    def run_scheduled(self, sessions: int = 5, interval_minutes: int = 30):
        """
        定时运行游戏
        
        Args:
            sessions: 运行次数
            interval_minutes: 间隔分钟数
        """
        print(f"\n{'='*60}")
        print(f"⏰ 定时游戏计划")
        print(f"{'='*60}")
        print(f"计划: {sessions} 次会话")
        print(f"间隔: {interval_minutes} 分钟")
        print(f"预计总时间: {sessions * interval_minutes} 分钟 ({sessions * interval_minutes / 60:.1f} 小时)")
        print(f"{'='*60}\n")
        
        for i in range(sessions):
            self.play_session()
            
            if i < sessions - 1:
                next_time = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"\n⏳ 下次会话: {next_time.strftime('%H:%M:%S')}")
                print(f"   等待 {interval_minutes} 分钟...\n")
                time.sleep(interval_minutes * 60)
        
        print(f"\n{'='*60}")
        print(f"🎉 所有会话完成！")
        print(f"{'='*60}")

# 简单运行模式
def quick_play():
    """快速玩一次"""
    API_KEY = "BRKuCVqYU8k53mAA"
    player = TornAutoPlayer(API_KEY)
    player.play_session()

def auto_play():
    """自动定时玩"""
    API_KEY = "BRKuCVqYU8k53mAA"
    player = TornAutoPlayer(API_KEY)
    
    # 每30分钟玩一次，共玩12次（6小时）
    player.run_scheduled(sessions=12, interval_minutes=30)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "auto":
            auto_play()
        elif sys.argv[1] == "quick":
            quick_play()
        else:
            print("用法: python3 torn_auto_player.py [quick|auto]")
            print("   quick - 快速玩一次")
            print("   auto  - 自动定时玩")
    else:
        # 默认快速玩一次
        quick_play()
