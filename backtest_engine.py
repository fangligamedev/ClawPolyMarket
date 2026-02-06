#!/usr/bin/env python3
"""
回测引擎
策略回测和评估
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 1000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, df: pd.DataFrame, strategy_params: dict) -> dict:
        """
        运行回测
        
        参数:
            df: 包含价格数据的 DataFrame
            strategy_params: 策略参数字典
        """
        
        print("🚀 开始回测")
        print(f"   初始资金: ${self.initial_capital}")
        print(f"   数据长度: {len(df)} 条")
        
        # 回测循环
        for i, row in df.iterrows():
            # 获取信号
            signal = self.generate_signal(row, strategy_params)
            
            # 执行交易
            if signal == 1:  # 买入信号
                self.buy(row, strategy_params)
            elif signal == -1:  # 卖出信号
                self.sell(row, strategy_params)
            
            # 更新权益
            self.update_equity(row)
        
        # 计算绩效指标
        metrics = self.calculate_metrics()
        
        print(f"\n✅ 回测完成")
        print(f"   最终资金: ${self.capital:.2f}")
        print(f"   总收益: {metrics['total_return']:.2%}")
        
        return metrics
    
    def generate_signal(self, row: pd.Series, params: dict) -> int:
        """生成交易信号"""
        
        # 简化版信号生成
        # 实际应该使用 ML 模型或复杂策略
        
        rsi = row.get('rsi', 50)
        price_momentum = row.get('price_momentum_24h', 0)
        
        if rsi < 30 and price_momentum > 0:
            return 1  # 买入
        elif rsi > 70 and price_momentum < 0:
            return -1  # 卖出
        
        return 0  # 持有
    
    def buy(self, row: pd.Series, params: dict):
        """买入"""
        
        if self.capital <= 0:
            return
        
        position_size = params.get('position_size', 10)
        cost = min(position_size, self.capital)
        
        self.capital -= cost
        self.positions['long'] = self.positions.get('long', 0) + cost / row['price']
        
        self.trades.append({
            'type': 'buy',
            'price': row['price'],
            'amount': cost,
            'timestamp': row.get('timestamp', datetime.now())
        })
    
    def sell(self, row: pd.Series, params: dict):
        """卖出"""
        
        if 'long' not in self.positions or self.positions['long'] <= 0:
            return
        
        amount = self.positions['long']
        revenue = amount * row['price']
        
        self.capital += revenue
        self.positions['long'] = 0
        
        self.trades.append({
            'type': 'sell',
            'price': row['price'],
            'amount': revenue,
            'timestamp': row.get('timestamp', datetime.now())
        })
    
    def update_equity(self, row: pd.Series):
        """更新权益"""
        
        position_value = self.positions.get('long', 0) * row['price']
        total_equity = self.capital + position_value
        
        self.equity_curve.append({
            'timestamp': row.get('timestamp'),
            'equity': total_equity
        })
    
    def calculate_metrics(self) -> dict:
        """计算绩效指标"""
        
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        # 总收益
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # 最大回撤
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()
        
        # 夏普比率 (简化版)
        returns = equity_df['equity'].pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0
        
        # 胜率
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            buy_trades = trades_df[trades_df['type'] == 'buy']
            sell_trades = trades_df[trades_df['type'] == 'sell']
            
            if len(sell_trades) > 0:
                # 简化的胜率计算
                win_rate = 0.5  # 实际需要计算每笔交易的盈亏
            else:
                win_rate = 0
        else:
            win_rate = 0
        
        return {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'num_trades': len(self.trades),
            'final_capital': final_equity
        }

if __name__ == "__main__":
    # 示例用法
    import json
    from feature_engineering import FeatureEngineer
    
    # 加载数据
    with open('historical_data/sample_history.json', 'r') as f:
        data = json.load(f)
    
    # 特征工程
    engineer = FeatureEngineer()
    df = engineer.process_all_features(data)
    
    # 运行回测
    engine = BacktestEngine(initial_capital=1000)
    
    strategy_params = {
        'position_size': 100,
        'stop_loss': 0.05,
        'take_profit': 0.1
    }
    
    metrics = engine.run_backtest(df, strategy_params)
    
    print("\n📊 回测绩效:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
