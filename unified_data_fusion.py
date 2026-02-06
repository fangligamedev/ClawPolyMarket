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
