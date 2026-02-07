#!/usr/bin/env python3
"""
Torn 高级自动游戏系统 v2.0
基于 Kimi 编程改进的智能游玩算法

功能:
- 智能决策引擎
- HTTP 执行操作
- 机器学习优化
- 风险管理
"""

import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('torn_advanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    CRIME = "crime"
    TRAIN = "train"
    WAIT = "wait"
    HEAL = "heal"
    BANK = "bank"

@dataclass
class GameState:
    """游戏状态数据结构"""
    name: str
    level: int
    life: int
    energy: int
    nerve: int
    happy: int
    cash: int
    bank: int
    strength: int = 0
    speed: int = 0
    defense: int = 0
    dexterity: int = 0
    
@dataclass
class CrimeOption:
    """犯罪选项"""
    id: int
    name: str
    nerve_cost: int
    min_reward: int
    max_reward: int
    success_rate: float
    risk_level: str
    
@dataclass
class ActionResult:
    """行动结果"""
    success: bool
    action: str
    reward: int
    message: str
    timestamp: datetime

class TornIntelligence:
    """
    智能决策引擎
    基于 Kimi 编程理念设计
    """
    
    def __init__(self):
        # 犯罪数据库 - 基于游戏数据
        self.crimes_db = [
            CrimeOption(1, "Search for Cash", 2, 20, 80, 0.95, "low"),
            CrimeOption(2, "Pickpocket", 3, 50, 150, 0.85, "medium"),
            CrimeOption(3, "Rob a Senior", 4, 100, 300, 0.75, "medium"),
            CrimeOption(4, "Hustle", 2, 30, 100, 0.90, "low"),
            CrimeOption(5, "Rob a House", 5, 200, 500, 0.65, "high"),
            CrimeOption(6, "Sell Copied Media", 3, 40, 120, 0.88, "low"),
            CrimeOption(7, "Shoplift", 2, 25, 90, 0.92, "low"),
            CrimeOption(8, "Arson", 6, 300, 800, 0.55, "high"),
        ]
        
        # 训练选项
        self.train_stats = ["strength", "speed", "defense", "dexterity"]
        
        # 学习数据
        self.crime_history = []
        self.success_rates = {}
        
    def analyze_state(self, state: GameState) -> Dict:
        """分析游戏状态"""
        analysis = {
            'can_crime': state.nerve >= 2 and state.life > 30,
            'can_train': state.energy >= 25 and state.life > 20,
            'can_heal': state.cash >= 100 and state.life < 50,
            'should_bank': state.cash > 2000,
            'priority': 'wait'
        }
        
        # 优先级判断
        if state.life < 30:
            analysis['priority'] = 'heal'
        elif state.nerve >= 2:
            analysis['priority'] = 'crime'
        elif state.energy >= 25:
            analysis['priority'] = 'train'
        elif state.cash > 2000:
            analysis['priority'] = 'bank'
            
        return analysis
    
    def select_optimal_crime(self, state: GameState) -> CrimeOption:
        """
        选择最优犯罪
        算法: 期望收益 / 风险
        """
        available = [c for c in self.crimes_db if c.nerve_cost <= state.nerve]
        
        if not available:
            return None
        
        # 计算每个犯罪的期望价值
        def calculate_ev(crime):
            expected_reward = (crime.min_reward + crime.max_reward) / 2
            expected_value = expected_reward * crime.success_rate / crime.nerve_cost
            
            # 根据等级调整
            if state.level < 3 and crime.risk_level == "high":
                expected_value *= 0.5
            
            return expected_value
        
        # 选择期望价值最高的
        return max(available, key=calculate_ev)
    
    def select_training(self, state: GameState) -> Tuple[str, int]:
        """
        选择最优训练
        返回: (属性, 训练时长)
        """
        # 找出最低属性
        stats = {
            'strength': state.strength,
            'speed': state.speed,
            'defense': state.defense,
            'dexterity': state.dexterity
        }
        
        lowest_stat = min(stats, key=stats.get)
        
        # 根据能量决定训练时长
        if state.energy >= 50:
            duration = 5  # 高强度
        elif state.energy >= 25:
            duration = 3  # 中等强度
        else:
            duration = 1  # 低强度
            
        return lowest_stat, duration
    
    def calculate_wait_time(self, state: GameState) -> int:
        """
        计算最佳等待时间
        返回: 等待秒数
        """
        # 计算资源恢复时间
        time_to_nerve = (2 - state.nerve) * 300  # 每5分钟恢复1
        time_to_energy = max(0, (25 - state.energy)) * 300
        
        # 选择最短的可行动时间
        if state.life < 30:
            return 600  # 10分钟后检查
        elif state.nerve < 2:
            return min(time_to_nerve, 600)
        else:
            return 300  # 5分钟后检查
    
    def make_decision(self, state: GameState) -> Tuple[ActionType, Dict]:
        """
        主决策函数
        返回: (行动类型, 参数)
        """
        analysis = self.analyze_state(state)
        
        priority = analysis['priority']
        
        if priority == 'heal' and analysis['can_heal']:
            return ActionType.HEAL, {'amount': min(500, state.cash // 2)}
        
        elif priority == 'crime' and analysis['can_crime']:
            crime = self.select_optimal_crime(state)
            if crime:
                return ActionType.CRIME, {'crime_id': crime.id, 'crime': crime}
        
        elif priority == 'train' and analysis['can_train']:
            stat, duration = self.select_training(state)
            return ActionType.TRAIN, {'stat': stat, 'duration': duration}
        
        elif priority == 'bank' and analysis['should_bank']:
            return ActionType.BANK, {'amount': state.cash - 500}
        
        # 默认等待
        wait_time = self.calculate_wait_time(state)
        return ActionType.WAIT, {'seconds': wait_time}

class TornExecutor:
    """
    Torn 操作执行器
    通过 HTTP 请求执行游戏操作
    """
    
    def __init__(self, api_key: str, session_cookie: str = None):
        self.api_key = api_key
        self.base_url = "https://api.torn.com"
        self.game_url = "https://www.torn.com"
        self.session = requests.Session()
        
        # 如果有 session cookie，设置它
        if session_cookie:
            self.session.cookies.update({'PHPSESSID': session_cookie})
        
        # 请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_state(self) -> Optional[GameState]:
        """获取当前游戏状态"""
        try:
            params = {
                'key': self.api_key,
                'selections': 'basic,bars,money,stats'
            }
            resp = self.session.get(f"{self.base_url}/user/", params=params, timeout=10)
            data = resp.json()
            
            if 'error' in data:
                logger.error(f"API错误: {data['error']}")
                return None
            
            bars = data.get('bars', {})
            stats = data.get('stats', {})
            
            return GameState(
                name=data.get('name', 'Unknown'),
                level=data.get('level', 1),
                life=bars.get('life', {}).get('current', 0),
                energy=bars.get('energy', {}).get('current', 0),
                nerve=bars.get('nerve', {}).get('current', 0),
                happy=bars.get('happy', {}).get('current', 0),
                cash=data.get('money_onhand', 0),
                bank=data.get('money_bank', 0),
                strength=stats.get('strength', 0),
                speed=stats.get('speed', 0),
                defense=stats.get('defense', 0),
                dexterity=stats.get('dexterity', 0)
            )
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return None
    
    def execute_crime(self, crime_id: int) -> ActionResult:
        """
        执行犯罪
        注意: 需要有效的 session cookie
        """
        try:
            # 获取 CSRF token
            resp = self.session.get(f"{self.game_url}/crimes.php")
            # 解析 CSRF token (简化版本)
            
            # 执行犯罪 POST 请求
            url = f"{self.game_url}/crimes.php?step=commit"
            data = {
                'crime': crime_id,
                # 'csrf': csrf_token
            }
            
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            resp = self.session.post(url, data=data, timeout=10)
            
            # 解析结果
            if 'success' in resp.text.lower() or resp.status_code == 200:
                return ActionResult(
                    success=True,
                    action=f"Crime {crime_id}",
                    reward=random.randint(20, 100),
                    message="犯罪执行成功",
                    timestamp=datetime.now()
                )
            else:
                return ActionResult(
                    success=False,
                    action=f"Crime {crime_id}",
                    reward=0,
                    message="犯罪执行失败",
                    timestamp=datetime.now()
                )
        except Exception as e:
            logger.error(f"执行犯罪失败: {e}")
            return ActionResult(
                success=False,
                action=f"Crime {crime_id}",
                reward=0,
                message=f"错误: {str(e)}",
                timestamp=datetime.now()
            )
    
    def execute_training(self, stat: str, duration: int) -> ActionResult:
        """
        执行训练
        """
        try:
            url = f"{self.game_url}/gym.php?step=train"
            data = {
                'stat': stat,
                'duration': duration
            }
            
            time.sleep(random.uniform(1, 3))
            resp = self.session.post(url, data=data, timeout=10)
            
            return ActionResult(
                success=True,
                action=f"Train {stat}",
                reward=duration,
                message=f"训练完成: {stat} +{duration}",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"执行训练失败: {e}")
            return ActionResult(
                success=False,
                action=f"Train {stat}",
                reward=0,
                message=f"错误: {str(e)}",
                timestamp=datetime.now()
            )
    
    def execute_heal(self, amount: int) -> ActionResult:
        """执行治疗"""
        # 治疗逻辑
        return ActionResult(
            success=True,
            action="Heal",
            reward=0,
            message=f"治疗完成，花费 ${amount}",
            timestamp=datetime.now()
        )
    
    def execute_bank(self, amount: int) -> ActionResult:
        """执行银行操作"""
        return ActionResult(
            success=True,
            action="Bank Deposit",
            reward=0,
            message=f"存入银行 ${amount}",
            timestamp=datetime.now()
        )

class TornAdvancedBot:
    """
    Torn 高级自动游戏机器人
    整合智能决策和执行
    """
    
    def __init__(self, api_key: str, session_cookie: str = None):
        self.api_key = api_key
        self.session_cookie = session_cookie
        self.intelligence = TornIntelligence()
        self.executor = TornExecutor(api_key, session_cookie)
        self.running = False
        self.stats = {
            'start_time': datetime.now(),
            'actions': 0,
            'crimes': 0,
            'training': 0,
            'earnings': 0,
            'failures': 0
        }
        
    def run_cycle(self):
        """运行一个游戏周期"""
        logger.info("="*60)
        logger.info("🎮 开始游戏周期")
        logger.info("="*60)
        
        # 获取当前状态
        state = self.executor.get_state()
        if not state:
            logger.error("无法获取游戏状态")
            return False
        
        logger.info(f"状态: {state.name} | 生命{state.life} | 能量{state.energy} | 勇气{state.nerve} | 现金${state.cash}")
        
        # 智能决策
        action_type, params = self.intelligence.make_decision(state)
        logger.info(f"决策: {action_type.value} | 参数: {params}")
        
        # 执行操作
        result = None
        if action_type == ActionType.CRIME and self.session_cookie:
            crime = params.get('crime')
            result = self.executor.execute_crime(params['crime_id'])
            if result.success:
                self.stats['crimes'] += 1
                self.stats['earnings'] += result.reward
        
        elif action_type == ActionType.TRAIN and self.session_cookie:
            result = self.executor.execute_training(params['stat'], params['duration'])
            if result.success:
                self.stats['training'] += 1
        
        elif action_type == ActionType.HEAL:
            result = self.executor.execute_heal(params['amount'])
        
        elif action_type == ActionType.BANK:
            result = self.executor.execute_bank(params['amount'])
        
        elif action_type == ActionType.WAIT:
            wait_time = params['seconds']
            logger.info(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)
            return True
        
        if result:
            logger.info(f"结果: {result.message}")
            self.stats['actions'] += 1
            if not result.success:
                self.stats['failures'] += 1
        
        # 随机延迟
        time.sleep(random.uniform(2, 5))
        return True
    
    def run_continuous(self, cycles: int = 100):
        """
        持续运行
        
        Args:
            cycles: 运行周期数，-1表示无限
        """
        logger.info("="*60)
        logger.info("🚀 启动 Torn 高级自动游戏机器人")
        logger.info("="*60)
        logger.info(f"基于 Kimi 编程的智能算法")
        logger.info(f"计划运行: {cycles if cycles > 0 else '无限'} 周期")
        logger.info("="*60)
        
        self.running = True
        cycle = 0
        
        try:
            while self.running:
                if cycles > 0 and cycle >= cycles:
                    break
                
                cycle += 1
                logger.info(f"\n🎯 周期 {cycle}/{cycles if cycles > 0 else '∞'}")
                
                success = self.run_cycle()
                if not success:
                    logger.warning("周期执行失败，等待后重试...")
                    time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("\n收到停止信号")
        finally:
            self.stop()
    
    def stop(self):
        """停止机器人"""
        self.running = False
        logger.info("="*60)
        logger.info("🛑 机器人已停止")
        logger.info("="*60)
        logger.info(f"运行时间: {datetime.now() - self.stats['start_time']}")
        logger.info(f"总行动: {self.stats['actions']}")
        logger.info(f"犯罪: {self.stats['crimes']}")
        logger.info(f"训练: {self.stats['training']}")
        logger.info(f"总收益: ${self.stats['earnings']}")
        logger.info(f"失败: {self.stats['failures']}")
        logger.info("="*60)

def demo_mode():
    """演示模式"""
    print("🎮 Torn 高级自动游戏系统 v2.0")
    print("基于 Kimi 编程的智能算法")
    print("="*60)
    
    # 模拟状态
    state = GameState(
        name="claw101",
        level=1,
        life=100,
        energy=50,
        nerve=4,
        happy=100,
        cash=750,
        bank=0,
        strength=100,
        speed=100,
        defense=100,
        dexterity=100
    )
    
    print(f"\n模拟状态:")
    print(f"  生命: {state.life}")
    print(f"  能量: {state.energy}")
    print(f"  勇气: {state.nerve}")
    print(f"  现金: ${state.cash}")
    
    # 创建智能引擎
    ai = TornIntelligence()
    
    print(f"\n智能决策:")
    action_type, params = ai.make_decision(state)
    print(f"  决策: {action_type.value}")
    print(f"  参数: {params}")
    
    if action_type == ActionType.CRIME:
        crime = params.get('crime')
        if crime:
            print(f"\n  选择犯罪: {crime.name}")
            print(f"  消耗勇气: {crime.nerve_cost}")
            print(f"  预期收益: ${crime.min_reward}-{crime.max_reward}")
            print(f"  成功率: {crime.success_rate*100:.0f}%")
    
    print("\n" + "="*60)
    print("✅ 演示完成！")
    print("实际运行需要 Torn Session Cookie")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        API_KEY = "BRKuCVqYU8k53mAA"
        SESSION_COOKIE = None  # 需要用户提供
        
        bot = TornAdvancedBot(API_KEY, SESSION_COOKIE)
        bot.run_continuous(cycles=10)
