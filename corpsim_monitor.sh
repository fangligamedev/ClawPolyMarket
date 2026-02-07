#!/bin/bash
# Corpsim 游戏监控汇报脚本

export PATH="$HOME/.local/bin:$PATH"
export CORPSIM_URL=https://profession-northern-cio-par.trycloudflare.com

SESSION="1d406dee-7e5b-469d-ab3e-81c41d765102"
LOG_FILE="/tmp/corpsim_watch.log"
REPORT_COUNT=0

echo "🎮 Corpsim 监控汇报系统启动"
echo "Session: $SESSION"
echo ""

while true; do
    sleep 30
    REPORT_COUNT=$((REPORT_COUNT + 1))
    
    # 获取最新状态
    STATUS=$(corpsim status session=$SESSION 2>/dev/null)
    
    # 获取最新日志
    NEW_LOGS=$(tail -10 $LOG_FILE 2>/dev/null | grep -E "System|CEO|CMO|CFO|agenda|vote|phase" | tail -5)
    
    if [ -n "$NEW_LOGS" ]; then
        echo ""
        echo "📊 Corpsim 汇报 #$REPORT_COUNT - $(date '+%H:%M:%S')"
        echo "═══════════════════════════════════"
        echo "$STATUS" | head -10
        echo ""
        echo "📝 最新动态:"
        echo "$NEW_LOGS"
        echo "═══════════════════════════════════"
    fi
done
