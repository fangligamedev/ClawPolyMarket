#!/bin/bash
# 启动简化版数据集成系统（仅日志，无需Discord/Telegram配置）

cd /root/clawd

echo "🚀 启动简化版数据集成系统"
echo "=========================="
echo ""

# 设置环境变量（空值，使用默认值）
export DISCORD_WEBHOOK=""
export TELEGRAM_BOT_TOKEN=""
export TELEGRAM_CHAT_ID=""

# 后台启动
echo "启动数据集成中心..."
screen -dmS data_integration python3 data_integration_hub.py

echo "✅ 系统已启动"
echo ""
echo "查看实时日志:"
echo "  tail -f /root/clawd/data_integration.log"
echo ""
echo "查看screen会话:"
echo "  screen -ls"
echo "  screen -r data_integration"
