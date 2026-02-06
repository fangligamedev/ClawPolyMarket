#!/usr/bin/env python3
"""
FiveThirtyEight 民调数据集成
修复数据获取问题
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict

class FiveThirtyEightMonitor:
    """538 民调数据监控器"""
    
    def __init__(self):
        # 正确的 API 端点
        self.urls = [
            "https://projects.fivethirtyeight.com/polls-page/data/polls.json",
            "https://projects.fivethirtyeight.com/2024-election-forecast/data/polls.json"
        ]
        self.cache = {}
        self.cache_time = 3600  # 1小时缓存
        
    async def fetch_polls(self) -> List[Dict]:
        """获取民调数据"""
        
        for url in self.urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # 过滤相关民调
                            relevant = self._filter_polls(data)
                            print(f"📊 从 538 获取到 {len(relevant)} 个相关民调")
                            return relevant
                            
            except Exception as e:
                print(f"❌ 从 {url} 获取失败: {e}")
                continue
        
        return []
    
    def _filter_polls(self, data) -> List[Dict]:
        """过滤相关民调"""
        relevant = []
        
        polls = data if isinstance(data, list) else data.get('polls', [])
        
        for poll in polls:
            # 检查是否是政治相关
            state = poll.get('state', '')
            race_id = str(poll.get('race_id', ''))
            
            # 只关注总统选举相关
            if any(keyword in race_id.lower() for keyword in ['president', '2024']):
                relevant.append({
                    'poll_id': poll.get('poll_id'),
                    'pollster': poll.get('pollster'),
                    'state': state,
                    'date': poll.get('end_date'),
                    'sample_size': poll.get('sample_size'),
                    'population': poll.get('population'),
                    'answers': poll.get('answers', []),
                    'url': poll.get('url')
                })
        
        return relevant
    
    async def analyze_divergence(self, polls: List[Dict]) -> List[Dict]:
        """分析民调与市场价格的偏差"""
        divergences = []
        
        # 这里应该对比 Polymarket 价格
        # 简化版示例
        
        for poll in polls[:10]:  # 只分析前10个
            answers = poll.get('answers', [])
            
            if len(answers) >= 2:
                # 假设第一个和第二个是主要候选人
                candidate_1 = answers[0]
                candidate_2 = answers[1]
                
                # 计算民调差距
                poll_diff = abs(candidate_1.get('pct', 0) - candidate_2.get('pct', 0))
                
                divergence = {
                    'poll': poll,
                    'poll_leader': candidate_1.get('choice'),
                    'poll_margin': poll_diff,
                    'market_price': None,  # 需要从 Polymarket 获取
                    'estimated_edge': 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
                
                divergences.append(divergence)
        
        return divergences
    
    async def run(self):
        """主运行循环"""
        print("🚀 启动 538 民调监控")
        
        while True:
            try:
                polls = await self.fetch_polls()
                
                if polls:
                    divergences = await self.analyze_divergence(polls)
                    
                    # 保存结果
                    import json
                    with open('data/fivethirtyeight_latest.json', 'w') as f:
                        json.dump({
                            'timestamp': datetime.now().isoformat(),
                            'poll_count': len(polls),
                            'divergences': divergences
                        }, f, indent=2)
                
                print(f"⏰ 等待 1 小时后再次检查...")
                await asyncio.sleep(3600)
                
            except Exception as e:
                print(f"❌ 运行错误: {e}")
                await asyncio.sleep(300)

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    
    monitor = FiveThirtyEightMonitor()
    asyncio.run(monitor.run())
