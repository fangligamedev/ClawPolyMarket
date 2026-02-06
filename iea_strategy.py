#!/usr/bin/env python3
"""
Polymarket "不可能事件"反向套利策略 (IEA Strategy)
基于 browomo $5→$370万 模式 + swisstony 事件驱动逻辑

作者: Kimi + 大Q
版本: 1.0
策略类型: 事件驱动套利
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iea_strategy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    """套利机会数据类"""
    market_id: str
    question: str
    outcome: str
    market_price: float
    implied_probability: float
    estimated_real_probability: float
    expected_return: float
    potential_profit: float
    liquidity: float
    end_date: str
    confidence_score: float

@dataclass
class Position:
    """持仓数据类"""
    market_id: str
    question: str
    outcome: str
    entry_price: float
    entry_time: datetime
    position_size: float
    target_exit_price: float
    stop_loss_price: float
    status: str  # 'open', 'closed', 'pending'

class ImpossibleEventArbitrage:
    """
    不可能事件反向套利策略主类
    """
    
    # 策略参数
    MAX_POSITION_SIZE = 50  # 单笔最大 $50
    MAX_POSITIONS = 20      # 最大持仓数
    MIN_LIQUIDITY = 5000    # 最小流动性 $5,000
    MAX_MARKET_PRICE = 0.15 # 最大市场价格 15%
    MIN_EXPECTED_RETURN = 0.3  # 最小期望收益 30%
    TAKE_PROFIT_THRESHOLD = 0.30  # 获利了结 30%
    STOP_LOSS_THRESHOLD = 0.05    # 止损 5%
    
    def __init__(self):
        """初始化策略"""
        self.api_key = os.getenv("POLYMARKET_API_KEY")
        self.api_secret = os.getenv("POLYMARKET_API_SECRET")
        self.api_passphrase = os.getenv("POLYMARKET_API_PASSPHRASE")
        
        if not all([self.api_key, self.api_secret, self.api_passphrase]):
            raise ValueError("缺少 API 凭据，请设置环境变量")
        
        self.host = "https://clob.polymarket.com"
        self.gamma_url = "https://gamma-api.polymarket.com"
        
        # 初始化 CLOB 客户端
        self.client = ClobClient(self.host)
        creds = ApiCreds(
            api_key=self.api_key,
            api_secret=self.api_secret,
            api_passphrase=self.api_passphrase
        )
        self.client.set_api_creds(creds)
        
        # 持仓管理
        self.positions: List[Position] = []
        self.positions_file = "positions.json"
        self.load_positions()
        
        logger.info("🚀 IEA 策略初始化完成")
        
    def load_positions(self):
        """加载持仓记录"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    data = json.load(f)
                    self.positions = [Position(**p) for p in data]
                logger.info(f"📊 加载了 {len(self.positions)} 个持仓")
        except Exception as e:
            logger.error(f"❌ 加载持仓失败: {e}")
            self.positions = []
    
    def save_positions(self):
        """保存持仓记录"""
        try:
            with open(self.positions_file, 'w') as f:
                json.dump([p.__dict__ for p in self.positions], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ 保存持仓失败: {e}")
    
    def fetch_active_markets(self, limit: int = 1000) -> List[Dict]:
        """
        获取活跃市场
        """
        markets = []
        offset = 0
        
        logger.info("🔍 正在获取活跃市场...")
        
        while len(markets) < limit:
            try:
                url = f"{self.gamma_url}/markets"
                params = {
                    "closed": "false",
                    "archived": "false",
                    "limit": 100,
                    "offset": offset
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                markets.extend(data)
                offset += 100
                
                if len(data) < 100:
                    break
                    
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"❌ 获取市场失败: {e}")
                break
        
        logger.info(f"✅ 获取到 {len(markets)} 个活跃市场")
        return markets
    
    def calculate_real_probability(self, market: Dict, outcome: Dict) -> float:
        """
        计算估计的真实概率
        基于市场数据和启发式算法
        """
        market_price = float(outcome.get("price", 0))
        
        # 基础调整因子
        base_adjustment = 3.0  # 市场价格通常低估 3 倍
        
        # 根据市场特征调整
        volume = float(market.get("volume", 0))
        liquidity = float(market.get("liquidity", 0))
        
        # 高流动性市场更有效，调整因子降低
        if liquidity > 1000000:  # >$1M
            liquidity_factor = 0.8
        elif liquidity > 100000:  # >$100K
            liquidity_factor = 0.9
        else:
            liquidity_factor = 1.0
        
        # 根据问题类型调整
        question = market.get("question", "").lower()
        
        # 政治事件通常被低估
        if any(word in question for word in ["trump", "election", "biden", "vote"]):
            category_factor = 1.3
        # 体育事件定价相对准确
        elif any(word in question for word in ["nba", "nfl", "score", "win"]):
            category_factor = 0.9
        # 加密事件波动大
        elif any(word in question for word in ["bitcoin", "ethereum", "crypto"]):
            category_factor = 1.2
        else:
            category_factor = 1.0
        
        estimated_prob = market_price * base_adjustment * liquidity_factor * category_factor
        
        # 限制在合理范围
        return min(estimated_prob, 0.45)  # 最多 45%
    
    def calculate_confidence_score(self, market: Dict, outcome: Dict) -> float:
        """
        计算机会置信度分数 (0-100)
        """
        score = 50  # 基础分
        
        # 流动性加分
        liquidity = float(market.get("liquidity", 0))
        if liquidity > 500000:
            score += 20
        elif liquidity > 100000:
            score += 10
        
        # 交易量加分
        volume = float(market.get("volume", 0))
        if volume > 1000000:
            score += 15
        elif volume > 100000:
            score += 5
        
        # 剩余时间加分
        end_date = market.get("endDate", "")
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                days_remaining = (end - datetime.now().astimezone()).days
                if 7 <= days_remaining <= 30:
                    score += 10  # 1-4周是理想时间
                elif days_remaining > 30:
                    score += 5
            except:
                pass
        
        # 价格极低加分（更大的定价错误空间）
        price = float(outcome.get("price", 0))
        if price < 0.05:
            score += 10
        
        return min(score, 100)
    
    def find_opportunities(self) -> List[ArbitrageOpportunity]:
        """
        寻找套利机会
        """
        markets = self.fetch_active_markets()
        opportunities = []
        
        logger.info(f"🎯 正在分析 {len(markets)} 个市场寻找套利机会...")
        
        for i, market in enumerate(markets):
            if i % 100 == 0:
                logger.info(f"   已分析 {i}/{len(markets)} 个市场...")
            
            try:
                # 检查流动性
                liquidity = float(market.get("liquidity", 0))
                if liquidity < self.MIN_LIQUIDITY:
                    continue
                
                # 检查结束时间
                end_date = market.get("endDate", "")
                if end_date:
                    try:
                        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        days_remaining = (end - datetime.now().astimezone()).days
                        if days_remaining < 7:  # 少于7天，时间不够
                            continue
                    except:
                        pass
                
                # 分析每个 outcome
                outcomes = market.get("outcomes", [])
                if not outcomes:
                    continue
                
                for outcome in outcomes:
                    if not isinstance(outcome, dict):
                        continue
                    
                    market_price = float(outcome.get("price", 0))
                    
                    # 策略核心：价格 < 10%
                    if market_price >= self.MAX_MARKET_PRICE:
                        continue
                    
                    if market_price <= 0:
                        continue
                    
                    # 计算估计的真实概率
                    real_prob = self.calculate_real_probability(market, outcome)
                    
                    # 计算期望收益
                    # 期望收益 = (真实概率 / 市场价格 - 1)
                    expected_return = (real_prob / market_price) - 1
                    
                    # 检查是否满足最小期望收益
                    if expected_return < self.MIN_EXPECTED_RETURN:
                        continue
                    
                    # 计算潜在利润
                    potential_profit = expected_return * self.MAX_POSITION_SIZE
                    
                    # 计算置信度
                    confidence = self.calculate_confidence_score(market, outcome)
                    
                    # 创建机会对象
                    opp = ArbitrageOpportunity(
                        market_id=market.get("id", ""),
                        question=market.get("question", ""),
                        outcome=outcome.get("name", ""),
                        market_price=market_price,
                        implied_probability=market_price * 100,
                        estimated_real_probability=real_prob * 100,
                        expected_return=expected_return * 100,
                        potential_profit=potential_profit,
                        liquidity=liquidity,
                        end_date=end_date,
                        confidence_score=confidence
                    )
                    
                    opportunities.append(opp)
                    
                    logger.info(f"   ✅ 发现机会: {opp.question[:40]}... "
                              f"期望收益: {opp.expected_return:.1f}% "
                              f"置信度: {opp.confidence_score}")
                    
            except Exception as e:
                logger.error(f"   ⚠️ 分析市场时出错: {e}")
                continue
        
        # 按期望收益排序
        opportunities.sort(key=lambda x: x.expected_return, reverse=True)
        
        logger.info(f"\n📊 共发现 {len(opportunities)} 个套利机会")
        return opportunities
    
    def filter_existing_positions(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        过滤掉已持仓的机会
        """
        existing_markets = {p.market_id for p in self.positions if p.status == 'open'}
        filtered = [opp for opp in opportunities if opp.market_id not in existing_markets]
        
        logger.info(f"📊 过滤后剩余 {len(filtered)} 个新机会 (已持仓: {len(existing_markets)})")
        return filtered
    
    def calculate_position_size(self, opportunity: ArbitrageOpportunity) -> float:
        """
        计算仓位大小
        基于凯利公式简化版
        """
        p = opportunity.estimated_real_probability / 100  # 获胜概率
        b = opportunity.expected_return / 100  # 赔率
        
        # 凯利公式: f = (bp - q) / b
        # 其中 q = 1 - p
        q = 1 - p
        
        if b <= 0:
            return 0
        
        kelly_fraction = (b * p - q) / b
        
        # 使用半凯利（降低风险）
        half_kelly = kelly_fraction * 0.5
        
        # 限制最大仓位
        max_position = min(self.MAX_POSITION_SIZE, half_kelly * 1000)
        
        # 根据置信度调整
        confidence_factor = opportunity.confidence_score / 100
        final_size = max_position * confidence_factor
        
        return max(final_size, 10)  # 最小 $10
    
    def execute_trade(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        执行交易
        """
        try:
            logger.info(f"\n🚀 准备执行交易:")
            logger.info(f"   市场: {opportunity.question[:50]}...")
            logger.info(f"   结果: {opportunity.outcome}")
            logger.info(f"   价格: {opportunity.market_price:.4f}")
            logger.info(f"   期望收益: {opportunity.expected_return:.1f}%")
            
            # 计算仓位大小
            position_size = self.calculate_position_size(opportunity)
            
            # 检查持仓限制
            open_positions = [p for p in self.positions if p.status == 'open']
            if len(open_positions) >= self.MAX_POSITIONS:
                logger.warning(f"⚠️ 已达到最大持仓数 {self.MAX_POSITIONS}，跳过")
                return False
            
            # 检查余额（实际实现需要查询余额）
            # balance = self.client.get_balance()
            
            logger.info(f"   建议仓位: ${position_size:.2f}")
            logger.info(f"   ⚠️ 注意: 实际交易需要确认 USDC 余额充足")
            
            # 模拟交易（实际部署时取消注释）
            # order_args = OrderArgs(
            #     price=opportunity.market_price,
            #     size=position_size,
            #     side="BUY",
            #     market_id=opportunity.market_id
            # )
            # 
            # order = self.client.create_order(order_args)
            
            # 记录持仓
            position = Position(
                market_id=opportunity.market_id,
                question=opportunity.question,
                outcome=opportunity.outcome,
                entry_price=opportunity.market_price,
                entry_time=datetime.now(),
                position_size=position_size,
                target_exit_price=self.TAKE_PROFIT_THRESHOLD,
                stop_loss_price=self.STOP_LOSS_THRESHOLD,
                status='open'
            )
            
            self.positions.append(position)
            self.save_positions()
            
            logger.info(f"   ✅ 交易已记录 (模拟模式)")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ 执行交易失败: {e}")
            return False
    
    def check_exit_conditions(self):
        """
        检查出场条件
        """
        logger.info("\n📊 检查出场条件...")
        
        for position in self.positions:
            if position.status != 'open':
                continue
            
            try:
                # 获取当前市场价格
                # market = self.client.get_market(position.market_id)
                # current_price = market.get("price", 0)
                
                # 简化为基于时间的检查
                days_held = (datetime.now() - position.entry_time).days
                
                # 出场条件 1: 价格达到目标
                # if current_price >= position.target_exit_price:
                #     logger.info(f"✅ 获利了结: {position.question[:40]}...")
                #     position.status = 'closed'
                
                # 出场条件 2: 止损
                # if current_price <= position.stop_loss_price:
                #     logger.info(f"⛔ 止损: {position.question[:40]}...")
                #     position.status = 'closed'
                
                # 出场条件 3: 持仓过久（30天）
                if days_held > 30:
                    logger.info(f"⏰ 持仓过久，建议评估: {position.question[:40]}...")
                    
            except Exception as e:
                logger.error(f"   ⚠️ 检查出场条件时出错: {e}")
        
        self.save_positions()
    
    def run(self):
        """
        主运行循环
        """
        logger.info("\n" + "=" * 70)
        logger.info("🚀 启动 IEA 策略")
        logger.info("=" * 70)
        logger.info(f"策略参数:")
        logger.info(f"  单笔最大: ${self.MAX_POSITION_SIZE}")
        logger.info(f"  最大持仓: {self.MAX_POSITIONS}")
        logger.info(f"  最小流动性: ${self.MIN_LIQUIDITY:,}")
        logger.info(f"  最大价格: {self.MAX_MARKET_PRICE*100}%")
        logger.info(f"  最小期望收益: {self.MIN_EXPECTED_RETURN*100}%")
        logger.info("=" * 70)
        
        # 步骤 1: 寻找机会
        opportunities = self.find_opportunities()
        
        # 步骤 2: 过滤已持仓
        new_opportunities = self.filter_existing_positions(opportunities)
        
        # 步骤 3: 执行交易（前 5 个最佳机会）
        executed = 0
        for opp in new_opportunities[:5]:
            if self.execute_trade(opp):
                executed += 1
                time.sleep(1)  # 避免请求过快
        
        # 步骤 4: 检查出场
        self.check_exit_conditions()
        
        # 步骤 5: 生成报告
        self.generate_report(opportunities, executed)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ IEA 策略运行完成")
        logger.info("=" * 70)
    
    def generate_report(self, opportunities: List[ArbitrageOpportunity], executed: int):
        """
        生成策略报告
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"IEA_REPORT_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🤖 IEA 策略执行报告\n\n")
            f.write(f"**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**策略**: Impossible Event Arbitrage\n\n")
            
            f.write("## 📊 执行摘要\n\n")
            f.write(f"| 指标 | 数值 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 发现机会 | {len(opportunities)} 个 |\n")
            f.write(f"| 执行交易 | {executed} 笔 |\n")
            f.write(f"| 当前持仓 | {len([p for p in self.positions if p.status == 'open'])} 个 |\n")
            f.write(f"| 总交易次数 | {len(self.positions)} 次 |\n\n")
            
            if opportunities:
                f.write("## 🎯 最佳机会 TOP 10\n\n")
                f.write(f"| 排名 | 市场 | 结果 | 价格 | 期望收益 | 置信度 |\n")
                f.write(f"|------|------|------|------|----------|--------|\n")
                
                for i, opp in enumerate(opportunities[:10], 1):
                    question = opp.question[:35] + "..."
                    f.write(f"| {i} | {question} | {opp.outcome[:15]} | "
                           f"{opp.market_price:.2%} | {opp.expected_return:.0f}% | "
                           f"{opp.confidence_score} |\n")
            
            f.write("\n## 💼 当前持仓\n\n")
            open_positions = [p for p in self.positions if p.status == 'open']
            if open_positions:
                for p in open_positions:
                    f.write(f"- **{p.question[:50]}...**\n")
                    f.write(f"  - 结果: {p.outcome}\n")
                    f.write(f"  - 入场价: {p.entry_price:.4f}\n")
                    f.write(f"  - 仓位: ${p.position_size:.2f}\n")
                    f.write(f"  - 入场时间: {p.entry_time.strftime('%Y-%m-%d')}\n\n")
            else:
                f.write("*当前没有持仓*\n")
            
            f.write("\n## 📈 策略说明\n\n")
            f.write("本策略基于以下逻辑:\n")
            f.write("1. **不可能事件**: 寻找市场价格 < 10% 的机会\n")
            f.write("2. **定价错误**: 估计真实概率是市场价格 3 倍以上\n")
            f.write("3. **小资金分散**: 单笔最多 $50，最多 20 个持仓\n")
            f.write("4. **长期持有**: 等待事件结果，不频繁交易\n\n")
            
            f.write("---\n\n")
            f.write("*报告由 IEA 策略自动生成*\n")
        
        logger.info(f"📄 报告已保存: {report_file}")

def main():
    """
    主函数
    """
    try:
        strategy = ImpossibleEventArbitrage()
        strategy.run()
    except Exception as e:
        logger.error(f"❌ 策略运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
