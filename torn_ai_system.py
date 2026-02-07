#!/usr/bin/env python3
"""
Torn AI 核心系统
OpenClaw 专用
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('torn_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TornAI:
    """
    Torn 游戏 AI 核心类
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.torn.com"
        self.player_id = None
        self.player_name = None
        self.cash = 0
        self.bank = 0
        self.stocks = {}
        self.stats = {}
        
        # 初始化
        self._init_player()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送API请求"""
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            data = response.json()
            
            if 'error' in data:
                logger.error(f"API错误: {data['error']['error']}")
                return {}
            
            return data
        except Exception as e:
            logger.error(f"请求失败: {e}")
            return {}
    
    def _init_player(self):
        """初始化玩家信息"""
        data = self._make_request("user/", {"selections": "basic"})
        if data:
            self.player_id = data.get('player_id')
            self.player_name = data.get('name')
            logger.info(f"初始化完成: {self.player_name} (ID: {self.player_id})")
    
    def update_status(self) -> Dict:
        """更新玩家状态"""
        data = self._make_request("user/", {"selections": "money,stocks,stats"})
        
        if data:
            self.cash = data.get('money_onhand', 0)
            self.bank = data.get('money_bank', 0)
            self.stocks = data.get('stocks', {})
            self.stats = data.get('stats', {})
            
            return {
                'cash': self.cash,
                'bank': self.bank,
                'total': self.cash + self.bank,
                'stocks': len(self.stocks),
                'stats': self.stats
            }
        return {}
    
    def get_stock_market(self) -> Dict:
        """获取股票市场信息"""
        data = self._make_request("torn/", {"selections": "stocks"})
        return data.get('stocks', {})
    
    def analyze_stocks(self) -> List[Dict]:
        """分析股票投资机会"""
        stocks = self.get_stock_market()
        analysis = []
        
        for stock_id, stock_data in stocks.items():
            analysis.append({
                'id': stock_id,
                'name': stock_data.get('name'),
                'acronym': stock_data.get('acronym'),
                'current_price': stock_data.get('current_price'),
                # 这里可以添加更多分析指标
            })
        
        return analysis
    
    def recommend_crime(self) -> Dict:
        """推荐最优犯罪选择"""
        # 基于当前资金和技能推荐
        recommendations = {
            'search_for_cash': {
                'name': 'Search for Cash',
                'risk': 'low',
                'reward': '$0-100',
                'recommended': self.cash < 1000
            },
            'sell_copper': {
                'name': 'Sell Coppered Wares',
                'risk': 'low',
                'reward': '$0-500',
                'recommended': self.cash < 5000
            },
            'rob_senior': {
                'name': 'Rob a Senior',
                'risk': 'medium',
                'reward': '$1000-5000',
                'recommended': self.stats.get('strength', 0) > 100
            }
        }
        
        # 选择最佳推荐
        for crime_id, crime_info in recommendations.items():
            if crime_info['recommended']:
                return crime_info
        
        return recommendations['search_for_cash']
    
    def get_training_recommendation(self) -> Dict:
        """获取训练建议"""
        if not self.stats:
            return {}
        
        # 找出最低属性
        stats_list = [
            ('strength', self.stats.get('strength', 0)),
            ('speed', self.stats.get('speed', 0)),
            ('defense', self.stats.get('defense', 0)),
            ('dexterity', self.stats.get('dexterity', 0))
        ]
        
        lowest_stat = min(stats_list, key=lambda x: x[1])
        
        return {
            'recommended_stat': lowest_stat[0],
            'current_value': lowest_stat[1],
            'gyms': ['Gym 1', 'Gym 2']  # 根据等级推荐
        }
    
    def display_dashboard(self):
        """显示AI仪表盘"""
        print("\n" + "=" * 60)
        print(f"🤖 Torn AI Dashboard - {self.player_name}")
        print("=" * 60)
        
        # 更新状态
        status = self.update_status()
        
        print(f"\n💰 资产状况:")
        print(f"   现金: ${status.get('cash', 0):,}")
        print(f"   银行: ${status.get('bank', 0):,}")
        print(f"   总计: ${status.get('total', 0):,}")
        print(f"   股票: {status.get('stocks', 0)} 支")
        
        if self.stats:
            print(f"\n💪 属性状况:")
            print(f"   力量: {self.stats.get('strength', 0):,}")
            print(f"   速度: {self.stats.get('speed', 0):,}")
            print(f"   防御: {self.stats.get('defense', 0):,}")
            print(f"   灵巧: {self.stats.get('dexterity', 0):,}")
        
        # 犯罪推荐
        crime = self.recommend_crime()
        print(f"\n🔫 犯罪推荐:")
        print(f"   推荐: {crime['name']}")
        print(f"   风险: {crime['risk']}")
        print(f"   收益: {crime['reward']}")
        
        # 训练推荐
        training = self.get_training_recommendation()
        if training:
            print(f"\n🏋️ 训练推荐:")
            print(f"   推荐训练: {training['recommended_stat']}")
            print(f"   当前值: {training['current_value']:,}")
        
        print("\n" + "=" * 60)

# 主程序
if __name__ == "__main__":
    API_KEY = "BRKuCVqYU8k53mAA"
    
    print("🚀 启动 Torn AI 系统...")
    ai = TornAI(API_KEY)
    
    # 显示仪表盘
    ai.display_dashboard()
    
    print("\n✅ AI 系统运行正常！")
    print("📊 数据已收集，开始分析...")
