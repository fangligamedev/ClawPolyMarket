#!/bin/bash
# Hummingbot 自动配置脚本

echo "========================================"
echo "🤖 Hummingbot 自动配置"
echo "========================================"
echo ""

# 检查容器是否运行
if ! docker ps | grep -q hummingbot; then
    echo "❌ Hummingbot 容器未运行"
    echo "请先运行: ./start_hummingbot.sh"
    exit 1
fi

echo "✅ Hummingbot 容器运行中"
echo ""
echo "配置步骤:"
echo "1. 连接到 Hummingbot: docker attach hummingbot"
echo "2. 创建密码"
echo "3. 连接 Polymarket: connect polymarket"
echo "4. 输入 API Key, Secret, Passphrase"
echo "5. 创建策略: create"
echo "6. 选择 pure_market_making"
echo "7. 配置参数"
echo "8. 启动: start"
echo ""
echo "💡 提示: 由于 Hummingbot 是交互式程序，需要手动配置"
echo "   请运行: docker attach hummingbot"
echo ""
echo "📚 参考: HUMMINGBOT_STRATEGY_GUIDE.md"
