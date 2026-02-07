#!/bin/bash
# Torn AI 启动脚本

echo "=========================================="
echo "🚀 Torn AI 系统启动"
echo "=========================================="
echo ""

# 检查API Key
if [ ! -f "torn_config.json" ]; then
    echo "✅ 检测到API Key: BRKuCVqYU8k53mAA"
    echo "{\"api_key\": \"BRKuCVqYU8k53mAA\"}" > torn_config.json
fi

echo "📊 启动模块:"
echo ""

echo "1. 测试API连接..."
python3 -c "
import requests
API_KEY = 'BRKuCVqYU8k53mAA'
resp = requests.get('https://api.torn.com/user/', params={'key': API_KEY, 'selections': 'basic'})
data = resp.json()
if 'name' in data:
    print(f'   ✅ 连接成功: {data[\"name\"]}')
else:
    print(f'   ❌ 连接失败')
"

echo ""
echo "2. 启动AI仪表盘..."
python3 torn_ai_system.py

echo ""
echo "=========================================="
echo "✅ Torn AI 系统启动完成！"
echo "=========================================="
echo ""
echo "可用功能:"
echo "   1. torn_ai_system.py      - AI仪表盘"
echo "   2. torn_crime_optimizer.py - 犯罪优化器"
echo ""
echo "玩家: claw101 (ID: 4091163)"
echo "状态: 运行中"
echo ""
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
