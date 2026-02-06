#!/usr/bin/env python3
"""
信号提取器 - 从日志中识别交易信号
无需 Discord/Telegram，直接读取本地日志
"""

import re
import time
from datetime import datetime
from pathlib import Path

def monitor_logs():
    """
    实时监控日志文件并提取信号
    """
    log_files = {
        'twitter': '/root/clawd/twitter_monitor_0xCristal.log',
        'data_integration': '/root/clawd/data_integration.log'
    }
    
    print("🔍 信号提取器已启动")
    print("=" * 60)
    print("监控以下日志文件:")
    for name, path in log_files.items():
        print(f"  - {name}: {path}")
    print("=" * 60)
    print()
    
    # 信号模式
    signal_patterns = [
        (r'🚨.*signal.*detected', 'HIGH'),
        (r'置信度.*([0-9]+)', 'MEDIUM'),
        (r'bought|sold|long|short', 'LOW'),
    ]
    
    while True:
        try:
            for name, path in log_files.items():
                if Path(path).exists():
                    with open(path, 'r') as f:
                        lines = f.readlines()
                        
                    # 检查最近10行
                    for line in lines[-10:]:
                        for pattern, level in signal_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                print(f"[{timestamp}] [{level}] {name}: {line.strip()}")
                                
                                if level == 'HIGH':
                                    print("  ⚠️  高优先级信号！请检查详情")
                                
            time.sleep(5)  # 每5秒检查一次
            
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_logs()
