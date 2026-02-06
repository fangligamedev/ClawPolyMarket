#!/bin/bash
# Phase 4 实施脚本 - 机器学习优化
# 运行: bash phase4_implementation.sh

echo "=========================================="
echo "🧠 Phase 4 实施: 机器学习优化"
echo "=========================================="
echo ""

echo "📋 机器学习架构"
echo "------------------------------"
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│        机器学习交易系统 v1.0            │"
echo "├─────────────────────────────────────────┤"
echo "│                                         │"
echo "│  历史数据  →  特征工程  →  模型训练     │"
echo "│     ↑              ↓           ↓       │"
echo "│  回测验证  ←  信号生成  ←  预测模型     │"
echo "│                                         │"
echo "│  自动优化  →  参数调优  →  部署上线     │"
echo "│                                         │"
echo "└─────────────────────────────────────────┘"
echo ""

# 创建历史数据收集模块
echo "📋 步骤 1: 创建历史数据收集系统"
echo "------------------------------"

cat > historical_data_collector.py << 'EOF'
#!/usr/bin/env python3
"""
历史数据收集器
收集 Polymarket 历史数据用于回测
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path

class HistoricalDataCollector:
    """历史数据收集器"""
    
    def __init__(self):
        self.data_dir = Path("historical_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 要收集的市场
        self.markets = [
            "Will Donald Trump win the 2024 U.S. presidential election?",
            "Will Joe Biden win the 2024 U.S. presidential election?",
            "Will Bitcoin ETF be approved by January 2024?",
            # 添加更多市场...
        ]
    
    async def fetch_market_history(self, market_id: str, days: int = 90) -> list:
        """获取市场历史价格数据"""
        
        # 这里应该调用 Polymarket API 获取历史数据
        # 简化版示例
        
        history = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 模拟数据 (实际应该从 API 获取)
        current_date = start_date
        while current_date <= end_date:
            # 这里应该调用实际 API
            history.append({
                'timestamp': current_date.isoformat(),
                'price': 0.5,  # 模拟价格
                'volume': 1000,
                'liquidity': 50000
            })
            current_date += timedelta(hours=1)
        
        return history
    
    async def collect_all_data(self):
        """收集所有数据"""
        print("🚀 开始收集历史数据")
        
        for market in self.markets:
            print(f"\n📊 收集: {market[:50]}...")
            
            history = await self.fetch_market_history(market)
            
            # 保存数据
            filename = self.data_dir / f"{market.replace(' ', '_')[:30]}_history.json"
            with open(filename, 'w') as f:
                json.dump(history, f, indent=2)
            
            print(f"   ✅ 已保存 {len(history)} 条记录")
        
        print("\n✅ 数据收集完成")

if __name__ == "__main__":
    collector = HistoricalDataCollector()
    asyncio.run(collector.collect_all_data())
EOF

echo "✅ 历史数据收集器已创建"
echo ""

# 创建特征工程模块
echo "📋 步骤 2: 创建特征工程模块"
echo "------------------------------"

cat > feature_engineering.py << 'EOF'
#!/usr/bin/env python3
"""
特征工程模块
从原始数据中提取有意义的特征
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict

