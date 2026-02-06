# Discord / Telegram 通知配置指南

## 🎯 快速配置 Discord 通知

### 步骤 1: 创建 Discord Webhook

1. 打开 Discord，进入你的服务器
2. 右键点击频道 → **编辑频道**
3. 点击 **集成** → **Webhooks**
4. 点击 **新建 Webhook**
5. 命名: `Polymarket Signals`
6. 复制 Webhook URL

### 步骤 2: 配置环境变量

```bash
export DISCORD_WEBHOOK="https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz"
```

### 步骤 3: 测试通知

```bash
python3 data_integration_hub.py
```

---

## 📱 Telegram 通知配置

### 步骤 1: 创建 Telegram Bot

1. 打开 Telegram，搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示命名机器人（如: `PolymarketSignalBot`）
4. 获取 **Bot Token**（格式: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 步骤 2: 获取 Chat ID

1. 向你的机器人发送一条消息
2. 访问: `https://api.telegram.org/bot<你的Token>/getUpdates`
3. 找到 `"chat":{"id":123456789` 这就是 Chat ID

### 步骤 3: 配置环境变量

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

---

## 🚀 启动完整数据集成系统

### 方法 1: 直接运行

```bash
cd /root/clawd

# 配置通知
export DISCORD_WEBHOOK="你的Webhook地址"
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"

# 启动
python3 data_integration_hub.py
```

### 方法 2: 后台运行

```bash
# 使用 screen
screen -dmS data_integration bash -c "cd /root/clawd && python3 data_integration_hub.py"

# 查看日志
tail -f data_integration.log
```

---

## 📊 监控的数据源

### 1. Twitter 监控
- **@0xCristal** - 交易信号
- **@Polymarket** - 官方动态
- **@PolymarketWhale** - 鲸鱼动向

监控关键词: bought, sold, long, short, position, polymarket

### 2. FiveThirtyEight 民调
- Trump vs Biden 支持率
- 各州选举预测
- 与 Polymarket 价格对比

### 3. ESPN 体育数据
- NBA 伤病报告
- NFL 伤病报告
- 重要新闻（交易、停赛等）

---

## 🔔 通知触发条件

### Twitter 信号
- 置信度 > 70/100
- 包含交易关键词
- 提及具体市场

### 民调偏差
- 民调与市场定价偏差 > 5%
- 关键摇摆州数据更新

### 体育新闻
- 明星球员伤病
- 阵容变化
- 比赛延期

---

## ⚙️ 配置文件示例

创建 `.env` 文件:

```bash
# Discord
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=123456789

# Twitter (如果使用 API)
TWITTER_BEARER_TOKEN=...

# Polymarket
POLYMARKET_API_KEY=...
POLYMARKET_API_SECRET=...
POLYMARKET_API_PASSPHRASE=...
```

---

## 🛠️ 故障排除

### Discord 通知不工作
- 检查 Webhook URL 是否正确
- 确认频道权限设置
- 查看日志错误信息

### Telegram 通知不工作
- 验证 Bot Token 是否有效
- 确认已向 Bot 发送过消息
- 检查 Chat ID 是否正确

### 数据源获取失败
- 检查网络连接
- 确认目标网站可访问
- 查看是否有 IP 限制

---

## 📈 预期输出示例

### Discord 通知
```
🚨 交易信号 detected!

Twitter Signal from @0xCristal

Just bought $5000 "Will Trump win 2024" on Polymarket 
at 45¢. Analysis shows real probability 60%+.

Source: Twitter
Confidence: 85/100
Time: 2026-02-06 15:30:00
```

### Telegram 通知
```
🚨 交易信号 detected!

538 Poll Divergence Detected

National poll: Biden 48% vs Trump 45%
Polymarket price: Biden 42% vs Trump 58%
Divergence: 6% on Biden

Confidence: 75/100
Time: 2026-02-06 15:35:00
```

---

## 🎯 下一步

1. ✅ 配置 Discord Webhook
2. ✅ 配置 Telegram Bot
3. ✅ 启动数据集成系统
4. ⏳ 等待第一个交易信号
5. 🚀 根据信号执行交易

---

**系统已准备就绪，等待配置通知渠道！** 🦞
