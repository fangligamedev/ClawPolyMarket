# 🎯 ClawPolyMarket

Polymarket 量化交易策略研究与自动化交易系统

**作者**: Mr. Bruce & 大Q  
**创建时间**: 2026-02-05  
**版本**: 2.1  
**状态**:  actively developing

---

## 📋 项目简介

本项目是基于 Polymarket 预测市场的量化交易策略研究，包含：
- 多策略套利系统
- 自动化交易框架
- 顶级交易者策略分析
- GitHub 主流生态集成

---

## 🚀 核心策略

### 1. IEA (Impossible Event Arbitrage)
不可能事件反向套利策略
- 寻找市场定价 < 15% 的机会
- 基于 browomo $5→$370万 模式
- 期望收益 > 30%

### 2. 多策略融合
- 价值发现策略 (Value)
- 高流动性套利 (Liquid)
- 动量突破策略 (Momentum)

### 3. 做市策略
基于 swisstony 高频做市模式

---

## 📁 文件结构

```
/
├── strategies/                 # 策略文件
│   ├── iea_strategy.py        # IEA 主策略
│   ├── multi_strategy_discovery.py  # 多策略发现
│   └── polymarket_strategy_engine_v2.py  # 策略引擎
│
├── scanners/                   # 扫描工具
│   ├── arbitrage_scanner.py   # 套利扫描
│   └── market_monitor.py      # 市场监控
│
├── analysis/                   # 分析报告
│   ├── 0xCristal_Strategy_Analysis.md
│   ├── trader_strategies_library.md
│   └── copy_trading_analysis.md
│
├── docs/                       # 文档
│   ├── Polymarket_Strategy_Research_Report.md
│   ├── IEA_STRATEGY_DOCUMENTATION.md
│   └── USDC_DEPOSIT_GUIDE.md
│
├── automation/                 # 自动化
│   ├── run_all_scans.sh       # 主执行脚本
│   └── cron.log              # 执行日志
│
└── README.md                   # 本文件
```

---

## 🛠️ 技术栈

### GitHub 生态集成
- ✅ `py-clob-client` - Polymarket 官方客户端
- ✅ `aiohttp` - 异步 HTTP
- ✅ `pandas/numpy` - 数据分析
- ⏳ `hummingbot` - 做市框架 (待集成)
- ⏳ `ccxt` - 多交易所 API (待集成)

### 系统架构
- Python 3.8+
- 异步编程 (asyncio)
- Cron 定时任务
- JSON 数据存储

---

## 🎯 研究成果

### 顶级交易者分析

| 交易者 | 策略 | 收益 | 可复制性 |
|--------|------|------|----------|
| swisstony | 高频做市+事件套利 | $3.65M | ⭐⭐⭐⭐ |
| browomo | 不可能事件套利 | $3.7M | ⭐⭐⭐⭐⭐ |
| DeFi_Hanzo | AI 套利自动化 | $1K/月 | ⭐⭐⭐⭐ |
| sharbel | AI 学习交易 | 92% 胜率 | ⭐⭐⭐⭐ |

### 关键洞察
- Polymarket 市场高度有效
- 纯价格套利机会稀少
- 信息优势是关键
- 需要外部数据源集成

---

## 🚀 快速开始

### 1. 环境配置
```bash
# 安装依赖
pip install py-clob-client pandas numpy aiohttp requests

# 设置环境变量
export POLYMARKET_API_KEY="your_api_key"
export POLYMARKET_API_SECRET="your_secret"
export POLYMARKET_API_PASSPHRASE="your_passphrase"
```

### 2. 运行策略
```bash
# 运行 IEA 策略
python3 iea_strategy.py

# 运行多策略发现
python3 multi_strategy_discovery.py

# 运行市场监控
python3 market_monitor.py
```

### 3. 自动化部署
```bash
# 添加定时任务
crontab -e

# 添加以下行
0 */2 * * * /root/clawd/automation/run_all_scans.sh
```

---

## 📊 系统状态

### 自动化运行时间表
```
每小时     → 市场监控
每2小时    → 套利扫描
每天3次    → IEA 策略扫描 (09:00/15:00/21:00)
每6小时    → Kimi 策略生成
每天02:00  → 生成汇总报告
```

### 当前状态
- ✅ 系统稳定运行 10+ 小时
- ✅ 扫描市场 1000+ 个/次
- ⏳ 等待发现套利机会
- ⏳ 等待存入 USDC 实战

---

## 📈 性能表现

### 扫描统计
- 市场扫描: 1000+ 个/次
- IEA 策略执行: 3 次
- 多策略执行: 2 次
- 发现机会: 0 个 (市场有效定价)

### 文件统计
- Python 脚本: 23 个
- 报告文档: 23 个
- 总代码量: ~150KB
- 磁盘占用: 1.5MB

---

## ⚠️ 风险提示

1. **市场风险**: Polymarket 交易存在风险
2. **技术风险**: 自动化系统可能出错
3. **流动性风险**: 小市场可能无法成交
4. **监管风险**: 不同地区法规不同

**只投入可承受损失的资金！**

---

## 🗺️ 路线图

### 短期 (本周)
- [ ] 启动 Twitter 信息监控
- [ ] 存入 USDC 开始实战
- [ ] 集成外部数据源

### 中期 (本月)
- [ ] 部署 Hummingbot 做市
- [ ] 接入 538 民调数据
- [ ] 建立完整风控体系

### 长期 (3个月)
- [ ] 机器学习模型
- [ ] 多策略并行优化
- [ ] 全自动交易系统

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

## 📄 许可

MIT License

---

**免责声明**: 本项目仅供研究和学习使用，不构成投资建议。交易有风险，投资需谨慎。

---

*Built with ❤️ by Mr. Bruce & 大Q* 🦞