class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self):
        self.features = []
    
    def extract_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取价格相关特征"""
        
        # 价格动量
        df['price_momentum_1h'] = df['price'].pct_change(periods=1)
        df['price_momentum_24h'] = df['price'].pct_change(periods=24)
        df['price_momentum_7d'] = df['price'].pct_change(periods=168)
        
        # 波动率
        df['volatility_1h'] = df['price'].rolling(window=24).std()
        df['volatility_24h'] = df['price'].rolling(window=168).std()
        
        # 移动平均线
        df['ma_1h'] = df['price'].rolling(window=24).mean()
        df['ma_24h'] = df['price'].rolling(window=168).mean()
        
        # RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def extract_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取交易量特征"""
        
        # 交易量变化
        df['volume_change_1h'] = df['volume'].pct_change(periods=1)
        df['volume_change_24h'] = df['volume'].pct_change(periods=24)
        
        # 交易量移动平均
        df['volume_ma_1h'] = df['volume'].rolling(window=24).mean()
        df['volume_ma_24h'] = df['volume'].rolling(window=168).mean()
        
        # 量价关系
        df['volume_price_ratio'] = df['volume'] / df['price']
        
        return df
    
    def extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取时间特征"""
        
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['day_of_month'] = pd.to_datetime(df['timestamp']).dt.day
        
        # 是否周末
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    def extract_sentiment_features(self, df: pd.DataFrame, sentiment_data: Dict) -> pd.DataFrame:
        """提取情绪特征"""
        
        # Twitter 情绪
        df['twitter_sentiment'] = sentiment_data.get('twitter', 0.5)
        
        # 民调偏差
        df['poll_divergence'] = sentiment_data.get('poll_divergence', 0)
        
        # 新闻情绪
        df['news_sentiment'] = sentiment_data.get('news', 0.5)
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame, lookahead: int = 24) -> pd.DataFrame:
        """创建目标变量 (未来价格方向)"""
        
        # 未来24小时的价格变化
        future_return = df['price'].shift(-lookahead) / df['price'] - 1
        
        # 分类目标: 1 (上涨), 0 (持平), -1 (下跌)
        df['target'] = np.where(future_return > 0.02, 1,
                               np.where(future_return < -0.02, -1, 0))
        
        return df
    
    def process_all_features(self, data: List[Dict], sentiment_data: Dict = None) -> pd.DataFrame:
        """处理所有特征"""
        
        df = pd.DataFrame(data)
        
        # 提取各类特征
        df = self.extract_price_features(df)
        df = self.extract_volume_features(df)
        df = self.extract_time_features(df)
        
        if sentiment_data:
            df = self.extract_sentiment_features(df, sentiment_data)
        
        df = self.create_target_variable(df)
        
        # 删除 NaN 值
        df = df.dropna()
        
        print(f"✅ 特征工程完成: {len(df)} 样本, {len(df.columns)} 特征")
        
        return df

if __name__ == "__main__":
    # 示例用法
    import json
    
    # 加载历史数据
    with open('historical_data/sample_history.json', 'r') as f:
        data = json.load(f)
    
    engineer = FeatureEngineer()
    features_df = engineer.process_all_features(data)
    
    print("\n特征列表:")
    print(features_df.columns.tolist())
    print("\n前5行:")
    print(features_df.head())
EOF

echo "✅ 特征工程模块已创建"
echo ""

# 创建模型训练模块
echo "📋 步骤 3: 创建模型训练模块"
echo "------------------------------"

cat > model_training.py << 'EOF'
#!/usr/bin/env python3
"""
模型训练模块
训练价格预测模型
"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

