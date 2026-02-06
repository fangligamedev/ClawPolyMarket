#!/usr/bin/env python3
"""
Polymarket 外部数据源集成系统
集成：
1. Twitter API - 监控交易信号
2. FiveThirtyEight - 民调数据
3. ESPN - 体育数据
4. Discord/Telegram - 通知推送
"""

import os
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataIntegrationHub:
    """
    外部数据源集成中心
    """
    
    def __init__(self):
        self.data_cache = {}
        self.cache_time = 300  # 5分钟缓存
        
        # API 配置
        self.config = {
            'twitter': {
                'enabled': True,
                'accounts': ['0xCristal', 'Polymarket', 'PolymarketWhale'],
                'keywords': ['bought', 'sold', 'long', 'short', 'position', 'polymarket']
            },
            'fivethirtyeight': {
                'enabled': True,
                'url': 'https://projects.fivethirtyeight.com/polls/data/polls.json',
                'check_interval': 3600  # 每小时检查
            },
            'espn': {
                'enabled': True,
                'url': 'https://site.api.espn.com/apis/site/v2/sports',
                'sports': ['basketball/nba', 'football/nfl']
            },
            'discord': {
                'enabled': False,  # 需要 webhook
                'webhook_url': os.getenv('DISCORD_WEBHOOK', '')
            },
            'telegram': {
                'enabled': False,  # 需要 bot token
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
            }
        }
    
    # ==========================================
    # 1. Twitter 监控
    # ==========================================
    async def fetch_twitter_nitter(self, username: str) -> List[Dict]:
        """
        使用 nitter 获取推文
        """
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.it",
            "https://nitter.cz",
        ]
        
        tweets = []
        
        for instance in nitter_instances:
            try:
                url = f"{instance}/{username}/rss"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            import xml.etree.ElementTree as ET
                            data = await response.text()
                            root = ET.fromstring(data)
                            
                            for item in root.findall('.//item')[:10]:
                                tweet = {
                                    'username': username,
                                    'title': item.find('title').text if item.find('title') is not None else '',
                                    'link': item.find('link').text if item.find('link') is not None else '',
                                    'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
                                    'description': item.find('description').text if item.find('description') is not None else ''
                                }
                                tweets.append(tweet)
                            
                            if tweets:
                                break
                                
            except Exception as e:
                logger.error(f"Error fetching from {instance}: {e}")
                continue
        
        return tweets
    
    async def monitor_twitter_accounts(self) -> List[Dict]:
        """
        监控多个 Twitter 账号
        """
        all_tweets = []
        
        for account in self.config['twitter']['accounts']:
            logger.info(f"🐦 监控 @{account}...")
            tweets = await self.fetch_twitter_nitter(account)
            
            # 过滤包含关键词的推文
            for tweet in tweets:
                text = (tweet.get('title', '') + ' ' + tweet.get('description', '')).lower()
                
                for keyword in self.config['twitter']['keywords']:
                    if keyword in text:
                        tweet['signal_type'] = keyword
                        tweet['confidence'] = self._calculate_signal_confidence(text)
                        all_tweets.append(tweet)
                        break
        
        return all_tweets
    
    def _calculate_signal_confidence(self, text: str) -> int:
        """计算信号置信度"""
        score = 50
        
        # 金额提及 +20
        if '$' in text and any(c.isdigit() for c in text):
            score += 20
        
        # 具体市场提及 +15
        if any(word in text for word in ['trump', 'biden', 'election', 'nba', 'nfl', 'bitcoin']):
            score += 15
        
        # 行动词 +10
        if any(word in text for word in ['bought', 'sold', 'entered', 'exited']):
            score += 10
        
        return min(score, 100)
    
    # ==========================================
    # 2. FiveThirtyEight 民调数据
    # ==========================================
    async def fetch_538_polls(self) -> List[Dict]:
        """
        获取 538 民调数据
        """
        try:
            url = self.config['fivethirtyeight']['url']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 过滤与 Polymarket 相关的民调
                        relevant_polls = []
                        
                        for poll in data:
                            # 只关注政治相关的民调
                            if any(keyword in str(poll).lower() for keyword in 
                                   ['trump', 'biden', 'election', '2024', 'president']):
                                
                                relevant_polls.append({
                                    'poll_id': poll.get('poll_id'),
                                    'pollster': poll.get('pollster'),
                                    'sponsors': poll.get('sponsors'),
                                    'state': poll.get('state'),
                                    'question': poll.get('question'),
                                    'subpopulation': poll.get('subpopulation'),
                                    'methodology': poll.get('methodology'),
                                    'population': poll.get('population'),
                                    'cycle': poll.get('cycle'),
                                    'results': poll.get('answers', [])
                                })
                        
                        logger.info(f"📊 获取到 {len(relevant_polls)} 个相关民调")
                        return relevant_polls
                    
        except Exception as e:
            logger.error(f"❌ 获取 538 数据失败: {e}")
        
        return []
    
    async def analyze_poll_market_divergence(self, polls: List[Dict]) -> List[Dict]:
        """
        分析民调与市场的偏差
        """
        divergences = []
        
        # 这里应该对比 Polymarket 价格
        # 简化版：标记可能有偏差的数据
        
        for poll in polls[:5]:  # 只分析前5个
            # 假设的逻辑
            if poll.get('state') == 'National':
                # 全国民调对比市场价格
                divergence = {
                    'poll': poll,
                    'market_price': None,  # 需要从 Polymarket 获取
                    'estimated_divergence': 'unknown',
                    'confidence': 70
                }
                divergences.append(divergence)
        
        return divergences
    
    # ==========================================
    # 3. ESPN 体育数据
    # ==========================================
    async def fetch_espn_injuries(self, sport: str = 'basketball/nba') -> List[Dict]:
        """
        获取 ESPN 伤病报告
        """
        try:
            url = f"{self.config['espn']['url']}/{sport}/injuries"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        injuries = data.get('injuries', [])
                        
                        logger.info(f"🏀 获取到 {len(injuries)} 条伤病信息")
                        return injuries
                    
        except Exception as e:
            logger.error(f"❌ 获取 ESPN 数据失败: {e}")
        
        return []
    
    async def fetch_espn_news(self, sport: str = 'basketball/nba') -> List[Dict]:
        """
        获取 ESPN 新闻
        """
        try:
            url = f"{self.config['espn']['url']}/{sport}/news"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        # 过滤重要新闻
                        important_news = []
                        for article in articles[:10]:
                            title = article.get('headline', '').lower()
                            
                            # 关键信息：伤病、交易、阵容
                            if any(keyword in title for keyword in 
                                   ['injury', 'out', 'trade', 'suspension', 'starting']):
                                important_news.append(article)
                        
                        logger.info(f"📰 获取到 {len(important_news)} 条重要新闻")
                        return important_news
                    
        except Exception as e:
            logger.error(f"❌ 获取 ESPN 新闻失败: {e}")
        
        return []
    
    # ==========================================
    # 4. 通知系统
    # ==========================================
    async def send_discord_notification(self, message: Dict):
        """
        发送 Discord 通知
        """
        if not self.config['discord']['enabled']:
            return
        
        try:
            webhook_url = self.config['discord']['webhook_url']
            
            payload = {
                "content": f"🚨 **交易信号 detected!**",
                "embeds": [{
                    "title": message.get('title', 'New Signal'),
                    "description": message.get('description', ''),
                    "color": 3447003,
                    "fields": [
                        {"name": "Source", "value": message.get('source', 'Unknown'), "inline": True},
                        {"name": "Confidence", "value": f"{message.get('confidence', 0)}/100", "inline": True},
                        {"name": "Time", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": False}
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("✅ Discord 通知已发送")
                    else:
                        logger.error(f"❌ Discord 通知失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ 发送 Discord 通知失败: {e}")
    
    async def send_telegram_notification(self, message: Dict):
        """
        发送 Telegram 通知
        """
        if not self.config['telegram']['enabled']:
            return
        
        try:
            bot_token = self.config['telegram']['bot_token']
            chat_id = self.config['telegram']['chat_id']
            
            text = f"""
🚨 <b>交易信号 detected!</b>

<b>{message.get('title', 'New Signal')}</b>

{message.get('description', '')}

Source: {message.get('source', 'Unknown')}
Confidence: {message.get('confidence', 0)}/100
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("✅ Telegram 通知已发送")
                    else:
                        logger.error(f"❌ Telegram 通知失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ 发送 Telegram 通知失败: {e}")
    
    # ==========================================
    # 主运行循环
    # ==========================================
    async def run(self):
        """
        主运行循环
        """
        logger.info("🚀 启动外部数据源集成系统")
        logger.info("=" * 60)
        
        while True:
            try:
                logger.info(f"\n📊 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 开始数据采集...")
                
                # 1. Twitter 监控
                if self.config['twitter']['enabled']:
                    tweets = await self.monitor_twitter_accounts()
                    logger.info(f"🐦 Twitter: 发现 {len(tweets)} 条相关推文")
                    
                    for tweet in tweets:
                        if tweet.get('confidence', 0) > 70:
                            await self.send_discord_notification({
                                'title': f"Twitter Signal from @{tweet['username']}",
                                'description': tweet.get('title', ''),
                                'source': 'Twitter',
                                'confidence': tweet.get('confidence', 0)
                            })
                
                # 2. 538 民调
                if self.config['fivethirtyeight']['enabled']:
                    polls = await self.fetch_538_polls()
                    divergences = await self.analyze_poll_market_divergence(polls)
                    logger.info(f"📊 538: 发现 {len(divergences)} 个民调偏差")
                
                # 3. ESPN 体育
                if self.config['espn']['enabled']:
                    for sport in self.config['espn']['sports']:
                        injuries = await self.fetch_espn_injuries(sport)
                        news = await self.fetch_espn_news(sport)
                        logger.info(f"🏀 ESPN ({sport}): {len(injuries)} 伤病, {len(news)} 新闻")
                
                logger.info(f"✅ 数据采集完成，等待 5 分钟...")
                await asyncio.sleep(300)  # 5分钟
                
            except Exception as e:
                logger.error(f"❌ 运行错误: {e}")
                await asyncio.sleep(60)

async def main():
    """主函数"""
    hub = DataIntegrationHub()
    await hub.run()

if __name__ == "__main__":
    asyncio.run(main())
