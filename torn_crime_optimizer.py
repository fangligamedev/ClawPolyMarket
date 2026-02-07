#!/usr/bin/env python3
"""
Torn AI - 犯罪优化器
选择最优犯罪路径
"""

import json
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Crime:
    name: str
    nerve: int
    difficulty: float
    expected_reward: float
    risk_level: str
    required_stats: Dict[str, int]
    description: str

class CrimeOptimizer:
    """
    犯罪路径优化器
    基于当前资金和技能推荐最优犯罪
    """
    
    def __init__(self):
        # 定义所有犯罪选项
        self.crimes = {
            'search_for_cash': Crime(
                name='Search for Cash',
                nerve=1,
                difficulty=0.1,
                expected_reward=50,
                risk_level='very_low',
                required_stats={},
                description='Search the streets for loose cash'
            ),
            'sell_copper': Crime(
                name='Sell Coppered Wares',
                nerve=2,
                difficulty=0.2,
                expected_reward=150,
                risk_level='low',
                required_stats={},
                description='Sell counterfeit goods'
            ),
            'rob_senior': Crime(
                name='Rob a Senior',
                nerve=3,
                difficulty=0.4,
                expected_reward=400,
                risk_level='medium',
                required_stats={'strength': 50},
                description='Rob an elderly person'
            ),
            'pickpocket': Crime(
                name='Pickpocket Someone',
                nerve=3,
                difficulty=0.5,
                expected_reward=600,
                risk_level='medium',
                required_stats={'dexterity': 50},
                description='Steal from someones pocket'
            ),
            'shoplift': Crime(
                name='Shoplift',
                nerve=4,
                difficulty=0.6,
                expected_reward=1000,
                risk_level='medium',
                required_stats={'dexterity': 100},
                description='Steal from a store'
            ),
            'rob_stores': Crime(
                name='Rob a Store',
                nerve=5,
                difficulty=0.7,
                expected_reward=2500,
                risk_level='high',
                required_stats={'strength': 200, 'dexterity': 150},
                description='Rob a store at gunpoint'
            ),
            'bank_fraud': Crime(
                name='Bank Fraud',
                nerve=6,
                difficulty=0.8,
                expected_reward=5000,
                risk_level='high',
                required_stats={'intelligence': 300},
                description='Commit bank fraud'
            ),
            'car_theft': Crime(
                name='Steal a Car',
                nerve=7,
                difficulty=0.7,
                expected_reward=8000,
                risk_level='high',
                required_stats={'dexterity': 300, 'intelligence': 200},
                description='Steal a parked car'
            )
        }
    
    def calculate_success_rate(self, crime: Crime, player_stats: Dict) -> float:
        """计算犯罪成功率"""
        base_rate = 1.0 - crime.difficulty
        
        # 检查属性要求
        for stat, required in crime.required_stats.items():
            current = player_stats.get(stat, 0)
            if current < required:
                # 属性不足，大幅降低成功率
                deficit = required - current
                base_rate *= max(0.1, 1 - (deficit / required))
        
        return max(0.05, min(0.95, base_rate))
    
    def calculate_expected_value(self, crime: Crime, player_stats: Dict) -> float:
        """计算期望收益"""
        success_rate = self.calculate_success_rate(crime, player_stats)
        expected_reward = crime.expected_reward * success_rate
        
        # 考虑风险成本（如果被抓住）
        failure_cost = 50  # 基础罚款
        risk_cost = (1 - success_rate) * failure_cost
        
        return expected_reward - risk_cost
    
    def get_recommendations(self, player_stats: Dict, nerve: int = 10, cash: int = 0) -> List[Dict]:
        """获取犯罪推荐列表"""
        recommendations = []
        
        for crime_id, crime in self.crimes.items():
            # 检查勇气值是否足够
            if crime.nerve > nerve:
                continue
            
            success_rate = self.calculate_success_rate(crime, player_stats)
            expected_value = self.calculate_expected_value(crime, player_stats)
            
            # 风险评分 (0-100)
            risk_score = int((1 - success_rate) * 100)
            
            recommendations.append({
                'id': crime_id,
                'name': crime.name,
                'nerve': crime.nerve,
                'success_rate': f"{success_rate*100:.1f}%",
                'expected_value': f"${expected_value:.0f}",
                'risk_score': risk_score,
                'risk_level': crime.risk_level,
                'description': crime.description,
                'recommended': success_rate > 0.5 and expected_value > 20
            })
        
        # 按期望收益排序
        recommendations.sort(
            key=lambda x: float(x['expected_value'].replace('$', '')),
            reverse=True
        )
        
        return recommendations
    
    def get_best_crime(self, player_stats: Dict, nerve: int = 10, cash: int = 0) -> Dict:
        """获取最优犯罪选择"""
        recommendations = self.get_recommendations(player_stats, nerve, cash)
        
        # 过滤掉成功率低于50%的
        viable_options = [r for r in recommendations if float(r['success_rate'].replace('%', '')) > 50]
        
        if viable_options:
            return viable_options[0]
        
        # 如果没有高成功率选项，返回成功率最高的
        if recommendations:
            return max(recommendations, key=lambda x: float(x['success_rate'].replace('%', '')))
        
        return {
            'id': 'search_for_cash',
            'name': 'Search for Cash',
            'success_rate': '90%',
            'expected_value': '$50'
        }
    
    def print_crime_guide(self, player_stats: Dict, nerve: int = 10):
        """打印犯罪指南"""
        print("\n" + "=" * 70)
        print("🔫 Torn AI - 犯罪优化指南")
        print("=" * 70)
        
        recommendations = self.get_recommendations(player_stats, nerve)
        
        print(f"\n📊 你的属性:")
        print(f"   力量: {player_stats.get('strength', 0)}")
        print(f"   速度: {player_stats.get('speed', 0)}")
        print(f"   防御: {player_stats.get('defense', 0)}")
        print(f"   灵巧: {player_stats.get('dexterity', 0)}")
        print(f"   勇气值: {nerve}")
        
        print(f"\n🎯 推荐犯罪（按期望收益排序）:")
        print("-" * 70)
        print(f"{'排名':<4} {'犯罪名称':<25} {'勇气':<6} {'成功率':<10} {'期望收益':<12} {'风险':<8}")
        print("-" * 70)
        
        for i, rec in enumerate(recommendations[:5], 1):
            marker = "⭐" if rec['recommended'] else "  "
            print(f"{marker}{i:<3} {rec['name']:<25} {rec['nerve']:<6} {rec['success_rate']:<10} {rec['expected_value']:<12} {rec['risk_level']:<8}")
        
        best = self.get_best_crime(player_stats, nerve)
        print(f"\n✅ 最优选择: {best['name']}")
        print(f"   成功率: {best['success_rate']}")
        print(f"   期望收益: {best['expected_value']}")
        print(f"   风险等级: {best['risk_level']}")
        
        print("\n" + "=" * 70)

# 测试
if __name__ == "__main__":
    optimizer = CrimeOptimizer()
    
    # 测试新手属性
    new_player_stats = {
        'strength': 100,
        'speed': 100,
        'defense': 100,
        'dexterity': 100
    }
    
    optimizer.print_crime_guide(new_player_stats, nerve=10)
    
    # 测试高级玩家
    advanced_stats = {
        'strength': 500,
        'speed': 500,
        'defense': 500,
        'dexterity': 500
    }
    
    print("\n" + "=" * 70)
    print("高级玩家推荐:")
    best = optimizer.get_best_crime(advanced_stats, nerve=10)
    print(f"最优选择: {best['name']} (期望收益: {best['expected_value']})")
