#!/usr/bin/env python3
"""
测试交易脚本 - 首笔真实交易
"""

import os
from py_clob_client.client import ClobClient
from py_clob_client.order_builder.constants import BUY

def test_trade():
    """执行测试交易"""
    
    print("🚀 执行测试交易")
    print("=" * 50)
    
    # 配置
    host = "https://clob.polymarket.com"
    
    try:
        # 初始化客户端
        client = ClobClient(
            host,
            key=os.getenv('POLYMARKET_PRIVATE_KEY'),
            chain_id=137,  # Polygon
            signature_type=1,
            funder=os.getenv('POLYMARKET_FUNDER')
        )
        
        # 设置 API 凭证
        client.set_api_creds(
            api_key=os.getenv('POLYMARKET_API_KEY'),
            api_secret=os.getenv('POLYMARKET_API_SECRET'),
            api_passphrase=os.getenv('POLYMARKET_API_PASSPHRASE')
        )
        
        # 检查余额
        balance = client.get_balance()
        print(f"💰 当前余额: ${balance} USDC")
        
        if balance < 10:
            print("❌ 余额不足，请先存入 USDC")
            return
        
        # 选择测试市场 (Trump 2024 - 高流动性)
        # 注意: 实际 token_id 需要通过 API 获取
        test_market = {
            'token_id': 'YOUR_TOKEN_ID',  # 需要替换为实际 ID
            'size': 10.0,  # $10
            'side': BUY
        }
        
        print(f"📊 测试市场: Trump 2024")
        print(f"💵 交易金额: $10")
        print(f"📈 交易方向: BUY (Yes)")
        
        # 创建订单
        # 注意: 这里需要实际的 token_id
        # order = client.create_order(...)
        
        print("\n⚠️  注意: 此脚本需要配置完整的 API 凭证和 token_id")
        print("    请先完成 USDC 存入和 API 配置")
        
    except Exception as e:
        print(f"❌ 交易失败: {e}")

if __name__ == "__main__":
    test_trade()
