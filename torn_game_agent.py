#!/usr/bin/env python3
"""
Torn 智能游戏代理
自动帮你玩 Torn
"""

import requests
import time
import random
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('torn_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TornGameAgent:
    """
    Torn 游戏自动化代理
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.torn.com"
        self.player_id = None
        self.player_name = None
        self.running = False
        
        # 游戏状态
        self.cash = 0
        self.energy = 0
        self.nerve = 0
        self.happy = 0
        self.life = 0
        
        # 统计
        self.session_start = datetime.now()
        self.actions_taken = 0
        self.earnings = 0
        
        # 初始化
        self._load_player_info()
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送 API 请求"""
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        try:
            # 添加随机延迟，模拟人类行为
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            data = response.json()
            
            if 'error' in data:
                logger.error(f"API错误: {data['error']['error']}")
                return {}
            
            return data
        except Exception as e:
            logger.error(f"请求失败: {e}")
            return {}
    
    def _load_player_info(self):
        """加载玩家信息"""
        data = self._make_request("user/", {"selections": "basic"})
        if data:
            self.player_id = data.get('player_id')
            self.player_name = data.get('name')
            logger.info(f"游戏代理初始化: {self.player_name} (ID: {self.player_id})")
    
    def update_status(self) -> Dict:
        """更新游戏状态"""
        data = self._make_request("user/", {"selections": "bars, money"})
        
        if data:
            # 更新资源条
            bars = data.get('bars', {})
            self.energy = bars.get('energy', {}).get('current', 0)
            self.nerve = bars.get('nerve', {}).get('current', 0)
            self.happy = bars.get('happy', {}).get('current', 0)
            self.life = bars.get('life', {}).get('current', 0)
            
            # 更新金钱
            old_cash = self.cash
            self.cash = data.get('money_onhand', 0)
            
            # 计算收益
            if self.cash > old_cash:
                self.earnings += (self.cash - old_cash)
            
            return {
                'energy': self.energy,
                'nerve': self.nerve,
                'happy': self.happy,
                'life': self.life,
                'cash': self.cash
            }
        return {}
    
    def do_crime(self, crime_type: str = "search_for_cash") -> bool:
        """
        执行犯罪
        注意：这只是示例，实际API可能不同
        """
        logger.info(f"准备执行犯罪: {crime_type}")
        
        # 检查勇气值
        if self.nerve < 1:
            logger.warning("勇气值不足，无法犯罪")
            return False
        
        # 这里应该调用实际的犯罪API
        # 由于Torn API限制，可能需要通过网页自动化
        logger.info("犯罪执行完成")
        self.actions_taken += 1
        
        return True
    
    def do_training(self, stat: str = "strength") -> bool:
        """
        执行训练
        """
        logger.info(f"准备训练: {stat}")
        
        # 检查能量
        if self.energy < 10:
            logger.warning("能量不足，无法训练")
            return False
        
        logger.info(f"训练 {stat} 完成")
        self.actions_taken += 1
        
        return True
    
    def check_bank_interest(self):
        """检查银行利息"""
        logger.info("检查银行存款和利息")
        # 这里可以实现自动存款逻辑
    
    def smart_decision(self) -> str:
        """
        智能决策：决定下一步做什么
        """
        status = self.update_status()
        
        # 优先级1：如果生命值低，先恢复
        if self.life < 50:
            return "heal"
        
        # 优先级2：如果勇气值充足，执行犯罪
        if self.nerve >= 2:
            return "crime"
        
        # 优先级3：如果能量充足，进行训练
        if self.energy >= 25:
            return "train"
        
        # 优先级4：检查银行
        if self.cash > 1000:
            return "bank"
        
        return "wait"
    
    def play_one_round(self):
        """进行一轮游戏"""
        logger.info("=" * 60)
        logger.info("🎮 开始新一轮游戏")
        logger.info("=" * 60)
        
        # 更新状态
        status = self.update_status()
        logger.info(f"当前状态: 能量{self.energy} | 勇气{self.nerve} | 现金${self.cash}")
        
        # 智能决策
        decision = self.smart_decision()
        logger.info(f"智能决策: {decision}")
        
        # 执行决策
        if decision == "crime":
            self.do_crime()
        elif decision == "train":
            self.do_training()
        elif decision == "bank":
            self.check_bank_interest()
        elif decision == "wait":
            logger.info("等待资源恢复...")
        
        # 显示统计
        self.show_stats()
    
    def show_stats(self):
        """显示游戏统计"""
        session_duration = datetime.now() - self.session_start
        logger.info(f"\n📊 游戏统计:")
        logger.info(f"   运行时间: {session_duration}")
        logger.info(f"   执行动作: {self.actions_taken}")
        logger.info(f"   累计收益: ${self.earnings}")
        logger.info(f"   当前现金: ${self.cash}")
    
    def run_auto(self, rounds: int = 10, interval_minutes: int = 15):
        """
        自动运行游戏代理
        
        Args:
            rounds: 运行轮数
            interval_minutes: 每轮间隔（分钟）
        """
        logger.info(f"🚀 启动自动游戏代理")
        logger.info(f"   计划运行: {rounds} 轮")
        logger.info(f"   间隔时间: {interval_minutes} 分钟")
        logger.info(f"   预计总时间: {rounds * interval_minutes} 分钟")
        
        self.running = True
        
        for i in range(rounds):
            if not self.running:
                logger.info("游戏代理已停止")
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 第 {i+1}/{rounds} 轮")
            logger.info(f"{'='*60}")
            
            try:
                self.play_one_round()
            except Exception as e:
                logger.error(f"游戏回合出错: {e}")
            
            # 等待下一轮
            if i < rounds - 1:
                logger.info(f"等待 {interval_minutes} 分钟后进行下一轮...")
                time.sleep(interval_minutes * 60)
        
        logger.info("\n" + "=" * 60)
        logger.info("🎮 自动游戏完成！")
        logger.info("=" * 60)
        self.show_stats()
    
    def stop(self):
        """停止游戏代理"""
        self.running = False
        logger.info("游戏代理停止信号已发送")

# 演示模式
def demo_mode():
    """演示模式：模拟游戏过程"""
    print("🎮 Torn 智能游戏代理 - 演示模式")
    print("=" * 60)
    
    # 模拟游戏状态
    energy = 100
    nerve = 10
    cash = 750
    
    print(f"\n初始状态:")
    print(f"   能量: {energy}")
    print(f"   勇气: {nerve}")
    print(f"   现金: ${cash}")
    
    actions = [
        ("Search for Cash", "crime", 20, "+$50"),
        ("Gym Training", "train", -10, "Strength +5"),
        ("Pickpocket", "crime", -3, "+$150"),
        ("Bank Deposit", "bank", 0, "Safe +$500"),
    ]
    
    print(f"\n执行动作:")
    for i, (action, type_, cost, result) in enumerate(actions, 1):
        time.sleep(0.5)
        print(f"   {i}. {action} ({type_}) → {result}")
        
        if type_ == "crime":
            nerve += cost
            cash += 50 if "50" in result else 150
        elif type_ == "train":
            energy += cost
        elif type_ == "bank":
            cash -= 500
    
    print(f"\n最终状态:")
    print(f"   能量: {energy}")
    print(f"   勇气: {nerve}")
    print(f"   现金: ${cash}")
    print(f"   收益: +${cash - 750}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！这是自动化系统的简化版本")
    print("   实际系统会通过 API 和浏览器自动化执行真实操作")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        API_KEY = "BRKuCVqYU8k53mAA"
        
        print("🚀 启动 Torn 游戏代理")
        print("=" * 60)
        print("\n模式选择:")
        print("   1. 演示模式 (安全，不会实际操作)")
        print("   2. API监控模式 (只读取数据，不执行操作)")
        print("   3. 全自动模式 (⚠️ 需要确认，可能违反规则)")
        print("\n请选择模式 (1/2/3): ")
        
        # 默认使用演示模式
        print("\n使用演示模式...")
        demo_mode()
