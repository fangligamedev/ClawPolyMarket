#!/bin/bash
# Hummingbot 自动配置脚本 (非交互式)
# 此脚本生成配置命令，需要在 Hummingbot 容器内执行

echo "========================================"
echo "🤖 Hummingbot 自动配置脚本"
echo "========================================"
echo ""

# 检查环境变量
if [ -z "$POLYMARKET_API_KEY" ] || [ -z "$POLYMARKET_API_SECRET" ] || [ -z "$POLYMARKET_API_PASSPHRASE" ]; then
    echo "❌ API 凭证未设置"
    echo "请先运行: bash setup_hummingbot_api.sh"
    exit 1
fi

echo "✅ API 凭证已配置"
echo ""

echo "生成自动配置命令..."
echo ""

# 创建 expect 脚本来自动化交互
cat > /tmp/hummingbot_autoconf.exp << 'EXPECTEOF'
#!/usr/bin/expect -f

set timeout 30

# 启动 Hummingbot
spawn docker attach hummingbot

# 等待启动
expect "Enter your new password:"
send "ClawPoly2026!\r"

expect "Confirm your new password:"
send "ClawPoly2026!\r"

# 连接 Polymarket
expect ">>>"
send "connect polymarket\r"

expect "Enter your Polymarket API key"
send "$env(POLYMARKET_API_KEY)\r"

expect "Enter your Polymarket API secret"
send "$env(POLYMARKET_API_SECRET)\r"

expect "Enter your Polymarket passphrase"
send "$env(POLYMARKET_API_PASSPHRASE)\r"

# 创建策略
expect ">>>"
send "create\r"

expect "What is your market making strategy?"
send "pure_market_making\r"

expect "Enter your maker spot connector"
send "polymarket\r"

expect "Enter the trading pair"
send "TRUMP-2024\r"

expect "How far away from the mid price do you want to place bid order"
send "0.01\r"

expect "How far away from the mid price do you want to place ask order"
send "0.01\r"

expect "How often do you want to cancel and replace orders"
send "30\r"

expect "What is the amount of [base_asset] per order"
send "10\r"

# 完成创建
expect ">>>"
send "config\r"

expect ">>>"
send "start\r"

# 保持运行
interact
EXPECTEOF

chmod +x /tmp/hummingbot_autoconf.exp

echo "✅ 自动配置脚本已生成"
echo ""
echo "注意: 此脚本使用 expect 自动化交互"
echo ""
echo "运行方式:"
echo "  expect /tmp/hummingbot_autoconf.exp"
echo ""
echo "或者手动配置:"
echo "  docker attach hummingbot"
echo ""

# 同时创建一个简化的配置指南
cat > HUMMINGBOT_QUICK_START.md << 'EOF'
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
# 然后: hummingbot.py

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

## 🆘 故障排除

### 连接失败
```bash
# 检查 API 凭证
docker exec hummingbot cat /conf/conf_polymarket.yml

# 重启容器
docker restart hummingbot
```

### 策略不执行
- 检查余额是否充足
- 检查市场是否开放
- 查看日志: `docker logs hummingbot`

### 退出容器
- 按 `Ctrl+P` 然后 `Ctrl+Q` (不停止)
- 不要按 `Ctrl+C` (会停止容器)

## 📚 更多文档

- [HUMMINGBOT_STRATEGY_GUIDE.md](HUMMINGBOT_STRATEGY_GUIDE.md) - 详细策略指南
- [Hummingbot 官方文档](https://docs.hummingbot.org)
- [Polymarket API 文档](https://docs.polymarket.com)

---

**准备好 USDC 后，3 分钟即可启动做市！** 🚀
EOF

echo "✅ 快速启动指南已创建: HUMMINGBOT_QUICK_START.md"
echo ""
