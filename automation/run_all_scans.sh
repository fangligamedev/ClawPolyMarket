#!/bin/bash
# Polymarket 自动化扫描系统
# 定时执行：套利扫描 + 市场监控

cd /root/clawd

# 设置环境变量
export POLYMARKET_API_KEY="019c2f1c-97ed-728f-bbb4-fb75b14dd1b5"
export POLYMARKET_API_SECRET="q_LCEJfbnGHWzT8uuRhX9Rr-y-HaDxkDlXGz9HRfw7U="
export POLYMARKET_API_PASSPHRASE="97ad8543e84fff7ae15b61bbe335a379cc22b810480cd4325596af1c60004945"

# 记录执行时间
DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$DATE] 开始执行自动化扫描..." >> /root/clawd/automation/cron.log

# 1. 运行套利扫描
echo "[$DATE] 运行套利扫描..." >> /root/clawd/automation/cron.log
python3 arbitrage_scanner.py >> /root/clawd/automation/cron.log 2>&1

# 2. 运行市场监控
echo "[$DATE] 运行市场监控..." >> /root/clawd/automation/cron.log
python3 market_monitor.py >> /root/clawd/automation/cron.log 2>&1

# 3. 整理生成的报告
echo "[$DATE] 整理报告..." >> /root/clawd/automation/cron.log
mkdir -p /root/clawd/reports/$(date +%Y%m%d)
mv /root/clawd/arbitrage_report_*.md /root/clawd/reports/$(date +%Y%m%d)/ 2>/dev/null
mv /root/clawd/market_monitor_report_*.md /root/clawd/reports/$(date +%Y%m%d)/ 2>/dev/null
mv /root/clawd/arbitrage_opportunities_*.json /root/clawd/reports/$(date +%Y%m%d)/ 2>/dev/null
mv /root/clawd/market_snapshot_*.json /root/clawd/reports/$(date +%Y%m%d)/ 2>/dev/null

echo "[$DATE] 扫描完成！" >> /root/clawd/automation/cron.log
echo "---" >> /root/clawd/automation/cron.log

