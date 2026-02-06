#!/usr/bin/env python3
"""
Polymarket 每日汇总报告生成器
整合所有扫描结果，生成每日策略报告
"""

import os
import json
import glob
from datetime import datetime, timedelta

class DailyReportGenerator:
    """
    每日报告生成器
    """
    
    def __init__(self):
        self.report_dir = "/root/clawd/reports"
        self.today = datetime.now().strftime("%Y%m%d")
        
    def load_reports(self, date_str: str = None):
        """
        加载指定日期的所有报告
        """
        if date_str is None:
            date_str = self.today
        
        date_dir = os.path.join(self.report_dir, date_str)
        
        if not os.path.exists(date_dir):
            print(f"❌ 未找到 {date_str} 的报告目录")
            return [], []
        
        # 加载套利报告
        arbitrage_files = glob.glob(os.path.join(date_dir, "arbitrage_*.json"))
        
        # 加载市场监控
        monitor_files = glob.glob(os.path.join(date_dir, "market_snapshot_*.json"))
        
        return arbitrage_files, monitor_files
    
    def generate_daily_summary(self):
        """
        生成每日汇总
        """
        arbitrage_files, monitor_files = self.load_reports()
        
        print(f"📊 生成每日汇总报告: {self.today}")
        print(f"   套利报告: {len(arbitrage_files)} 个")
        print(f"   监控报告: {len(monitor_files)} 个")
        
        # 汇总数据
        total_opportunities = 0
        all_markets = set()
        
        for arb_file in arbitrage_files:
            try:
                with open(arb_file, 'r') as f:
                    data = json.load(f)
                    total_opportunities += data.get("total_opportunities", 0)
            except:
                pass
        
        for mon_file in monitor_files:
            try:
                with open(mon_file, 'r') as f:
                    data = json.load(f)
                    trending = data.get("trending_markets", [])
                    for m in trending:
                        all_markets.add(m.get("question", ""))
            except:
                pass
        
        # 生成报告
        report_file = f"/root/clawd/DAILY_REPORT_{self.today}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 Polymarket 每日策略报告\n\n")
            f.write(f"**日期**: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%H:%M:%S')}\n\n")
            f.write(f"---\n\n")
            
            # 执行摘要
            f.write(f"## 📈 执行摘要\n\n")
            f.write(f"| 指标 | 数值 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 扫描次数 | {len(arbitrage_files)} 次 |\n")
            f.write(f"| 发现机会 | {total_opportunities} 个 |\n")
            f.write(f"| 监控市场 | {len(all_markets)} 个 |\n")
            f.write(f"| 扫描时间 | 24 小时 |\n\n")
            
            # 策略建议
            f.write(f"## 🎯 策略建议\n\n")
            
            if total_opportunities > 0:
                f.write(f"✅ **今日发现 {total_opportunities} 个套利机会**\n")
                f.write(f"   建议: 查看详细报告，评估风险后小资金测试\n\n")
            else:
                f.write(f"⚠️ **今日未发现明显套利机会**\n")
                f.write(f"   建议: 继续监控，等待市场波动\n\n")
            
            f.write(f"## 📁 今日报告文件\n\n")
            f.write(f"### 套利扫描报告\n")
            for arb in arbitrage_files:
                filename = os.path.basename(arb)
                f.write(f"- `{filename}`\n")
            
            f.write(f"\n### 市场监控报告\n")
            for mon in monitor_files:
                filename = os.path.basename(mon)
                f.write(f"- `{filename}`\n")
            
            f.write(f"\n## 🔍 明日关注\n\n")
            f.write(f"- [ ] 继续监控 Trump 相关市场\n")
            f.write(f"- [ ] 关注 NBA/NFL 赛事市场\n")
            f.write(f"- [ ] 检查加密货币价格波动\n")
            f.write(f'- [ ] 寻找"不可能事件"机会\n\n')
            
            f.write(f"---\n\n")
            f.write(f"*本报告由 Polymarket 自动化系统生成*\n")
            f.write(f"*下次更新: {datetime.now().strftime('%Y-%m-%d')} 02:00*\n")
        
        print(f"✅ 每日汇总报告已生成: {report_file}")
        return report_file

def main():
    generator = DailyReportGenerator()
    report_file = generator.generate_daily_summary()
    
    if report_file:
        print(f"\n📄 报告位置: {report_file}")

if __name__ == "__main__":
    main()
