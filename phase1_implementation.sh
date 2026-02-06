#!/bin/bash
# Phase 1 实施脚本 - USDC 存入和测试交易
# 运行: bash phase1_implementation.sh

echo "=========================================="
echo "🚀 Phase 1 实施: USDC 存入和测试交易"
echo "=========================================="
echo ""

# 检查环境
echo "📋 步骤 1: 环境检查"
echo "------------------------------"

# 检查 API 配置
if [ -z "$POLYMARKET_API_KEY" ]; then
    echo "⚠️  警告: POLYMARKET_API_KEY 未设置"
    echo "    请先设置环境变量"
else
    echo "✅ Polymarket API Key 已配置"
fi

echo ""
echo "📋 步骤 2: 检查当前系统状态"
echo "------------------------------"

# 检查运行的进程
echo "运行中的监控进程:"
ps aux | grep -E "twitter_signal_monitor|data_integration_hub" | grep -v grep | wc -l
echo "个进程正在运行"

echo ""
echo "📋 步骤 3: 准备存入 USDC"
echo "------------------------------"
echo ""
echo "💡 USDC 存入步骤:"
echo ""
echo "1️⃣  从交易所购买 USDC"
echo "    - 推荐: Binance, OKX, Bybit"
echo "    - 金额: $1,000 USDC"
echo "    - 网络: ERC-20 或 BEP-20"
echo ""
echo "2️⃣  准备 ETH 作为 Gas 费"
echo "    - 金额: ~$50 (Polygon 网络)"
echo "    - 网络: Polygon"
echo ""
echo "3️⃣  桥接 USDC 到 Polygon"
echo "    选项 A: 官方桥 (bridge.Polygon)"
echo "    选项 B: 第三方桥 (Stargate, Bungee)"
echo ""
echo "4️⃣  验证到账"
echo "    - 查询 Polygon 地址余额"
echo "    - 确认 USDC 到账"
echo ""
echo "⚠️  注意: 此步骤需要你手动操作"
echo "    我无法直接操作你的钱包"
echo ""

# 创建存入检查脚本
cat > /root/clawd/check_usdc_deposit.py << 'EOF'
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
EOF

echo "📋 步骤 4: 创建测试交易脚本"
echo "------------------------------"

cat > /root/clawd/test_trade.py << 'EOF'
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
EOF

echo "✅ 测试交易脚本已创建"
echo ""

# 创建存入指南
cat > /root/clawd/USDC_DEPOSIT_CHECKLIST.md << 'EOF'
# USDC 存入检查清单

## ✅ 存入步骤

### 1. 购买 USDC
- [ ] 从交易所 (Binance/OKX/Bybit) 购买 $1,000 USDC
- [ ] 同时准备 ~$50 ETH 作为 Gas 费

### 2. 准备钱包
- [ ] 确保钱包支持 Polygon 网络
- [ ] 推荐: MetaMask
- [ ] 添加 Polygon 网络配置

### 3. 桥接 USDC
- [ ] 访问 https://portal.polygon.technology/bridge
- [ ] 连接钱包
- [ ] 选择从 Ethereum 到 Polygon
- [ ] 输入金额 $1,000
- [ ] 确认交易
- [ ] 等待 ~10-30 分钟

### 4. 验证到账
- [ ] 在 Polygon 浏览器查看余额
- [ ] 运行检查脚本: python3 check_usdc_deposit.py

### 5. 配置 API
- [ ] 获取 Polymarket API Key
- [ ] 设置环境变量
- [ ] 测试 API 连接

## ⚠️ 安全提醒

- 小额测试: 首次交易建议 $10
- Gas 费: 保留足够 ETH 支付交易费
- 私钥: 永远不要分享私钥
- 备份: 保存好钱包助记词

## 📞 支持

遇到问题联系大Q协助
EOF

echo "✅ 存入检查清单已创建"
echo ""

echo "=========================================="
echo "📊 Phase 1 准备完成！"
echo "=========================================="
echo ""
echo "下一步行动:"
echo ""
echo "1. 手动从交易所购买 USDC ($1,000)"
echo "2. 桥接到 Polygon 网络"
echo "3. 运行: python3 check_usdc_deposit.py"
echo "4. 配置 Polymarket API"
echo "5. 运行: python3 test_trade.py"
echo ""
echo "📚 参考文档:"
echo "   - DEVELOPMENT_PLAN.md - 完整开发计划"
echo "   - USDC_DEPOSIT_GUIDE.md - 存入指南"
echo "   - USDC_DEPOSIT_CHECKLIST.md - 检查清单"
echo ""
echo "⚠️  注意: USDC 存入需要你手动操作钱包"
echo "    我无法直接访问你的资金"
echo ""
echo "🚀 准备好后告诉我，协助你完成测试交易！"
echo "=========================================="
