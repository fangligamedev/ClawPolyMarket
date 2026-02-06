# Hummingbot 做市策略指南

## 🚀 快速开始

### 1. 启动 Hummingbot
```bash
./start_hummingbot.sh
```

### 2. 首次配置
```
# 在 Hummingbot 中输入
connect polymarket

# 输入 API Key
# 输入 API Secret
# 输入 Passphrase
```

### 3. 启动策略
```
# 创建策略
create

# 选择策略: pure_market_making
# 选择交易所: polymarket
# 选择市场: TRUMP-2024
# 配置参数...

# 启动策略
start
```

## 📊 策略参数优化

### 保守型 (低风险)
```yaml
bid_spread: 0.02      # 2% 买价价差
ask_spread: 0.02      # 2% 卖价价差
order_amount: 5.0     # $5 每单
order_refresh_time: 60.0  # 60秒刷新
```

### 积极型 (中风险)
```yaml
bid_spread: 0.01      # 1% 买价价差
ask_spread: 0.01      # 1% 卖价价差
order_amount: 20.0    # $20 每单
order_refresh_time: 30.0  # 30秒刷新
```

### 激进型 (高风险)
```yaml
bid_spread: 0.005     # 0.5% 价差
ask_spread: 0.005
order_amount: 50.0    # $50 每单
order_refresh_time: 10.0  # 10秒刷新
```

## 🎯 推荐市场

### 高流动性市场 (适合做市)
1. **Trump 2024** - 交易量最大
2. **Ethereum ETF** - 流动性好
3. **NBA 比赛** - 体育事件
4. **Bitcoin ETF** - 高关注度

### 选择标准
- 日交易量 > $100K
- 价差 < 2%
- 剩余时间 > 1周

## 📈 监控指标

### 关键指标
- **填充率** (Fill Rate): > 30%
- **平均盈利** (Avg Profit): > 0.5%
- **最大回撤** (Max Drawdown): < 10%
- **夏普比率** (Sharpe Ratio): > 1.0

### 查看日志
```bash
tail -f hummingbot_files/hummingbot_logs/logs_*.log
```

### 性能监控
```bash
python3 monitor_hummingbot.py
```

## ⚠️ 风险控制

### 持仓限制
- 单个市场最大持仓: $200
- 总持仓上限: $500
- 单笔交易最大: $50

### 止损设置
- 单日最大亏损: $50
- 单市场最大亏损: $100
- 达到限制自动暂停

## 🔧 故障排除

### 连接失败
```bash
# 检查 API 配置
docker exec hummingbot cat /conf/conf_polymarket.yml

# 重启容器
./stop_hummingbot.sh
./start_hummingbot.sh
```

### 策略不执行
- 检查余额是否充足
- 检查市场是否开放
- 查看日志错误信息

### 性能问题
- 降低订单刷新频率
- 减少订单层级
- 检查网络延迟

## 🎓 进阶技巧

### 动态价差调整
根据市场波动率自动调整价差

### 多市场做市
同时在多个市场做市，分散风险

### 套利策略
结合跨市场套利，提高收益

## 📚 参考

- Hummingbot 文档: https://docs.hummingbot.org
- Polymarket API: https://docs.polymarket.com
- 策略配置: conf_pure_mm_*.yml