class ModelTrainer:
    """模型训练器"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        }
        self.best_model = None
        self.best_score = 0
    
    def prepare_data(self, df: pd.DataFrame) -> tuple:
        """准备训练数据"""
        
        # 特征列 (排除非特征列)
        feature_cols = [col for col in df.columns if col not in 
                       ['timestamp', 'target', 'price']]
        
        X = df[feature_cols]
        y = df['target']
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def train_models(self, X_train, y_train):
        """训练多个模型"""
        
        print("🚀 开始训练模型")
        
        for name, model in self.models.items():
            print(f"\n📊 训练 {name}...")
            
            # 训练
            model.fit(X_train, y_train)
            
            # 交叉验证
            scores = cross_val_score(model, X_train, y_train, cv=5)
            mean_score = scores.mean()
            
            print(f"   交叉验证准确率: {mean_score:.3f} (+/- {scores.std()*2:.3f})")
            
            # 选择最佳模型
            if mean_score > self.best_score:
                self.best_score = mean_score
                self.best_model = model
                print(f"   ⭐ 当前最佳模型: {name}")
    
    def evaluate_model(self, X_test, y_test):
        """评估模型性能"""
        
        if self.best_model is None:
            print("❌ 没有训练好的模型")
            return
        
        # 预测
        y_pred = self.best_model.predict(X_test)
        
        # 计算指标
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1': f1_score(y_test, y_pred, average='weighted')
        }
        
        print("\n📈 模型评估结果:")
        print(f"   准确率: {metrics['accuracy']:.3f}")
        print(f"   精确率: {metrics['precision']:.3f}")
        print(f"   召回率: {metrics['recall']:.3f}")
        print(f"   F1分数: {metrics['f1']:.3f}")
        
        return metrics
    
    def get_feature_importance(self, feature_names: list) -> pd.DataFrame:
        """获取特征重要性"""
        
        if self.best_model is None:
            return None
        
        importance = self.best_model.feature_importances_
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\n🔍 特征重要性 (Top 10):")
        print(importance_df.head(10).to_string(index=False))
        
        return importance_df
    
    def save_model(self, filepath: str = 'models/prediction_model.pkl'):
        """保存模型"""
        
        if self.best_model is None:
            print("❌ 没有训练好的模型")
            return
        
        import os
        os.makedirs('models', exist_ok=True)
        
        joblib.dump(self.best_model, filepath)
        print(f"\n💾 模型已保存: {filepath}")
    
    def load_model(self, filepath: str = 'models/prediction_model.pkl'):
        """加载模型"""
        
        self.best_model = joblib.load(filepath)
        print(f"✅ 模型已加载: {filepath}")

if __name__ == "__main__":
    # 示例用法
    from feature_engineering import FeatureEngineer
    import json
    
    # 加载数据
    with open('historical_data/sample_history.json', 'r') as f:
        data = json.load(f)
    
    # 特征工程
    engineer = FeatureEngineer()
    df = engineer.process_all_features(data)
    
    # 训练模型
    trainer = ModelTrainer()
    X_train, X_test, y_train, y_test, feature_cols = trainer.prepare_data(df)
    trainer.train_models(X_train, y_train)
    trainer.evaluate_model(X_test, y_test)
    trainer.get_feature_importance(feature_cols)
    trainer.save_model()
EOF

echo "✅ 模型训练模块已创建"
echo ""

# 创建自动优化模块
echo "📋 步骤 4: 创建自动优化模块"
echo "------------------------------"

cat > auto_optimizer.py << 'EOF'
#!/usr/bin/env python3
"""
自动优化模块
使用 Optuna 自动优化策略参数
"""

import optuna
from datetime import datetime
import json

def optimize_strategy_params():
    """
    优化策略参数
    
    目标: 最大化收益 / 最小化回撤
    """
    
    def objective(trial):
        # 定义参数搜索空间
        params = {
            'buy_threshold': trial.suggest_float('buy_threshold', 0.1, 0.5),
            'sell_threshold': trial.suggest_float('sell_threshold', 0.5, 0.9),
            'position_size': trial.suggest_int('position_size', 10, 100),
            'stop_loss': trial.suggest_float('stop_loss', 0.02, 0.1),
            'take_profit': trial.suggest_float('take_profit', 0.05, 0.3),
            'max_positions': trial.suggest_int('max_positions', 1, 5)
        }
        
        # 这里应该运行回测
        # 简化版示例
        
        # 模拟回测收益
        # 实际应该调用 backtest_engine
        pnl = simulate_backtest(params)
        
        return pnl
    
    def simulate_backtest(params: dict) -> float:
        """模拟回测 (实际应该使用真实回测)"""
        
        # 这是一个简化的模拟
        # 实际应该运行完整的回测
        
        import random
        random.seed(42)
        
        # 模拟收益 (实际应该用策略参数回测)
        base_return = 0.1
        noise = random.gauss(0, 0.05)
        
        # 参数合理性奖励
        if params['buy_threshold'] < params['sell_threshold']:
            reward = 0.02
        else:
            reward = -0.02
        
        return base_return + noise + reward
    
    # 创建优化研究
    study = optuna.create_study(
        study_name='polymarket_strategy',
        direction='maximize',
        storage='sqlite:///optimization.db'
    )
    
    print("🚀 开始自动优化")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行优化
    study.optimize(objective, n_trials=100, show_progress_bar=True)
    
    # 输出结果
    print("\n✅ 优化完成!")
    print(f"\n📊 最佳参数:")
    print(f"   收益: {study.best_value:.4f}")
    print(f"   参数: {json.dumps(study.best_params, indent=2)}")
    
    # 保存结果
    result = {
        'timestamp': datetime.now().isoformat(),
        'best_value': study.best_value,
        'best_params': study.best_params,
        'n_trials': len(study.trials)
    }
    
    with open('optimization_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 结果已保存: optimization_results.json")
    
    return study.best_params

if __name__ == "__main__":
    best_params = optimize_strategy_params()
EOF

echo "✅ 自动优化模块已创建"
echo ""

# 创建回测框架
echo "📋 步骤 5: 创建回测框架"
echo "------------------------------"

cat > backtest_engine.py << 'EOF'
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
EOF

echo "✅ 回测框架已创建"
echo ""

echo "=========================================="
echo "🧠 Phase 4 准备完成！"
echo "=========================================="
echo ""
echo "📦 已创建模块:"
echo "   - historical_data_collector.py - 历史数据收集"
echo "   - feature_engineering.py - 特征工程"
echo "   - model_training.py - 模型训练"
echo "   - auto_optimizer.py - 自动优化"
echo "   - backtest_engine.py - 回测引擎"
echo ""
echo "🚀 实施步骤:"
echo ""
echo "1. 安装依赖:"
echo "   pip install pandas numpy scikit-learn optuna joblib"
echo ""
echo "2. 收集历史数据:"
echo "   python3 historical_data_collector.py"
echo ""
echo "3. 特征工程:"
echo "   python3 feature_engineering.py"
echo ""
echo "4. 训练模型:"
echo "   python3 model_training.py"
echo ""
echo "5. 自动优化:"
echo "   python3 auto_optimizer.py"
echo ""
echo "6. 回测验证:"
echo "   python3 backtest_engine.py"
echo ""
echo "🎯 目标: 模型准确率 >65%, 月收益率 >10%"
echo "=========================================="
