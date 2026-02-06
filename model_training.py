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
