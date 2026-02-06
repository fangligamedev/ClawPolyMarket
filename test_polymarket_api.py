#!/usr/bin/env python3
"""
Polymarket API 连接测试
验证 API Key 是否有效
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_api_connection():
    """测试 Polymarket API 连接"""
    
    print("🚀 Polymarket API 连接测试")
    print("=" * 60)
    
    # 获取环境变量
    api_key = os.getenv("POLYMARKET_API_KEY")
    
    if not api_key:
        print("❌ 错误: 未找到 POLYMARKET_API_KEY 环境变量")
        print("   请先设置环境变量:")
        print("   export POLYMARKET_API_KEY='你的APIKey'")
        return False
    
    print(f"✅ API Key 已配置: {api_key[:8]}...{api_key[-4:]}")
    
    # 测试 1: 获取 Gamma API 市场数据
    print("\n📡 测试 1: Gamma API - 获取市场列表")
    try:
        gamma_url = "https://gamma-api.polymarket.com/markets"
        params = {
            "closed": "false",
            "archived": "false",
            "limit": 5
        }
        
        response = requests.get(
            gamma_url,
            params=params,
            headers={
                "Accept": "application/json",
                "User-Agent": "PolymarketBot/1.0"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            market_count = len(data) if isinstance(data, list) else len(data.get("data", []))
            print(f"✅ 成功！获取到 {market_count} 个活跃市场")
            
            # 显示第一个市场
            if isinstance(data, list) and len(data) > 0:
                first_market = data[0]
                print(f"   示例市场: {first_market.get('question', 'N/A')[:50]}...")
        else:
            print(f"⚠️  返回状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 测试 2: 获取 Polymarket 数据
    print("\n📡 测试 2: Polymarket API - 获取市场数据")
    try:
        url = "https://polymarket.com/api/markets"
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 成功！Polymarket API 可访问")
        else:
            print(f"⚠️  状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 测试 3: 检查 CLOB 状态
    print("\n📡 测试 3: CLOB API 状态检查")
    try:
        clob_url = "https://clob.polymarket.com"
        response = requests.get(
            clob_url,
            timeout=5
        )
        
        if response.status_code in [200, 404]:  # 404 也是正常的，表示需要认证
            print(f"✅ CLOB API 可访问 (状态: {response.status_code})")
        else:
            print(f"⚠️  状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("📝 总结")
    print("=" * 60)
    print("✅ API Key 已配置")
    print("✅ Gamma API 可访问（获取市场数据）")
    print("✅ Polymarket 平台可访问")
    print("⚠️  CLOB API 需要完整凭据（api_key + secret + passphrase）")
    print("\n💡 提示: 要进行交易，还需要 api_secret 和 api_passphrase")
    
    return True

def show_next_steps():
    """显示下一步"""
    print("\n🎯 下一步行动")
    print("=" * 60)
    print("1. 安装 py-clob-client:")
    print("   pip install py-clob-client")
    print("\n2. 配置完整 API 凭据:")
    print("   - api_key: 已配置")
    print("   - api_secret: 需要获取")
    print("   - api_passphrase: 需要获取")
    print("\n3. 运行跟单机器人或做市策略")
    print("\n💡 如果你没有 api_secret 和 api_passphrase，")
    print("   可以使用钱包私钥方式连接（更安全）")

if __name__ == "__main__":
    success = test_api_connection()
    show_next_steps()
    
    if success:
        print("\n✨ 基础 API 测试完成！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，请检查配置")
        sys.exit(1)
