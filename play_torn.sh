#!/bin/bash
# Torn 自动游戏启动器

echo "=========================================="
echo "🎮 Torn 自动游戏系统"
echo "=========================================="
echo ""

# 检查 API Key
if [ ! -f "torn_config.json" ]; then
    echo "{\"api_key\": \"BRKuCVqYU8k53mAA\"}" > torn_config.json
fi

echo "👤 玩家: claw101"
echo "🔑 API: 已配置"
echo ""

# 显示菜单
echo "请选择游戏模式:"
echo ""
echo "1. 快速游戏一次 (立即执行)"
echo "2. 自动定时游戏 (每30分钟一次)"
echo "3. 智能代理模式 (AI决策)"
echo "4. 查看游戏状态"
echo "5. 查看统计数据"
echo "6. 停止自动游戏"
echo ""
echo "0. 退出"
echo ""
read -p "选择 (0-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动快速游戏..."
        python3 torn_auto_player.py quick
        ;;
    2)
        echo ""
        echo "⏰ 启动自动定时游戏..."
        echo "将在后台运行，每30分钟执行一次"
        echo "查看日志: tail -f torn_agent.log"
        echo ""
        nohup python3 torn_auto_player.py auto > torn_game.log 2>&1 &
        echo $! > torn_game.pid
        echo "✅ 自动游戏已启动 (PID: $(cat torn_game.pid))"
        ;;
    3)
        echo ""
        echo "🤖 启动智能代理..."
        python3 torn_game_agent.py
        ;;
    4)
        echo ""
        echo "📊 获取当前状态..."
        python3 -c "
import requests
API_KEY = 'BRKuCVqYU8k53mAA'
resp = requests.get('https://api.torn.com/user/', 
    params={'key': API_KEY, 'selections': 'bars,money,basic'})
data = resp.json()
print(f\"玩家: {data.get('name')}\")
print(f\"等级: {data.get('level')}\")
bars = data.get('bars', {})
print(f\"能量: {bars.get('energy', {}).get('current', 0)}\")
print(f\"勇气: {bars.get('nerve', {}).get('current', 0)}\")
print(f\"生命: {bars.get('life', {}).get('current', 0)}\")
print(f\"现金: \${data.get('money_onhand', 0):,}\")
"
        ;;
    5)
        echo ""
        echo "📈 游戏统计:"
        if [ -f "torn_game_data.json" ]; then
            cat torn_game_data.json | python3 -m json.tool
        else
            echo "暂无统计数据"
        fi
        ;;
    6)
        echo ""
        if [ -f "torn_game.pid" ]; then
            PID=$(cat torn_game.pid)
            kill $PID 2>/dev/null
            rm -f torn_game.pid
            echo "🛑 自动游戏已停止"
        else
            echo "⚠️  自动游戏未在运行"
        fi
        ;;
    0)
        echo ""
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ 无效选择"
        ;;
esac

echo ""
