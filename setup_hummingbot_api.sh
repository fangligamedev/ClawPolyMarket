#!/bin/bash
# Hummingbot API 自动配置脚本
# 运行: bash setup_hummingbot_api.sh

echo "========================================"
echo "🤖 Hummingbot API 配置向导"
echo "========================================"
echo ""

# 检查容器
if ! docker ps | grep -q hummingbot; then
    echo "❌ Hummingbot 容器未运行"
    echo "请先运行: ./start_hummingbot.sh"
    exit 1
fi

echo "✅ Hummingbot 容器运行正常"
echo ""

# 检查环境变量
if [ -z "$POLYMARKET_API_KEY" ] || [ -z "$POLYMARKET_API_SECRET" ] || [ -z "$POLYMARKET_API_PASSPHRASE" ]; then
    echo "⚠️  API 凭证未设置"
    echo ""
    echo "请提供以下信息:"
    echo "1. Polymarket API Key"
    echo "2. Polymarket API Secret"
    echo "3. Polymarket API Passphrase"
    echo ""
    echo "💡 获取方式:"
    echo "   访问 https://polymarket.com/settings/api"
    echo "   创建新的 API Key"
    echo ""
    
    # 交互式输入
    read -p "是否现在输入? (y/n): " choice
    if [ "$choice" = "y" ]; then
        read -p "API Key: " api_key
        read -p "API Secret: " api_secret
        read -p "API Passphrase: " api_passphrase
        
        # 设置环境变量
        export POLYMARKET_API_KEY="$api_key"
        export POLYMARKET_API_SECRET="$api_secret"
        export POLYMARKET_API_PASSPHRASE="$api_passphrase"
        
        echo ""
        echo "✅ 环境变量已设置"
    else
        echo "❌ 配置取消"
        echo "请设置环境变量后重新运行"
        exit 1
    fi
fi

echo ""
echo "步骤 1: 创建 Hummingbot 配置文件..."
echo "------------------------------"

# 创建 Polymarket 连接器配置
mkdir -p hummingbot_files/hummingbot_conf

cat > hummingbot_files/hummingbot_conf/conf_polymarket.yml << EOF
########################################################
###       Polymarket Connector Configuration         ###
########################################################

# API 凭证
polymarket_api_key: "$POLYMARKET_API_KEY"
polymarket_api_secret: "$POLYMARKET_API_SECRET"
polymarket_api_passphrase: "$POLYMARKET_API_PASSPHRASE"

# 其他配置
rate_limit: 10.0
timeout: 30
use_testnet: false
EOF

echo "✅ 配置文件已创建"
echo ""

echo "步骤 2: 配置文件权限..."
echo "------------------------------"
docker exec hummingbot chmod 600 /conf/conf_polymarket.yml
echo "✅ 权限已设置"
echo ""

echo "步骤 3: 配置做市策略..."
echo "------------------------------"

cat > hummingbot_files/hummingbot_conf/conf_pure_mm_polymarket.yml << EOF
########################################################
###       Pure Market Making Strategy                ###
########################################################

template_version: 24
strategy: pure_market_making

# 交易所和交易对
exchange: polymarket
market: TRUMP-2024

# 订单金额 (USDC)
order_amount: 10.0

# 买卖价差 (1% = 0.01)
bid_spread: 0.01
ask_spread: 0.01

# 最小价差
minimum_spread: 0.005

# 订单刷新时间 (秒)
order_refresh_time: 30.0

# 订单刷新容忍度
order_refresh_tolerance_pct: 0.0

# 挂单数量
order_levels: 1

# 填充后暂停 (秒)
filled_order_delay: 60.0

# 风控
max_order_size: 50.0
min_order_size: 5.0
EOF

echo "✅ 策略配置已创建"
echo ""

echo "========================================"
echo "🎉 API 配置完成!"
echo "========================================"
echo ""
echo "配置文件位置:"
echo "  - hummingbot_files/hummingbot_conf/conf_polymarket.yml"
echo "  - hummingbot_files/hummingbot_conf/conf_pure_mm_polymarket.yml"
echo ""
echo "下一步 (二选一):"
echo ""
echo "选项 A: 自动配置 (在容器内执行)"
echo "  ./auto_configure_hummingbot.sh"
echo ""
echo "选项 B: 手动配置 (交互式)"
echo "  docker attach hummingbot"
echo "  # 然后按以下步骤:"
echo "  1. 创建密码"
echo "  2. connect polymarket"
echo "  3. 输入 API Key, Secret, Passphrase"
echo "  4. create (创建策略)"
echo "  5. 选择 pure_market_making"
echo "  6. 输入策略参数"
echo "  7. start (启动策略)"
echo ""
echo "📚 参考: HUMMINGBOT_STRATEGY_GUIDE.md"
echo ""
