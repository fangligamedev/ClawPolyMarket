#!/usr/bin/env python3
"""
Polymarket 高级套利扫描器
寻找"不可能事件"套利机会（基于 browomo 策略）
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests

class ArbitrageScanner:
    """
    套利机会扫描器
    """
    
    def __init__(self):
        self.api_key = os.getenv("POLYMARKET_API_KEY")
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.results = []
        self.opportunities = []
        
    def fetch_all_markets(self, limit: int = 1000) -> List[Dict]:
        """
        获取所有活跃市场
        """
        markets = []
        offset = 0
        
        print("🔍 正在扫描 Polymarket 所有市场...")
        
        while True:
            try:
                url = f"{self.gamma_url}/markets"
                params = {
                    "closed": "false",
                    "archived": "false",
                    "limit": limit,
                    "offset": offset
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                markets.extend(data)
                offset += limit
                
                print(f"   已获取 {len(markets)} 个市场...")
                
                if len(data) < limit:
                    break
                    
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ 获取市场失败: {e}")
                break
        
        print(f"✅ 共获取 {len(markets)} 个活跃市场")
        return markets
    
    def analyze_opportunity(self, market: Dict) -> Optional[Dict]:
        """
        分析单个市场的套利机会
        策略：寻找高赔率但有一定真实概率的"不可能事件"
        """
        try:
            question = market.get("question", "")
            outcomes = market.get("outcomes", [])
            
            if not outcomes or len(outcomes) < 2:
                return None
            
            opportunities = []
            
            for outcome in outcomes:
                name = outcome.get("name", "")
                price = float(outcome.get("price", 0))
                
                # 策略1: "不可能事件" - 价格 < 0.05 (95%+ 认为不会发生)
                if 0.01 <= price <= 0.10:
                    # 估计真实概率是价格的 2-5 倍
                    estimated_prob = min(price * 3.5, 0.45)
                    
                    # 计算期望收益
                    if price > 0:
                        odds = (1 - price) / price
                        expected_return = estimated_prob * odds - (1 - estimated_prob)
                        
                        if expected_return > 0.5:  # 50%+ 期望收益
                            opportunities.append({
                                "type": "impossible_event",
                                "outcome": name,
                                "market_price": price,
                                "implied_prob": price * 100,
                                "estimated_real_prob": estimated_prob * 100,
                                "odds": f"{odds:.1f}:1",
                                "expected_return": expected_return * 100,
                                "potential_profit": f"{(expected_return * 100):.0f}%"
                            })
                
                # 策略2: 高赔率事件 - 价格 0.45-0.55（接近50/50但市场定价错误）
                elif 0.45 <= price <= 0.55:
                    # 检查是否存在明显不对称信息
                    volume = float(market.get("volume", 0))
                    if volume > 100000:  # 高流动性市场
                        opportunities.append({
                            "type": "mispricing",
                            "outcome": name,
                            "market_price": price,
                            "implied_prob": price * 100,
                            "volume": volume,
                            "note": "高流动性但定价接近50/50，可能存在信息不对称"
                        })
            
            if opportunities:
                return {
                    "market_id": market.get("id", ""),
                    "question": question,
                    "volume": float(market.get("volume", 0)),
                    "liquidity": float(market.get("liquidity", 0)),
                    "end_date": market.get("endDate", ""),
                    "opportunities": opportunities,
                    "opportunity_count": len(opportunities),
                    "scan_time": datetime.now().isoformat()
                }
                
        except Exception as e:
            pass
        
        return None
    
    def scan_for_arbitrage(self) -> List[Dict]:
        """
        扫描所有市场寻找套利机会
        """
        markets = self.fetch_all_markets()
        opportunities = []
        
        print(f"\n🎯 正在分析 {len(markets)} 个市场寻找套利机会...")
        
        for i, market in enumerate(markets):
            if i % 100 == 0:
                print(f"   已分析 {i}/{len(markets)} 个市场...")
            
            result = self.analyze_opportunity(market)
            if result:
                opportunities.append(result)
                print(f"   ✅ 发现机会: {result['question'][:40]}...")
        
        # 按机会数量排序
        opportunities.sort(key=lambda x: x["opportunity_count"], reverse=True)
        
        return opportunities
    
    def save_results(self, opportunities: List[Dict]):
        """
        保存扫描结果
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存 JSON
        json_file = f"arbitrage_opportunities_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scan_time": datetime.now().isoformat(),
                "total_opportunities": len(opportunities),
                "opportunities": opportunities
            }, f, indent=2, ensure_ascii=False)
        
        # 保存 Markdown 报告
        md_file = f"arbitrage_report_{timestamp}.md"
        self.generate_markdown_report(opportunities, md_file)
        
        print(f"\n💾 结果已保存:")
        print(f"   JSON: {json_file}")
        print(f"   报告: {md_file}")
        
        return json_file, md_file
    
    def generate_markdown_report(self, opportunities: List[Dict], filename: str):
        """
        生成 Markdown 格式报告
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 🎯 Polymarket 套利机会扫描报告\n\n")
            f.write(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**发现机会**: {len(opportunities)} 个\n")
            f.write(f"**扫描市场**: 1000+ 个活跃市场\n\n")
            f.write(f"---\n\n")
            
            if not opportunities:
                f.write("❌ 未发现明显的套利机会\n")
                return
            
            f.write(f"## 📊 机会概览\n\n")
            f.write(f"| 排名 | 市场 | 类型 | 预期收益 | 流动性 |\n")
            f.write(f"|------|------|------|----------|--------|\n")
            
            for i, opp in enumerate(opportunities[:20], 1):
                question = opp['question'][:40] + "..."
                types = ", ".join([o['type'] for o in opp['opportunities']])
                returns = max([o.get('expected_return', 0) for o in opp['opportunities']])
                liquidity = f"${opp['liquidity']:,.0f}" if opp['liquidity'] > 0 else "N/A"
                f.write(f"| {i} | {question} | {types} | {returns:.0f}% | {liquidity} |\n")
            
            f.write(f"\n## 🔍 详细分析\n\n")
            
            for i, opp in enumerate(opportunities[:10], 1):
                f.write(f"### {i}. {opp['question']}\n\n")
                f.write(f"- **市场ID**: `{opp['market_id']}`\n")
                f.write(f"- **交易量**: ${opp['volume']:,.2f}\n")
                f.write(f"- **流动性**: ${opp['liquidity']:,.2f}\n")
                f.write(f"- **结束日期**: {opp['end_date']}\n\n")
                
                f.write(f"**套利机会**:\n\n")
                for detail in opp['opportunities']:
                    f.write(f"- **类型**: {detail['type']}\n")
                    f.write(f"  - **结果**: {detail['outcome']}\n")
                    if 'market_price' in detail:
                        f.write(f"  - **市场价格**: {detail['market_price']:.4f} ({detail['implied_prob']:.1f}%)\n")
                    if 'estimated_real_prob' in detail:
                        f.write(f"  - **估计真实概率**: {detail['estimated_real_prob']:.1f}%\n")
                    if 'odds' in detail:
                        f.write(f"  - **赔率**: {detail['odds']}\n")
                    if 'expected_return' in detail:
                        f.write(f"  - **期望收益**: {detail['expected_return']:.1f}%\n")
                    if 'note' in detail:
                        f.write(f"  - **备注**: {detail['note']}\n")
                    f.write(f"\n")
                
                f.write(f"---\n\n")
            
            f.write(f"## 💡 策略建议\n\n")
            f.write(f"基于扫描结果，建议关注以下策略:\n\n")
            f.write(f'1. **"不可能事件"策略**: 寻找价格 < 10% 但有一定真实概率的机会\n')
            f.write(f"2. **信息套利**: 关注高流动性但定价接近50/50的市场\n")
            f.write(f"3. **分散投资**: 小资金分散押注多个机会\n")
            f.write(f"4. **长期持有**: 等待事件结果，不频繁交易\n\n")
            
            f.write(f"## ⚠️ 风险提示\n\n")
            f.write(f"- 以上分析基于算法估计，真实概率可能不同\n")
            f.write(f"- 预测市场存在不确定性\n")
            f.write(f"- 建议只用小额资金测试\n")
            f.write(f"- 过往表现不代表未来收益\n")

def main():
    """
    主函数
    """
    print("🚀 Polymarket 高级套利扫描器")
    print("=" * 70)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("策略: 寻找'不可能事件'中的定价错误")
    print("=" * 70)
    print()
    
    scanner = ArbitrageScanner()
    
    # 执行扫描
    opportunities = scanner.scan_for_arbitrage()
    
    # 显示结果
    print("\n" + "=" * 70)
    print("📊 扫描结果")
    print("=" * 70)
    print(f"发现 {len(opportunities)} 个潜在套利机会\n")
    
    if opportunities:
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"\n{i}. {opp['question']}")
            print(f"   机会数: {opp['opportunity_count']}")
            for detail in opp['opportunities']:
                if 'expected_return' in detail:
                    print(f"   💰 期望收益: {detail['expected_return']:.0f}%")
    else:
        print("未发现明显套利机会")
    
    # 保存结果
    json_file, md_file = scanner.save_results(opportunities)
    
    print("\n" + "=" * 70)
    print("✅ 扫描完成！")
    print(f"下次扫描建议: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
