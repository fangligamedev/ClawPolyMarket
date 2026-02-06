#!/usr/bin/env python3
"""
Hummingbot 监控脚本
实时监控做市表现
"""

import json
import time
from datetime import datetime
from pathlib import Path

def monitor_performance():
    """监控 Hummingbot 表现"""
    
    print("📊 Hummingbot 性能监控")
    print("=" * 50)
    
    log_dir = Path("hummingbot_files/hummingbot_logs")
    
    if not log_dir.exists():
        print("❌ 日志目录不存在，Hummingbot 可能未运行")
        return
    
    # 读取最新日志
    log_files = list(log_dir.glob("*.log"))
    
    if not log_files:
        print("⏳ 暂无日志文件")
        return
    
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    
    print(f"📄 监控日志: {latest_log.name}")
    print(f"⏰ 更新时间: {datetime.fromtimestamp(latest_log.stat().st_mtime)}")
    
    # 统计关键指标
    with open(latest_log, 'r') as f:
        lines = f.readlines()
    
    fills = [l for l in lines if 'filled' in l.lower()]
    orders = [l for l in lines if 'order' in l.lower()]
    errors = [l for l in lines if 'error' in l.lower()]
    
    print(f"\n📈 统计:")
    print(f"   总订单: {len(orders)}")
    print(f"   成交: {len(fills)}")
    print(f"   错误: {len(errors)}")
    
    if fills:
        print(f"\n✅ 最近成交:")
        for fill in fills[-3:]:
            print(f"   {fill.strip()}")

if __name__ == "__main__":
    while True:
        monitor_performance()
        print(f"\n⏳ {datetime.now().strftime('%H:%M:%S')} - 等待 60 秒...")
        time.sleep(60)
