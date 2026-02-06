#!/usr/bin/env python3
"""
Polymarket Arbitrage Scanner
基于 browomo 策略：寻找"不可能事件"套利机会
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

class PolymarketScanner:
    def __init__(self):
        # Polymarket 使用 Gamma 的 API
        self.base_url = "https://gamma-api.polymarket.com"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PolymarketScanner/1.0",
            "Origin": "https://polymarket.com"
        }
        self.results = []
        
    def fetch_all_markets(self, limit: int = 100) -> List[Dict]:
        """
        获取所有活跃市场
        """
        markets = []
        offset = 0
        
        print("🔍 正在扫描 Polymarket 市场...")
        
        while True:
            try:
                # Gamma API 使用查询参数
                url = f"{self.base_url}/markets"
                params = {
                    "closed": "false",
                    "archived": "false",
                    "limit": limit,
                    "offset": offset
                }
                
                response = requests.get(url, params=params, headers=self.headers, timeout=30)
                
                if response.status_code != 200:
                    print(f"⚠️ API 返回状态码: {response.status_code}")
                    print(f"   尝试备用方案...")
                    # 尝试备用 API
                    url = "https://strapi-mmc.polymarket.com/markets"
                    response = requests.get(url, params={"_limit": limit, "_start": offset}, 
                                          headers=self.headers, timeout=30)
                
                response.raise_for_status()
                
                data = response.json()
                if isinstance(data, dict):
                    data = data.get("data", data.get("markets", []))
                
                if not data or len(data) == 0:
                    break
                    
                markets.extend(data)
                offset += limit
                
                print(f"   已获取 {len(markets)} 个市场...")
                
                # 限速
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ 获取市场失败: {e}")
                print(f"   提示: Polymarket API 可能需要认证或有访问限制")
                break
                
        print(f"✅ 共获取 {len(markets)} 个活跃市场")
        return markets
    
    def calculate_ev(self, probability: float, odds: float) -> float:
        """
        计算期望值 (Expected Value)
        EV = (胜率 × 收益) - (败率 × 损失)
        """
        # 假设赔率为 odds:1，押注 1 单位
        win_amount = odds
        loss_amount = 1
        
        ev = (probability * win_amount) - ((1 - probability) * loss_amount)
        return ev
    
    def analyze_market(self, market: Dict) -> Optional[Dict]:
        """
        分析单个市场，寻找套利机会
        策略：寻找高赔率（>90% 不会发生）但有一定真实概率的机会
        """
        try:
            market_id = market.get("id", "unknown")
            question = market.get("question", "Unknown")
            outcomes = market.get("outcomes", "")
            
            # 获取最佳报价
            book = market.get("book", {})
            if not book:
                return None
                
            # 分析每个 outcome
            opportunities = []
            
            for outcome_data in book.get("bids", []):
                outcome = outcome_data.get("outcome", "")
                price = float(outcome_data.get("price", 0))
                size = float(outcome_data.get("size", 0))
                
                # 价格范围 0-1，表示概率
                # 价格 < 0.1 表示 "不太可能"（>90% 不会发生）
                if price < 0.1 and price > 0.01:  # 1% < 概率 < 10%
                    # 赔率 = 1 / 价格
                    odds = 1 / price if price > 0 else 0
                    
                    # 假设真实概率是价格的 2-5 倍（被低估）
                    estimated_real_prob = min(price * 3, 0.5)  # 最多 50%
                    
                    # 计算 EV
                    ev = self.calculate_ev(estimated_real_prob, odds)
                    
                    if ev > 0:  # 正期望值
                        opportunities.append({
                            "outcome": outcome,
                            "market_price": price,
                            "implied_probability": price * 100,
                            "estimated_real_probability": estimated_real_prob * 100,
                            "odds": f"{odds:.1f}:1",
                            "expected_value": ev,
                            "potential_return": odds,
                            "liquidity": size
                        })
            
            if opportunities:
                # 按 EV 排序
                opportunities.sort(key=lambda x: x["expected_value"], reverse=True)
                
                return {
                    "market_id": market_id,
                    "question": question,
                    "opportunities": opportunities[:3],  # 取前 3 个最佳机会
                    "best_ev": opportunities[0]["expected_value"],
                    "scan_time": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"⚠️ 分析市场 {market.get('id', 'unknown')} 时出错: {e}")
            
        return None
    
    def scan_for_arbitrage(self, min_ev: float = 0.1) -> List[Dict]:
        """
        扫描所有市场，寻找套利机会
        """
        markets = self.fetch_all_markets()
        opportunities = []
        
        print(f"\n🎯 正在分析 {len(markets)} 个市场寻找套利机会...")
        print(f"   筛选条件: EV > {min_ev}\n")
        
        for i, market in enumerate(markets):
            if i % 10 == 0:
                print(f"   已分析 {i}/{len(markets)} 个市场...")
            
            result = self.analyze_market(market)
            if result and result["best_ev"] > min_ev:
                opportunities.append(result)
                print(f"   ✅ 发现机会: {result['question'][:50]}... EV: {result['best_ev']:.2f}")
            
            # 限速
            time.sleep(0.1)
        
        # 按 EV 排序
        opportunities.sort(key=lambda x: x["best_ev"], reverse=True)
        
        return opportunities
    
    def save_results(self, opportunities: List[Dict], filename: Optional[str] = None):
        """
        保存结果到 JSON 文件
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"polymarket_arbitrage_{timestamp}.json"
        
        output = {
            "scan_time": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "opportunities": opportunities
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存到: {filename}")
        return filename
    
    def print_summary(self, opportunities: List[Dict]):
        """
        打印结果摘要
        """
        print("\n" + "="*80)
        print("🎯 POLYMARKET 套利机会扫描结果")
        print("="*80)
        print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"发现机会: {len(opportunities)} 个\n")
        
        if not opportunities:
            print("❌ 未发现符合条件的套利机会")
            print("   建议: 放宽筛选条件或稍后再试")
            return
        
        for i, opp in enumerate(opportunities[:10], 1):  # 显示前 10 个
            print(f"\n{'─'*80}")
            print(f"📊 排名 #{i}")
            print(f"📝 市场: {opp['question']}")
            print(f"🔗 ID: {opp['market_id']}")
            print(f"📈 最佳 EV: {opp['best_ev']:.4f}")
            print("\n   详细机会:")
            
            for detail in opp['opportunities']:
                print(f"   • 结果: {detail['outcome']}")
                print(f"     市场价格: {detail['market_price']:.4f} ({detail['implied_probability']:.1f}%)")
                print(f"     估计真实概率: {detail['estimated_real_probability']:.1f}%")
                print(f"     赔率: {detail['odds']}")
                print(f"     期望值 (EV): {detail['expected_value']:.4f}")
                print(f"     潜在回报: {detail['potential_return']:.2f}x")
                print(f"     流动性: {detail['liquidity']:.2f}")
                print()
        
        print("="*80)
        print("⚠️ 风险提示:")
        print("   • 以上分析基于估计概率，实际结果可能不同")
        print("   • Polymarket 交易存在风险，请谨慎投资")
        print("   • 建议先用小资金测试策略")
        print("="*80)

def main():
    """
    主函数
    """
    print("🚀 Polymarket 套利扫描器")
    print("策略：寻找'不可能事件'中的定价错误\n")
    
    scanner = PolymarketScanner()
    
    # 扫描套利机会（EV > 0.1）
    opportunities = scanner.scan_for_arbitrage(min_ev=0.1)
    
    # 打印摘要
    scanner.print_summary(opportunities)
    
    # 保存结果
    if opportunities:
        filename = scanner.save_results(opportunities)
        print(f"\n📄 详细结果文件: {filename}")
    
    print("\n✅ 扫描完成！")

if __name__ == "__main__":
    main()
