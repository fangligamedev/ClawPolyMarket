#!/usr/bin/env python3
"""
Twitter API v2 集成模块
实时流监控交易信号
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List

try:
    import tweepy
except ImportError:
    print("Installing tweepy...")
    os.system("pip install tweepy -q")
    import tweepy

class TwitterSignalMonitor:
    """Twitter 实时信号监控器"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        
        # 监控账号列表
        self.accounts = [
            '0xCristal',
            'Polymarket',
            'PolymarketWhale',
            'vsinicki',
            'DOMOCOSTA7',
            'syndicatexbt',
            'optimalopp',
            'traderpow'
        ]
        
        # 交易关键词
        self.keywords = [
            'bought', 'sold', 'buy', 'sell',
            'long', 'short', 'position',
            'polymarket', 'prediction',
            'trump', 'biden', 'election'
        ]
        
        self.client = None
        self.signals = []
        
    def connect(self):
        """连接 Twitter API"""
        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                wait_on_rate_limit=True
            )
            print("✅ Twitter API 连接成功")
            return True
        except Exception as e:
            print(f"❌ Twitter API 连接失败: {e}")
            return False
    
    def fetch_user_tweets(self, username: str, count: int = 10) -> List[Dict]:
        """获取用户最近推文"""
        try:
            user = self.client.get_user(username=username)
            if not user.data:
                return []
            
            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=count,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not tweets.data:
                return []
            
            results = []
            for tweet in tweets.data:
                text = tweet.text.lower()
                
                # 检查是否包含交易关键词
                for keyword in self.keywords:
                    if keyword in text:
                        signal = {
                            'source': 'twitter',
                            'username': username,
                            'text': tweet.text,
                            'created_at': str(tweet.created_at),
                            'keyword': keyword,
                            'confidence': self._calculate_confidence(text),
                            'metrics': tweet.public_metrics
                        }
                        results.append(signal)
                        break
            
            return results
            
        except Exception as e:
            print(f"❌ 获取推文失败 @{username}: {e}")
            return []
    
    def _calculate_confidence(self, text: str) -> int:
        """计算信号置信度"""
        score = 50
        
        # 金额提及
        if '$' in text and any(c.isdigit() for c in text):
            score += 20
        
        # 具体市场
        if any(word in text for word in ['trump', 'biden', 'election', 'nba']):
            score += 15
        
        # 行动词
        if any(word in text for word in ['bought', 'sold', 'entered']):
            score += 15
        
        return min(score, 100)
    
    async def monitor_stream(self):
        """实时监控流"""
        print("🚀 启动 Twitter 实时监控")
        
        while True:
            try:
                all_signals = []
                
                for account in self.accounts:
                    tweets = self.fetch_user_tweets(account, count=5)
                    all_signals.extend(tweets)
                    await asyncio.sleep(1)  # 避免频率限制
                
                # 过滤高置信度信号
                high_confidence = [s for s in all_signals if s['confidence'] >= 70]
                
                if high_confidence:
                    print(f"\n🚨 发现 {len(high_confidence)} 个高置信度信号!")
                    for signal in high_confidence:
                        print(f"   @{signal['username']}: {signal['text'][:50]}...")
                        print(f"   置信度: {signal['confidence']}/100")
                        
                        # 保存信号
                        self._save_signal(signal)
                
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 等待 60 秒...")
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                await asyncio.sleep(60)
    
    def _save_signal(self, signal: Dict):
        """保存信号到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"signals/twitter_signal_{timestamp}.json"
        
        os.makedirs('signals', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
        
        print(f"   💾 信号已保存: {filename}")

async def main():
    """主函数"""
    monitor = TwitterSignalMonitor()
    
    if monitor.connect():
        await monitor.monitor_stream()
    else:
        print("❌ 无法连接 Twitter API")
        print("\n💡 请设置环境变量:")
        print("   export TWITTER_BEARER_TOKEN='...'")
        print("   export TWITTER_API_KEY='...'")
        print("   export TWITTER_API_SECRET='...'")

if __name__ == "__main__":
    asyncio.run(main())
