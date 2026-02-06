#!/bin/bash
# Phase 3 实施脚本 - 多数据源融合
# 运行: bash phase3_implementation.sh

echo "=========================================="
echo "🔌 Phase 3 实施: 多数据源融合"
echo "=========================================="
echo ""

echo "📋 数据融合架构"
echo "------------------------------"
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│           数据融合中心 (Data Hub)        │"
echo "├─────────────────────────────────────────┤"
echo "│                                         │"
echo "│  Twitter API  ←──┐                     │"
echo "│  FiveThirtyEight ←─┼──→ 信号分析引擎    │"
echo "│  ESPN Sports    ←──┤    (置信度评分)    │"
echo "│  链上数据       ←──┘         ↓         │"
echo "│  新闻 RSS            ┌──────────────┐  │"
echo "│                      │ 交易信号输出  │  │"
echo "│                      └──────────────┘  │"
echo "│                                         │"
echo "└─────────────────────────────────────────┘"
echo ""

# 创建 Twitter API 集成模块
echo "📋 步骤 1: 创建 Twitter API 集成"
echo "------------------------------"

cat > twitter_api_integration.py << 'EOF'
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
EOF

echo "✅ Twitter API 集成模块已创建"
echo ""

# 创建 538 数据修复模块
echo "📋 步骤 2: 修复 FiveThirtyEight 数据获取"
echo "------------------------------"

cat > fivethirtyeight_integration.py << 'EOF'
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
EOF

echo "✅ 538 数据模块已创建"
echo ""

# 创建链上数据监控模块
echo "📋 步骤 3: 创建链上数据监控"
echo "------------------------------"

cat > onchain_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
链上数据监控 (Web3.py)
监控 Polygon 网络上的 Polymarket 活动
"""

import os
from datetime import datetime
from typing import Dict, List

try:
    from web3 import Web3
except ImportError:
    print("Installing web3...")
    os.system("pip install web3 -q")
    from web3 import Web3

class OnChainMonitor:
    """链上数据监控器"""
    
    def __init__(self):
        # Polygon RPC 节点
        self.rpc_urls = [
            "https://polygon-rpc.com",
            "https://rpc.ankr.com/polygon",
            "https://polygon.llamarpc.com"
        ]
        
        self.w3 = None
        self.connect()
        
        # Polymarket 相关合约地址
        self.contracts = {
            'ctf_exchange': '0x...',  # 需要实际地址
            'neg_risk_adapter': '0x...',
            'usdc': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
        }
    
    def connect(self):
        """连接 RPC 节点"""
        for url in self.rpc_urls:
            try:
                w3 = Web3(Web3.HTTPProvider(url))
                if w3.is_connected():
                    self.w3 = w3
                    print(f"✅ 已连接到 Polygon: {url}")
                    return True
            except Exception as e:
                print(f"❌ 连接失败 {url}: {e}")
                continue
        
        print("❌ 无法连接到任何 Polygon 节点")
        return False
    
    def get_usdc_transfers(self, hours: int = 1) -> List[Dict]:
        """获取 USDC 大额转账"""
        if not self.w3:
            return []
        
        # USDC Transfer 事件主题
        transfer_topic = self.w3.keccak(text="Transfer(address,address,uint256)").hex()
        
        try:
            # 获取最新区块
            latest = self.w3.eth.block_number
            blocks_per_hour = 1800  # ~2秒一个区块
            from_block = latest - (hours * blocks_per_hour)
            
            # 获取日志
            logs = self.w3.eth.get_logs({
                'fromBlock': from_block,
                'toBlock': 'latest',
                'address': self.contracts['usdc'],
                'topics': [transfer_topic]
            })
            
            transfers = []
            for log in logs:
                # 解析转账金额
                amount = int(log['data'], 16) / 1e6  # USDC 有 6 位小数
                
                if amount >= 10000:  # 只关注 >= $10,000
                    transfers.append({
                        'tx_hash': log['transactionHash'].hex(),
                        'amount': amount,
                        'block_number': log['blockNumber'],
                        'timestamp': datetime.now().isoformat()
                    })
            
            print(f"📊 发现 {len(transfers)} 个大额 USDC 转账 (>=$10K)")
            return transfers
            
        except Exception as e:
            print(f"❌ 获取转账失败: {e}")
            return []
    
    def get_block_timestamp(self, block_number: int) -> datetime:
        """获取区块时间戳"""
        if not self.w3:
            return datetime.now()
        
        try:
            block = self.w3.eth.get_block(block_number)
            return datetime.fromtimestamp(block['timestamp'])
        except:
            return datetime.now()
    
    def monitor(self):
        """监控链上活动"""
        print("🚀 启动链上数据监控")
        
        import time
        while True:
            try:
                # 获取大额转账
                transfers = self.get_usdc_transfers(hours=1)
                
                # 保存数据
                if transfers:
                    import json
                    with open('data/onchain_activity.json', 'w') as f:
                        json.dump({
                            'timestamp': datetime.now().isoformat(),
                            'transfers': transfers
                        }, f, indent=2)
                
                print(f"⏰ 等待 5 分钟...")
                time.sleep(300)
                
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                time.sleep(60)

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    
    monitor = OnChainMonitor()
    if monitor.w3:
        monitor.monitor()
EOF

echo "✅ 链上监控模块已创建"
echo ""

# 创建统一数据融合模块
echo "📋 步骤 4: 创建统一数据融合中心"
echo "------------------------------"

cat > unified_data_fusion.py << 'EOF'
#!/usr/bin/env python3
"""
统一数据融合中心
整合所有数据源，输出交易信号
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

