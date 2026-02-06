# Hummingbot 快速启动指南

## 🚀 快速配置 (3分钟)

### 前提条件
- Hummingbot 容器已运行: `docker ps | grep hummingbot`
- API 凭证已设置: `echo $POLYMARKET_API_KEY`

### 步骤 1: 进入 Hummingbot
```bash
docker attach hummingbot
```

### 步骤 2: 创建密码 (首次运行)
```
Enter your new password: ********
Confirm your new password: ********
```

### 步骤 3: 连接 Polymarket
```
>>> connect polymarket
Enter your Polymarket API key: ********************
Enter your Polymarket API secret: ********************
Enter your Polymarket passphrase: ********************
```

### 步骤 4: 创建做市策略
```
>>> create
What is your market making strategy?: pure_market_making
Enter your maker spot connector: polymarket
Enter the trading pair: TRUMP-2024
How far away from the mid price (bid_spread)?: 0.01
How far away from the mid price (ask_spread)?: 0.01
How often (order_refresh_time)?: 30
What is the amount per order?: 10
```

### 步骤 5: 启动策略
```
>>> start
```

### 步骤 6: 查看状态
```
>>> status
>>> history
```

## 📊 策略参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| bid_spread | 0.01 | 买价距离中间价 1% |
| ask_spread | 0.01 | 卖价距离中间价 1% |
| order_refresh_time | 30 | 每30秒刷新订单 |
| order_amount | 10 | 每单 $10 |
| market | TRUMP-2024 | 交易对 |

## 🎯 监控命令

```bash
# 查看日志
docker logs hummingbot -f

# 查看策略状态
docker exec -it hummingbot /bin/bash

# 停止策略
>>> stop

# 退出 (不停止容器)
Ctrl+P, Ctrl+Q
```

## ⚠️ 注意事项

1. **资金要求**: 确保 Polymarket 账户有 USDC
2. **Gas 费**: Polygon 网络需要 ETH 支付 Gas
3. **风险控制**: 首次建议使用小资金测试
4. **监控**: 定期检查策略表现

## 📈 预期收益

**保守估计** (日交易量 $1,000):
- 做市收益: 0.1-0.3% / 天
- 月收益: 3-9%
- 风险: 低 (双边做市)

---

**准备好 USDC 后，3 分钟即可启动做市！** 🚀
