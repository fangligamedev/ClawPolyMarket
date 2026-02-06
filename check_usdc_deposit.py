#!/usr/bin/env python3
"""
检查 USDC 存入状态
"""

import os
from py_clob_client.client import ClobClient

def check_deposit():
    """检查账户余额"""
    
    # 初始化客户端 (只读模式)
    host = "https://clob.polymarket.com"
    
    try:
        client = ClobClient(host)
        
        # 如果有 API Key，检查余额
        if os.getenv('POLYMARKET_API_KEY'):
            client.set_api_creds(
                api_key=os.getenv('POLYMARKET_API_KEY'),
                api_secret=os.getenv('POLYMARKET_API_SECRET'),
                api_passphrase=os.getenv('POLYMARKET_API_PASSPHRASE')
            )
            
            balance = client.get_balance()
            print(f"💰 账户余额: ${balance} USDC")
            
            if balance >= 1000:
                print("✅ USDC 存入完成！")
                return True
            else:
                print(f"⏳ 当前余额不足，还需存入: ${1000 - balance} USDC")
                return False
        else:
            print("⚠️  未配置 API Key，无法检查余额")
            print("    请先设置 POLYMARKET_API_KEY")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    check_deposit()
