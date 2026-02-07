#!/bin/bash
# Torn 高级自动游戏系统 v2.0 启动器
# 基于 Kimi 编程改进版

echo "=========================================="
echo "🎮 Torn 高级自动游戏系统 v2.0"
echo "基于 Kimi 编程的智能算法"
echo "=========================================="
echo ""

# 检查依赖
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 缺少依赖: $1"
        return 1
    fi
    return 0
}

echo "检查依赖..."
check_dependency python3 || exit 1
check_dependency pip3 || exit 1
echo "✅ 依赖检查通过"
echo ""

# 安装必要的 Python 包
echo "安装 Python 依赖..."
pip3 install -q requests 2>/dev/null || echo "⚠️  可能已经安装"
echo "✅ Python 依赖就绪"
echo ""

# 检查配置文件
if [ ! -f "torn_config.json" ]; then
    echo "创建配置文件..."
    cat > torn_config.json << 'EOF'
{
  "api_key": "BRKuCVqYU8k53mAA",
  "session_cookie": null,
  "mode": "demo",
  "interval_minutes": 10,
  "auto_heal": true,
  "auto_bank": true,
  "risk_level": "low"
}
EOF
    echo "✅ 配置文件已创建"
else
    echo "✅ 配置文件已存在"
fi
echo ""

# 显示菜单
echo "请选择运行模式:"
echo ""
echo "1. 🎯 演示模式 (查看智能算法)"
echo "2. 📊 状态监控 (只读取数据)"
echo "3. 🤖 智能自动 (需要Session Cookie)"
echo "4. ⚙️  配置设置"
echo "5. 📈 查看统计"
echo "6. 🛑 停止自动游戏"
echo ""
echo "0. 退出"
echo ""
read -p "选择 (0-6): " choice

case $choice in
    1)
        echo ""
        echo "🎯 启动演示模式..."
        python3 torn_advanced_bot.py demo
        ;;
    2)
        echo ""
        echo "📊 启动状态监控..."
        python3 -c "
from torn_advanced_bot import TornExecutor, GameState
import json

with open('torn_config.json') as f:
    config = json.load(f)

executor = TornExecutor(config['api_key'])
state = executor.get_state()

if state:
    print('🎮 当前游戏状态')
    print('='*50)
    print(f'👤 玩家: {state.name} (Level {state.level})')
    print(f'❤️  生命: {state.life}/100')
    print(f'🔋 能量: {state.energy}/100')
    print(f'⚡ 勇气: {state.nerve}/10')
    print(f'😊 快乐: {state.happy}/100')
    print(f'💰 现金: \${state.cash:,}')
    print(f'🏦 银行: \${state.bank:,}')
    print(f'💪 力量: {state.strength:,}')
    print(f'⚡ 速度: {state.speed:,}')
    print(f'🛡️  防御: {state.defense:,}')
    print(f'🎯 灵巧: {state.dexterity:,}')
    
    # 智能分析
    from torn_advanced_bot import TornIntelligence
    ai = TornIntelligence()
    action, params = ai.make_decision(state)
    print()
    print('🤖 智能决策:')
    print(f'  建议行动: {action.value}')
    print(f'  参数: {params}')
else:
    print('❌ 无法获取状态')
"
        ;;
    3)
        echo ""
        echo "🤖 智能自动模式"
        echo ""
        
        # 检查是否有 session cookie
        has_cookie=$(python3 -c "import json; print(json.load(open('torn_config.json'))['session_cookie'] is not None)")
        
        if [ "$has_cookie" = "False" ]; then
            echo "⚠️  缺少 Session Cookie"
            echo ""
            echo "要执行实际游戏操作，需要:"
            echo "1. 登录 https://www.torn.com"
            echo "2. 按 F12 打开开发者工具"
            echo "3. 选择 Application/Storage > Cookies"
            echo "4. 复制 PHPSESSID 的值"
            echo ""
            read -p "请输入 Session Cookie (PHPSESSID): " cookie
            
            if [ -n "$cookie" ]; then
                python3 -c "
import json
with open('torn_config.json', 'r') as f:
    config = json.load(f)
config['session_cookie'] = '$cookie'
config['mode'] = 'auto'
with open('torn_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('✅ Session Cookie 已保存')
"
            else
                echo "❌ 未提供 Cookie，退出"
                exit 1
            fi
        fi
        
        echo ""
        echo "启动智能自动游戏..."
        echo "按 Ctrl+C 停止"
        echo ""
        python3 torn_advanced_bot.py
        ;;
    4)
        echo ""
        echo "⚙️  配置设置"
        cat torn_config.json | python3 -m json.tool
        echo ""
        read -p "是否编辑配置? (y/n): " edit
        if [ "$edit" = "y" ]; then
            nano torn_config.json 2>/dev/null || vim torn_config.json 2>/dev/null || echo "请手动编辑 torn_config.json"
        fi
        ;;
    5)
        echo ""
        echo "📈 游戏统计"
        if [ -f "torn_game_data.json" ]; then
            cat torn_game_data.json | python3 -m json.tool
        else
            echo "暂无统计数据"
        fi
        ;;
    6)
        echo ""
        echo "🛑 停止自动游戏"
        pkill -f "torn_advanced_bot" 2>/dev/null
        pkill -f "torn_auto_player" 2>/dev/null
        pkill -f "torn_auto_10min" 2>/dev/null
        echo "✅ 已停止所有自动游戏进程"
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
