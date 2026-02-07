#!/bin/bash
# Torn 定时任务设置脚本

echo "========================================"
echo "🕐 设置 Torn 自动游戏定时任务"
echo "========================================"
echo ""

# 检查当前 crontab
echo "当前定时任务:"
crontab -l 2>/dev/null | grep -E "torn|PLAY|report" || echo "暂无 Torn 相关任务"
echo ""

# 创建新的 crontab 内容
cat > /tmp/torn_cron.txt << 'CRONEOF'
# Torn 自动游戏定时任务
# 每30分钟执行一次游戏会话
*/30 * * * * cd /root/clawd && python3 torn_auto_player.py quick >> /root/clawd/cron_game.log 2>&1

# 每2小时汇报一次状态
0 */2 * * * cd /root/clawd && python3 slack_report.py >> /root/clawd/cron_report.log 2>&1

# 每天早8点发送详细日报
0 8 * * * cd /root/clawd && echo "Torn Daily Report $(date)\n========================\n" >> /root/clawd/daily_reports.log 2>&1 && cat torn_game_data.json >> /root/clawd/daily_reports.log 2>&1

# 每天凌晨备份数据
0 0 * * * cd /root/clawd && cp torn_game_data.json "backups/torn_game_data_$(date +\%Y\%m\%d).json" 2>/dev/null || true
CRONEOF

echo "将添加以下定时任务:"
echo ""
cat /tmp/torn_cron.txt
echo ""
read -p "确认添加这些定时任务? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    # 备份当前 crontab
    crontab -l > /tmp/cron_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || echo "# Empty" > /tmp/cron_backup.txt
    
    # 添加新任务
    (crontab -l 2>/dev/null; cat /tmp/torn_cron.txt) | crontab -
    
    echo ""
    echo "✅ 定时任务已添加！"
    echo ""
    echo "📋 任务列表:"
    crontab -l | grep -E "torn|PLAY|report" | nl
    echo ""
    echo "📊 监控命令:"
    echo "   tail -f /root/clawd/cron_game.log    # 游戏日志"
    echo "   tail -f /root/clawd/cron_report.log  # 汇报日志"
    echo "   crontab -l                           # 查看所有任务"
else
    echo ""
    echo "❌ 已取消"
fi

echo ""
echo "========================================"