class UnifiedDataFusion:
    """
    统一数据融合中心
    整合多个数据源，生成综合交易信号
    """
    
    def __init__(self):
        self.sources = {
            'twitter': {'weight': 0.3, 'signals': []},
            'fivethirtyeight': {'weight': 0.25, 'signals': []},
            'espn': {'weight': 0.2, 'signals': []},
            'onchain': {'weight': 0.15, 'signals': []},
            'news': {'weight': 0.1, 'signals': []}
        }
        
        self.fusion_threshold = 70  # 融合后置信度阈值
    
    def calculate_fusion_score(self, signals: List[Dict]) -> Dict:
        """
        计算融合后的综合评分
        
        加权平均算法:
        score = Σ(source_confidence × source_weight)
        """
        total_score = 0
        total_weight = 0
        
        details = {}
        
        for source, data in self.sources.items():
            weight = data['weight']
            signals = data['signals']
            
            if signals:
                # 取该源的最新信号
                latest = signals[-1]
                confidence = latest.get('confidence', 0)
                
                weighted_score = confidence * weight
                total_score += weighted_score
                total_weight += weight
                
                details[source] = {
                    'confidence': confidence,
                    'weight': weight,
                    'contribution': weighted_score
                }
        
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0
        
        return {
            'score': round(final_score, 2),
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_trading_signal(self, fusion_result: Dict) -> Dict:
        """
        根据融合结果生成交易信号
        """
        score = fusion_result['score']
        
        if score >= self.fusion_threshold:
            signal = {
                'action': 'TRADE',
                'direction': 'BUY' if score > 75 else 'HOLD',
                'confidence': score,
                'urgency': 'HIGH' if score > 85 else 'MEDIUM',
                'sources': fusion_result['details'],
                'timestamp': fusion_result['timestamp'],
                'market': self._infer_market(fusion_result)
            }
        else:
            signal = {
                'action': 'WAIT',
                'confidence': score,
                'reason': 'Confidence below threshold',
                'timestamp': fusion_result['timestamp']
            }
        
        return signal
    
    def _infer_market(self, fusion_result: Dict) -> str:
        """推断相关市场"""
        # 简化版：根据数据源推断
        details = fusion_result.get('details', {})
        
        if 'fivethirtyeight' in details:
            return 'US_ELECTION_2024'
        elif 'espn' in details:
            return 'SPORTS'
        else:
            return 'UNKNOWN'
    
    async def run(self):
        """主运行循环"""
        print("🚀 启动统一数据融合中心")
        print("=" * 60)
        
        while True:
            try:
                # 这里应该读取各个数据源的信号
                # 简化版示例
                
                fusion_result = self.calculate_fusion_score([])
                signal = self.generate_trading_signal(fusion_result)
                
                if signal['action'] == 'TRADE':
                    print(f"\n🚨 交易信号生成!")
                    print(f"   方向: {signal['direction']}")
                    print(f"   置信度: {signal['confidence']}/100")
                    print(f"   紧急度: {signal['urgency']}")
                    print(f"   市场: {signal['market']}")
                    
                    # 保存信号
                    self._save_signal(signal)
                else:
                    print(f"\n⏳ 等待中... 当前置信度: {signal['confidence']}/100")
                
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 下次检查...")
                await asyncio.sleep(300)  # 5分钟
                
            except Exception as e:
                print(f"❌ 运行错误: {e}")
                await asyncio.sleep(60)
    
    def _save_signal(self, signal: Dict):
        """保存信号到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"signals/fusion_signal_{timestamp}.json"
        
        import os
        os.makedirs('signals', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(signal, f, indent=2)
        
        print(f"   💾 信号已保存: {filename}")

async def main():
    """主函数"""
    fusion = UnifiedDataFusion()
    await fusion.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

echo "✅ 统一数据融合中心已创建"
echo ""

echo "=========================================="
echo "🔌 Phase 3 准备完成！"
echo "=========================================="
echo ""
echo "📦 已创建模块:"
echo "   - twitter_api_integration.py - Twitter API 集成"
echo "   - fivethirtyeight_integration.py - 538 民调数据"
echo "   - onchain_monitor.py - 链上数据监控"
echo "   - unified_data_fusion.py - 统一数据融合"
echo ""
echo "🚀 下一步行动:"
echo ""
echo "1. 设置 Twitter API 凭证:"
echo "   export TWITTER_BEARER_TOKEN='...'"
echo "   export TWITTER_API_KEY='...'"
echo "   export TWITTER_API_SECRET='...'"
echo ""
echo "2. 启动各个监控模块:"
echo "   python3 twitter_api_integration.py &"
echo "   python3 fivethirtyeight_integration.py &"
echo "   python3 onchain_monitor.py &"
echo ""
echo "3. 启动融合中心:"
echo "   python3 unified_data_fusion.py"
echo ""
echo "📚 依赖安装:"
echo "   pip install tweepy web3 aiohttp"
echo ""
echo "🎯 目标: 建立信息优势，提前市场 5+ 分钟"
echo "=========================================="
