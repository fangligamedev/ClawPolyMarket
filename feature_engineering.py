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
