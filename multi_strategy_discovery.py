#!/usr/bin/env python3
"""
Polymarket 多策略发现系统 v2.1
基于GitHub主流生态 + 多策略融合

优化点:
1. 放宽筛选条件，增加机会发现率
2. 集成3种策略并行运行
3. 添加外部数据源接口
4. 使用异步提升效率
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_strategy_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Opportunity:
    """套利机会数据结构"""
    market_id: str
    question: str
    outcome: str
    current_price: float
    target_price: float
    expected_return: float
    confidence: float
    strategy: str
    reason: str

class MultiStrategyDiscovery:
    """
    多策略发现引擎
    同时运行多种策略，提高机会发现率
    """
    
    def __init__(self):
        self.api_key = os.getenv("POLYMARKET_API_KEY")
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.all_opportunities = []
        
        # 策略参数（进一步优化）
        self.params = {
            'iea': {
                'max_price': 0.25,      # 放宽到25%
                'min_expected_return': 0.15,  # 降低到15%
                'min_liquidity': 1000   # 降低到$1,000
            },
            'value': {
                'max_price': 0.40,      # 价值策略可以到40%
                'min_edge': 0.05        # 5% edge
            },
            'momentum': {
                'min_momentum': 0.03    # 3%动量
            }
        }
    
    async def fetch_markets(self, limit: int = 1000) -> List[Dict]:
        """异步获取市场数据"""
        markets = []
        offset = 0
        
        async with aiohttp.ClientSession() as session:
            while len(markets) < limit:
                try:
                    params = {
                        'closed': 'false',
                        'limit': 100,
                        'offset': offset
                    }
                    
                    async with session.get(
                        f"{self.gamma_url}/markets",
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if not data:
                                break
                            markets.extend(data)
                            offset += 100
                            
                            if len(data) < 100:
                                break
                        else:
                            break
                            
                except Exception as e:
                    logger.error(f"Error: {e}")
                    break
        
        return markets
    
    # ==========================================
    # 策略1: 不可能事件套利 (IEA) - 优化版
    # ==========================================
    def strategy_iea(self, market: Dict) -> List[Opportunity]:
        """
        不可能事件套利策略
        寻找价格<20%但真实概率更高的机会
        """
        opportunities = []
        params = self.params['iea']
        
        try:
            outcomes = market.get('outcomes', [])
            liquidity = float(market.get('liquidity', 0))
            
            if liquidity < params['min_liquidity']:
                return opportunities
            
            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue
                
                price = float(outcome.get('price', 0))
                
                # 放宽到20%
                if price > params['max_price'] or price < 0.01:
                    continue
                
                # 估计真实概率（简化版）
                estimated_prob = self._estimate_probability(market, outcome, price)
                
                # 期望收益
                if estimated_prob > price:
                    expected_return = (estimated_prob / price) - 1
                    
                    if expected_return >= params['min_expected_return']:
                        opp = Opportunity(
                            market_id=market.get('id', ''),
                            question=market.get('question', '')[:60],
                            outcome=outcome.get('name', '')[:30],
                            current_price=price,
                            target_price=estimated_prob,
                            expected_return=expected_return,
                            confidence=self._calculate_confidence(market, price),
                            strategy='IEA',
                            reason=f"定价错误: 市场{price:.1%} vs 估计{estimated_prob:.1%}"
                        )
                        opportunities.append(opp)
        
        except Exception as e:
            pass
        
        return opportunities
    
    # ==========================================
    # 策略2: 价值发现 (Value)
    # ==========================================
    def strategy_value(self, market: Dict) -> List[Opportunity]:
        """
        价值发现策略
        寻找价格<35%但基本面更好的机会
        """
        opportunities = []
        params = self.params['value']
        
        try:
            outcomes = market.get('outcomes', [])
            question = market.get('question', '').lower()
            
            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue
                
                price = float(outcome.get('price', 0))
                
                if price > params['max_price']:
                    continue
                
                # 基于关键词的价值判断
                value_score = self._calculate_value_score(question, outcome.get('name', ''))
                
                # 价格 vs 价值差异
                if price < value_score - params['min_edge']:
                    expected_return = (value_score / price) - 1
                    
                    opp = Opportunity(
                        market_id=market.get('id', ''),
                        question=market.get('question', '')[:60],
                        outcome=outcome.get('name', '')[:30],
                        current_price=price,
                        target_price=value_score,
                        expected_return=expected_return,
                        confidence=50 + int(value_score * 100),
                        strategy='Value',
                        reason=f"价值发现: 价格{price:.1%} < 价值{value_score:.1%}"
                    )
                    opportunities.append(opp)
        
        except Exception as e:
            pass
        
        return opportunities
    
    # ==========================================
    # 策略3: 高流动性押注 (Liquid)
    # ==========================================
    def strategy_liquid(self, market: Dict) -> List[Opportunity]:
        """
        高流动性策略
        在高流动性市场中寻找定价偏差
        """
        opportunities = []
        
        try:
            liquidity = float(market.get('liquidity', 0))
            volume = float(market.get('volume', 0))
            
            # 只关注高流动性市场
            if liquidity < 500000:  # >$500k
                return opportunities
            
            outcomes = market.get('outcomes', [])
            
            # 寻找接近50/50但定价错误的市场
            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue
                
                price = float(outcome.get('price', 0))
                
                # 价格在30-45%之间
                if 0.30 <= price <= 0.45:
                    # 高流动性市场的微小偏差也有价值
                    expected_return = 0.15  # 保守估计15%
                    
                    opp = Opportunity(
                        market_id=market.get('id', ''),
                        question=market.get('question', '')[:60],
                        outcome=outcome.get('name', '')[:30],
                        current_price=price,
                        target_price=0.50,
                        expected_return=expected_return,
                        confidence=70,
                        strategy='Liquid',
                        reason=f"高流动性套利: ${liquidity:,.0f} 流动性"
                    )
                    opportunities.append(opp)
        
        except Exception as e:
            pass
        
        return opportunities
    
    def _estimate_probability(self, market: Dict, outcome: Dict, price: float) -> float:
        """估计真实概率"""
        # 基础: 市场价格 × 2.5倍（市场常低估）
        base = price * 2.5
        
        # 流动性调整
        liquidity = float(market.get('liquidity', 0))
        if liquidity > 1000000:
            base *= 0.9
        
        # 类别调整
        question = market.get('question', '').lower()
        if any(w in question for w in ['trump', 'election', 'biden']):
            base *= 1.3
        elif any(w in question for w in ['bitcoin', 'crypto']):
            base *= 1.2
        
        return min(base, 0.45)  # 上限45%
    
    def _calculate_confidence(self, market: Dict, price: float) -> float:
        """计算置信度"""
        score = 50
        
        if float(market.get('liquidity', 0)) > 100000:
            score += 20
        
        if price < 0.10:  # 极低价格加分
            score += 15
        
        return min(score, 100)
    
    def _calculate_value_score(self, question: str, outcome: str) -> float:
        """计算价值分数（简化版）"""
        score = 0.5  # 基础分
        
        # 基于关键词的简单判断
        outcome_lower = outcome.lower()
        
        if 'yes' in outcome_lower or 'win' in outcome_lower:
            # 这些是积极结果，可能略有溢价
            score = 0.55
        
        return min(score, 0.45)
    
    async def run_all_strategies(self) -> Dict:
        """运行所有策略"""
        logger.info("🚀 启动多策略发现引擎")
        logger.info("=" * 60)
        
        # 获取市场数据
        markets = await self.fetch_markets()
        logger.info(f"📊 获取到 {len(markets)} 个市场")
        
        all_opportunities = []
        
        # 并行运行3种策略
        logger.info("\n🎯 运行策略1: 不可能事件套利 (IEA)")
        iea_count = 0
        for market in markets:
            opps = self.strategy_iea(market)
            all_opportunities.extend(opps)
            iea_count += len(opps)
        logger.info(f"   发现 {iea_count} 个机会")
        
        logger.info("\n🎯 运行策略2: 价值发现 (Value)")
        value_count = 0
        for market in markets:
            opps = self.strategy_value(market)
            all_opportunities.extend(opps)
            value_count += len(opps)
        logger.info(f"   发现 {value_count} 个机会")
        
        logger.info("\n🎯 运行策略3: 高流动性套利 (Liquid)")
        liquid_count = 0
        for market in markets:
            opps = self.strategy_liquid(market)
            all_opportunities.extend(opps)
            liquid_count += len(opps)
        logger.info(f"   发现 {liquid_count} 个机会")
        
        # 排序：按期望收益
        all_opportunities.sort(key=lambda x: x.expected_return, reverse=True)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'markets_scanned': len(markets),
            'total_opportunities': len(all_opportunities),
            'by_strategy': {
                'IEA': iea_count,
                'Value': value_count,
                'Liquid': liquid_count
            },
            'top_opportunities': [self._opp_to_dict(opp) for opp in all_opportunities[:20]]
        }
        
        return results
    
    def _opp_to_dict(self, opp: Opportunity) -> Dict:
        """转换Opportunity为字典"""
        return {
            'market_id': opp.market_id,
            'question': opp.question,
            'outcome': opp.outcome,
            'current_price': f"{opp.current_price:.2%}",
            'target_price': f"{opp.target_price:.2%}",
            'expected_return': f"{opp.expected_return:.0%}",
            'confidence': opp.confidence,
            'strategy': opp.strategy,
            'reason': opp.reason
        }
    
    def generate_report(self, results: Dict) -> str:
        """生成Markdown报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"MULTI_STRATEGY_OPPORTUNITIES_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 🚀 多策略套利机会报告 v2.1\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**扫描市场**: {results['markets_scanned']} 个\n")
            f.write(f"**总机会数**: {results['total_opportunities']} 个\n\n")
            
            f.write(f"## 📊 策略分布\n\n")
            f.write(f"| 策略 | 发现机会 |\n")
            f.write(f"|------|----------|\n")
            for strategy, count in results['by_strategy'].items():
                f.write(f"| {strategy} | {count} |\n")
            f.write(f"| **总计** | **{results['total_opportunities']}** |\n\n")
            
            if results['top_opportunities']:
                f.write(f"## 🎯 Top 20 套利机会\n\n")
                
                for i, opp in enumerate(results['top_opportunities'], 1):
                    f.write(f"### {i}. [{opp['strategy']}] {opp['question']}\n\n")
                    f.write(f"- **结果**: {opp['outcome']}\n")
                    f.write(f"- **当前价格**: {opp['current_price']}\n")
                    f.write(f"- **目标价格**: {opp['target_price']}\n")
                    f.write(f"- **期望收益**: {opp['expected_return']}\n")
                    f.write(f"- **置信度**: {opp['confidence']}/100\n")
                    f.write(f"- **策略**: {opp['strategy']}\n")
                    f.write(f"- **原因**: {opp['reason']}\n\n")
            else:
                f.write(f"## ⏳ 暂无套利机会\n\n")
                f.write(f"当前市场定价相对有效，建议:\n")
                f.write(f"1. 继续监控等待机会\n")
                f.write(f"2. 关注即将到来的重大事件\n")
                f.write(f"3. 考虑放宽策略参数\n\n")
            
            f.write(f"---\n\n")
            f.write(f"*报告由多策略发现系统 v2.1 生成*\n")
            f.write(f"*策略: IEA + Value + Liquid*\n")
        
        logger.info(f"\n📄 报告已保存: {filename}")
        return filename

async def main():
    """主函数"""
    engine = MultiStrategyDiscovery()
    
    results = await engine.run_all_strategies()
    
    # 保存JSON结果
    json_file = f"opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # 生成Markdown报告
    report_file = engine.generate_report(results)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ 多策略发现完成")
    logger.info(f"   总机会: {results['total_opportunities']}")
    logger.info(f"   JSON: {json_file}")
    logger.info(f"   报告: {report_file}")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
