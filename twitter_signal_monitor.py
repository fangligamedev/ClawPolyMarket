#!/usr/bin/env python3
"""
Twitter 交易信号监控工具
监控 @0xCristal 或其他交易专家的推文
当出现交易信号时发送通知
"""

import os
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests

class TwitterSignalMonitor:
    """
    Twitter 交易信号监控器
    注意: 需要使用 Twitter API v2 或 nitter 等替代方案
    """
    
    def __init__(self, username: str = "0xCristal"):
        self.username = username
        self.keywords = {
            'buy': ['bought', 'buying', 'long', '做多', '买入'],
            'sell': ['sold', 'selling', 'short', '做空', '卖出'],
            'position': ['position', '持仓', '仓位', '押注'],
            'markets': ['polymarket', 'kalshi', '预测市场'],
            'crypto': ['bitcoin', 'ethereum', 'btc', 'eth', '加密']
        }
        
        self.signals_history = []
        self.monitor_log = f"twitter_monitor_{username}.log"
        
        print(f"🐦 Twitter 监控器已启动")
        print(f"   监控账号: @{username}")
        print(f"   监控关键词: {sum(len(v) for v in self.keywords.values())} 个")
    
    def fetch_tweets_nitter(self, count: int = 20) -> List[Dict]:
        """
        使用 nitter 获取推文 (无需 API key)
        nitter 是 Twitter 的开源镜像
        """
        # nitter 实例列表 (部分可能不可用)
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.it",
            "https://nitter.cz",
        ]
        
        tweets = []
        
        for instance in nitter_instances:
            try:
                url = f"{instance}/{self.username}/rss"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # 解析 RSS
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    
                    for item in root.findall('.//item')[:count]:
                        tweet = {
                            'title': item.find('title').text if item.find('title') is not None else '',
                            'link': item.find('link').text if item.find('link') is not None else '',
                            'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
                            'description': item.find('description').text if item.find('description') is not None else ''
                        }
                        tweets.append(tweet)
                    
                    if tweets:
                        break  # 成功获取，跳出循环
                        
            except Exception as e:
                continue
        
        return tweets
    
    def analyze_tweet(self, tweet: Dict) -> Optional[Dict]:
        """
        分析单条推文，提取交易信号
        """
        text = tweet.get('title', '') + ' ' + tweet.get('description', '')
        text_lower = text.lower()
        
        signal = {
            'timestamp': tweet.get('pubDate'),
            'text': text[:200],
            'link': tweet.get('link'),
            'signals': [],
            'confidence': 0
        }
        
        # 检测买入信号
        for keyword in self.keywords['buy']:
            if keyword in text_lower:
                signal['signals'].append(f'BUY:{keyword}')
                signal['confidence'] += 20
        
        # 检测卖出信号
        for keyword in self.keywords['sell']:
            if keyword in text_lower:
                signal['signals'].append(f'SELL:{keyword}')
                signal['confidence'] += 20
        
        # 检测持仓信息
        for keyword in self.keywords['position']:
            if keyword in text_lower:
                signal['signals'].append(f'POSITION:{keyword}')
                signal['confidence'] += 15
        
        # 检测市场提及
        for keyword in self.keywords['markets']:
            if keyword in text_lower:
                signal['signals'].append(f'MARKET:{keyword}')
                signal['confidence'] += 10
        
        # 检测具体市场 (Polymarket 格式)
        market_patterns = [
            r'Will\s+([A-Za-z\s]+)\s+(win|lose|happen)',
            r'([A-Za-z\s]+)\s+by\s+\d{4}',
        ]
        
        for pattern in market_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                signal['signals'].append(f'MARKET_SPECIFIC:{matches[0]}')
                signal['confidence'] += 25
        
        # 提取金额
        amount_pattern = r'\$([\d,]+(?:\.\d+)?)([KkMm]?)'
        amount_matches = re.findall(amount_pattern, text)
        if amount_matches:
            signal['amount'] = amount_matches[0]
            signal['confidence'] += 10
        
        # 只有置信度 > 30 才认为是有效信号
        if signal['confidence'] >= 30 and signal['signals']:
            return signal
        
        return None
    
    def save_signal(self, signal: Dict):
        """保存信号到历史记录"""
        self.signals_history.append(signal)
        
        # 保存到文件
        with open(self.monitor_log, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"时间: {signal['timestamp']}\n")
            f.write(f"信号: {', '.join(signal['signals'])}\n")
            f.write(f"置信度: {signal['confidence']}\n")
            f.write(f"内容: {signal['text']}\n")
            f.write(f"链接: {signal['link']}\n")
    
    def generate_alert(self, signal: Dict):
        """生成警报消息"""
        print("\n" + "🚨" * 30)
        print(f"🚨 交易信号检测到！")
        print("🚨" * 30)
        print(f"\n📅 时间: {signal['timestamp']}")
        print(f"📊 信号类型: {', '.join(signal['signals'])}")
        print(f"🎯 置信度: {signal['confidence']}/100")
        print(f"\n📝 推文内容:\n{signal['text'][:300]}...")
        print(f"\n🔗 链接: {signal['link']}")
        print(f"\n💡 建议操作:")
        
        if 'BUY' in str(signal['signals']):
            print("   1. 点击链接查看完整推文")
            print("   2. 验证市场是否存在")
            print("   3. 小资金跟随测试 ($10-20)")
        elif 'SELL' in str(signal['signals']):
            print("   1. 检查是否已有持仓")
            print("   2. 评估是否跟随卖出")
        
        print("\n⚠️  风险提示: 请先验证信号准确性，不要盲目跟随！")
        print("="*60)
    
    def run_monitor(self, interval: int = 300):
        """
        运行监控循环
        
        Args:
            interval: 检查间隔（秒），默认5分钟
        """
        print(f"\n🔄 开始监控循环（每 {interval} 秒检查一次）")
        print("按 Ctrl+C 停止\n")
        
        checked_tweets = set()  # 避免重复检查
        
        try:
            while True:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查新推文...")
                
                # 获取最新推文
                tweets = self.fetch_tweets_nitter(count=10)
                
                new_signals = 0
                for tweet in tweets:
                    # 使用链接作为唯一标识
                    tweet_id = tweet.get('link', '')
                    
                    if tweet_id and tweet_id not in checked_tweets:
                        checked_tweets.add(tweet_id)
                        
                        # 分析推文
                        signal = self.analyze_tweet(tweet)
                        
                        if signal:
                            self.save_signal(signal)
                            self.generate_alert(signal)
                            new_signals += 1
                
                if new_signals == 0:
                    print(f"   未发现交易信号")
                else:
                    print(f"   发现 {new_signals} 个新信号！")
                
                print(f"   已监控 {len(checked_tweets)} 条推文")
                print()
                
                # 等待下次检查
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ 监控已停止")
            print(f"📊 总共检查 {len(checked_tweets)} 条推文")
            print(f"📈 发现 {len(self.signals_history)} 个交易信号")
            
            if self.signals_history:
                print(f"\n💾 信号历史已保存到: {self.monitor_log}")
    
    def analyze_history(self):
        """分析历史信号"""
        if not self.signals_history:
            print("⚠️  暂无信号历史")
            return
        
        print("\n📊 信号历史分析")
        print("="*60)
        
        buy_signals = [s for s in self.signals_history if 'BUY' in str(s)]
        sell_signals = [s for s in self.signals_history if 'SELL' in str(s)]
        
        print(f"总信号数: {len(self.signals_history)}")
        print(f"买入信号: {len(buy_signals)}")
        print(f"卖出信号: {len(sell_signals)}")
        print(f"平均置信度: {sum(s['confidence'] for s in self.signals_history) / len(self.signals_history):.1f}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter 交易信号监控工具')
    parser.add_argument('--username', '-u', default='0xCristal', 
                       help='要监控的 Twitter 用户名 (默认: 0xCristal)')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='检查间隔（秒）(默认: 300)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🐦 Twitter 交易信号监控工具 v1.0")
    print("="*60)
    print()
    
    # 创建监控器
    monitor = TwitterSignalMonitor(username=args.username)
    
    # 运行监控
    monitor.run_monitor(interval=args.interval)

if __name__ == "__main__":
    main()
