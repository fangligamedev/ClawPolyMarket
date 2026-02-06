#!/bin/bash
# 检查 Hummingbot 状态

echo "========================================"
echo "🤖 Hummingbot 状态检查"
echo "========================================"
echo ""

# 检查容器
echo "1. 容器状态:"
docker ps | grep -E "CONTAINER|hummingbot" || echo "   ❌ 容器未运行"
echo ""

# 检查配置文件
echo "2. 配置文件:"
if [ -f "hummingbot_files/hummingbot_conf/conf_polymarket.yml" ]; then
    echo "   ✅ Polymarket 配置存在"
else
    echo "   ❌ Polymarket 配置不存在"
fi

if [ -f "hummingbot_files/hummingbot_conf/conf_pure_mm_polymarket.yml" ]; then
    echo "   ✅ 策略配置存在"
else
    echo "   ❌ 策略配置不存在"
fi
echo ""

# 检查日志
echo "3. 日志文件:"
ls -lh hummingbot_files/hummingbot_logs/*.log 2>/dev/null | wc -l
echo "   个日志文件"
echo ""

# 检查 API 凭证
echo "4. API 凭证:"
if [ -n "$POLYMARKET_API_KEY" ]; then
    echo "   ✅ API Key 已设置"
else
    echo "   ❌ API Key 未设置"
fi

echo ""
echo "========================================"
echo "📊 配置建议:"

if docker ps | grep -q hummingbot; then
    if [ -f "hummingbot_files/hummingbot_conf/conf_polymarket.yml" ]; then
        echo "✅ Hummingbot 已部署，配置已创建"
        echo ""
        echo "下一步: 启动策略"
        echo "  docker attach hummingbot"
        echo "  >>> start"
    else
        echo "⏳ Hummingbot 已部署，需要配置 API"
        echo ""
        echo "运行: bash setup_hummingbot_api.sh"
    fi
else
    echo "❌ Hummingbot 未运行"
    echo ""
    echo "运行: ./start_hummingbot.sh"
fi
echo "========================================"
