#!/usr/bin/env python3
"""
Polymarket 实时市场监控器
监控特定市场和整体市场动态
"""

import os
import json
import time
from datetime import datetime
import requests

class MarketMonitor:
    """
    市场监控系统
    """
    
    def __init__(self):
        self.api_key = os.getenv("POLYMARKET_API_KEY")
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.watchlist = [
            "Will Trump",
            "Bitcoin",
            "Ethereum",
            "NBA",
            "NFL",
            "Election"
        ]
        self.history_file = "market_history.json"
        
    def fetch_market_by_keyword(self, keyword: str) -> list:
        """
        根据关键词获取市场
        """
        try:
            url = f"{self.gamma_url}/markets"
            params = {
                "closed": "false",
                "active": "true",
                "limit": 50
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            markets = response.json()
            # 过滤包含关键词的市场
            filtered = [
                m for m in markets 
                if keyword.lower() in m.get("question", "").lower()
            ]
            
            return filtered[:10]  # 返回前10个
            
        except Exception as e:
            print(f"❌ 获取市场失败: {e}")
            return []
    
    def fetch_trending_markets(self) -> list:
        """
        获取热门市场
        """
        try:
            url = f"{self.gamma_url}/markets"
            params = {
                "closed": "false",
                "limit": 20,
                "order": "volume",  # 按交易量排序
                "sort": "desc"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ 获取热门市场失败: {e}")
            return []
    
    def analyze_market(self, market: dict) -> dict:
        """
        分析单个市场
        """
        outcomes = market.get("outcomes", [])
        # 处理不同格式的outcomes
        if outcomes and isinstance(outcomes[0], dict):
            outcomes_data = [
                {
                    "name": o.get("name", "N/A"),
                    "price": float(o.get("price", 0)),
                    "probability": float(o.get("price", 0)) * 100
                }
                for o in outcomes
            ]
        else:
            # outcomes 可能是字符串列表
            outcomes_data = [{"name": str(o), "price": 0.5, "probability": 50} for o in outcomes]
        
        return {
            "id": market.get("id"),
            "question": market.get("question"),
            "volume": float(market.get("volume", 0)),
            "liquidity": float(market.get("liquidity", 0)),
            "outcomes": outcomes_data,
            "end_date": market.get("endDate"),
            "category": market.get("category"),
            "timestamp": datetime.now().isoformat()
        }
    
    def save_snapshot(self, data: dict):
        """
        保存市场快照
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"market_snapshot_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def generate_markdown_report(self, trending: list, watchlist_data: dict) -> str:
        """
        生成 Markdown 监控报告
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"market_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 Polymarket 市场监控报告\n\n")
            f.write(f"**生成时间**: {timestamp}\n")
            f.write(f"**监控周期**: 实时\n\n")
            f.write(f"---\n\n")
            
            # 热门市场
            f.write(f"## 🔥 热门市场（按交易量）\n\n")
            f.write(f"| 排名 | 市场 | 交易量 | 主要结果 | 概率 |\n")
            f.write(f"|------|------|--------|----------|------|\n")
            
            for i, market in enumerate(trending[:10], 1):
                question = market.get("question", "")[:40] + "..."
                volume = f"${float(market.get('volume', 0)):,.0f}"
                
                outcomes = market.get("outcomes", [])
                if outcomes:
                    main_outcome = outcomes[0]
                    if isinstance(main_outcome, dict):
                        main_name = main_outcome.get("name", "N/A")[:15]
                        main_prob = f"{float(main_outcome.get('price', 0)) * 100:.1f}%"
                    else:
                        main_name = str(main_outcome)[:15]
                        main_prob = "N/A"
                else:
                    main_name = "N/A"
                    main_prob = "N/A"
                
                f.write(f"| {i} | {question} | {volume} | {main_name} | {main_prob} |\n")
            
            f.write(f"\n## 👀 关注列表监控\n\n")
            
            for keyword, markets in watchlist_data.items():
                f.write(f"### {keyword}\n\n")
                
                if markets:
                    for market in markets[:5]:
                        question = market.get("question", "")
                        f.write(f"- **{question}**\n")
                        
                        for outcome in market.get("outcomes", [])[:2]:
                            if isinstance(outcome, dict):
                                name = outcome.get("name", "")
                                price = float(outcome.get("price", 0))
                                prob = price * 100
                                f.write(f"  - {name}: {prob:.1f}%\n")
                            else:
                                f.write(f"  - {outcome}\n")
                        f.write(f"\n")
                else:
                    f.write(f"*暂无活跃市场*\n\n")
            
            f.write(f"\n## 📈 市场统计\n\n")
            total_volume = sum(float(m.get("volume", 0)) for m in trending)
            f.write(f"- **监控市场总数**: {len(trending)}\n")
            f.write(f"- **总交易量**: ${total_volume:,.2f}\n")
            f.write(f"- **关注关键词**: {', '.join(self.watchlist)}\n\n")
            
            f.write(f"---\n\n")
            f.write(f"*下次更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        return filename
    
    def run_monitor(self):
        """
        运行监控
        """
        print("📊 Polymarket 实时市场监控")
        print("=" * 70)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
        
        # 获取热门市场
        print("🔥 正在获取热门市场...")
        trending = self.fetch_trending_markets()
        print(f"✅ 获取到 {len(trending)} 个热门市场\n")
        
        # 获取关注列表
        print("👀 正在监控关注列表...")
        watchlist_data = {}
        for keyword in self.watchlist:
            markets = self.fetch_market_by_keyword(keyword)
            watchlist_data[keyword] = markets
            print(f"   {keyword}: {len(markets)} 个相关市场")
        
        print()
        
        # 保存数据
        snapshot_data = {
            "timestamp": datetime.now().isoformat(),
            "trending_markets": [self.analyze_market(m) for m in trending[:20]],
            "watchlist": {
                k: [self.analyze_market(m) for m in v[:5]]
                for k, v in watchlist_data.items()
            }
        }
        
        # 保存快照
        snapshot_file = self.save_snapshot(snapshot_data)
        print(f"💾 数据快照已保存: {snapshot_file}")
        
        # 生成报告
        report_file = self.generate_markdown_report(trending, watchlist_data)
        print(f"📝 监控报告已生成: {report_file}")
        
        # 显示摘要
        print("\n" + "=" * 70)
        print("📈 监控摘要")
        print("=" * 70)
        print(f"热门市场数: {len(trending)}")
        print(f"关注关键词: {len(self.watchlist)}")
        print(f"数据文件: {snapshot_file}")
        print(f"报告文件: {report_file}")
        print("=" * 70)

def main():
    monitor = MarketMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()
