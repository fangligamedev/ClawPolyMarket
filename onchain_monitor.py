#!/usr/bin/env python3
"""
链上数据监控 (Web3.py)
监控 Polygon 网络上的 Polymarket 活动
"""

import os
from datetime import datetime
from typing import Dict, List

try:
    from web3 import Web3
except ImportError:
    print("Installing web3...")
    os.system("pip install web3 -q")
    from web3 import Web3

class OnChainMonitor:
    """链上数据监控器"""
    
    def __init__(self):
        # Polygon RPC 节点
        self.rpc_urls = [
            "https://polygon-rpc.com",
            "https://rpc.ankr.com/polygon",
            "https://polygon.llamarpc.com"
        ]
        
        self.w3 = None
        self.connect()
        
        # Polymarket 相关合约地址
        self.contracts = {
            'ctf_exchange': '0x...',  # 需要实际地址
            'neg_risk_adapter': '0x...',
            'usdc': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
        }
    
    def connect(self):
        """连接 RPC 节点"""
        for url in self.rpc_urls:
            try:
                w3 = Web3(Web3.HTTPProvider(url))
                if w3.is_connected():
                    self.w3 = w3
                    print(f"✅ 已连接到 Polygon: {url}")
                    return True
            except Exception as e:
                print(f"❌ 连接失败 {url}: {e}")
                continue
        
        print("❌ 无法连接到任何 Polygon 节点")
        return False
    
    def get_usdc_transfers(self, hours: int = 1) -> List[Dict]:
        """获取 USDC 大额转账"""
        if not self.w3:
            return []
        
        # USDC Transfer 事件主题
        transfer_topic = self.w3.keccak(text="Transfer(address,address,uint256)").hex()
        
        try:
            # 获取最新区块
            latest = self.w3.eth.block_number
            blocks_per_hour = 1800  # ~2秒一个区块
            from_block = latest - (hours * blocks_per_hour)
            
            # 获取日志
            logs = self.w3.eth.get_logs({
                'fromBlock': from_block,
                'toBlock': 'latest',
                'address': self.contracts['usdc'],
                'topics': [transfer_topic]
            })
            
            transfers = []
            for log in logs:
                # 解析转账金额
                amount = int(log['data'], 16) / 1e6  # USDC 有 6 位小数
                
                if amount >= 10000:  # 只关注 >= $10,000
                    transfers.append({
                        'tx_hash': log['transactionHash'].hex(),
                        'amount': amount,
                        'block_number': log['blockNumber'],
                        'timestamp': datetime.now().isoformat()
                    })
            
            print(f"📊 发现 {len(transfers)} 个大额 USDC 转账 (>=$10K)")
            return transfers
            
        except Exception as e:
            print(f"❌ 获取转账失败: {e}")
            return []
    
    def get_block_timestamp(self, block_number: int) -> datetime:
        """获取区块时间戳"""
        if not self.w3:
            return datetime.now()
        
        try:
            block = self.w3.eth.get_block(block_number)
            return datetime.fromtimestamp(block['timestamp'])
        except:
            return datetime.now()
    
    def monitor(self):
        """监控链上活动"""
        print("🚀 启动链上数据监控")
        
        import time
        while True:
            try:
                # 获取大额转账
                transfers = self.get_usdc_transfers(hours=1)
                
                # 保存数据
                if transfers:
                    import json
                    with open('data/onchain_activity.json', 'w') as f:
                        json.dump({
                            'timestamp': datetime.now().isoformat(),
                            'transfers': transfers
                        }, f, indent=2)
                
                print(f"⏰ 等待 5 分钟...")
                time.sleep(300)
                
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                time.sleep(60)

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    
    monitor = OnChainMonitor()
    if monitor.w3:
        monitor.monitor()
