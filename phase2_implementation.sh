#!/bin/bash
# Phase 2 实施脚本 - Hummingbot 做市框架部署
# 运行: bash phase2_implementation.sh

echo "=========================================="
echo "🤖 Phase 2 实施: Hummingbot 做市框架"
echo "=========================================="
echo ""

# 检查 Docker
echo "📋 步骤 1: 检查 Docker 环境"
echo "------------------------------"

if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装"
    docker --version
else
    echo "❌ Docker 未安装"
    echo "正在安装 Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "✅ Docker 安装完成"
fi

echo ""
echo "📋 步骤 2: 拉取 Hummingbot 镜像"
echo "------------------------------"

docker pull hummingbot/hummingbot:latest

echo ""
echo "📋 步骤 3: 创建目录结构"
echo "------------------------------"

mkdir -p hummingbot_files/hummingbot_conf
mkdir -p hummingbot_files/hummingbot_logs
mkdir -p hummingbot_files/hummingbot_data
mkdir -p hummingbot_files/hummingbot_scripts

echo "✅ 目录创建完成"
echo ""

# 创建 Hummingbot 配置文件
echo "📋 步骤 4: 创建配置文件"
echo "------------------------------"

# 创建 Polymarket 连接器配置
cat > hummingbot_files/hummingbot_conf/conf_polymarket.yml << 'EOF'
########################################################
###       Polymarket Connector Configuration         ###
########################################################

# API 凭证 (需要从环境变量或安全存储获取)
polymarket_api_key: null
polymarket_api_secret: null
polymarket_api_passphrase: null

# 测试网配置 (可选)
use_testnet: false

# 其他配置
rate_limit: 10.0
timeout: 30
EOF

# 创建做市策略配置
cat > hummingbot_files/hummingbot_conf/conf_pure_mm_1.yml << 'EOF'
########################################################
###       Pure Market Making Strategy                ###
########################################################

template_version: 24
strategy: pure_market_making

# 交易所和交易对
exchange: polymarket
market: TRUMP-2024

# 订单金额
order_amount: 10.0

# 买卖价差 (1% = 0.01)
bid_spread: 0.01
ask_spread: 0.01

# 最小价差
minimum_spread: 0.005

# 订单刷新时间 (秒)
order_refresh_time: 30.0

# 订单刷新容忍度
order_refresh_tolerance_pct: 0.0

# 挂单数量
order_levels: 1

# 订单量倍增
order_level_amount: 0

# 订单间距
order_level_spread: 0.01

# 填充后暂停
filled_order_delay: 60.0

# 挂单取消时间
hang_orders_enabled: false
hang_orders_cancel_pct: 0.1

# 交易前检查
order_optimization_enabled: false
ask_order_optimization_depth: 0
bid_order_optimization_depth: 0

# 添加交易费用
deal_to_open_source_exchange: false
deal_to_open_target_exchange: false

# 风控
risk_management: true
max_order_size: 100.0
min_order_size: 1.0
EOF

echo "✅ 配置文件创建完成"
echo ""

# 创建启动脚本
echo "📋 步骤 5: 创建启动脚本"
echo "------------------------------"

cat > start_hummingbot.sh << 'EOF'
#!/bin/bash
# 启动 Hummingbot 容器

echo "🚀 启动 Hummingbot..."

docker run -it \
  --name hummingbot \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_conf,destination=/conf/" \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_logs,destination=/logs/" \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_data,destination=/data/" \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_scripts,destination=/scripts/" \
  hummingbot/hummingbot:latest

echo "✅ Hummingbot 已启动"
EOF

chmod +x start_hummingbot.sh

cat > stop_hummingbot.sh << 'EOF'
#!/bin/bash
# 停止 Hummingbot 容器

echo "🛑 停止 Hummingbot..."
docker stop hummingbot
docker rm hummingbot
echo "✅ Hummingbot 已停止"
EOF

chmod +x stop_hummingbot.sh

echo "✅ 启动脚本创建完成"
echo ""

# 创建监控脚本
echo "📋 步骤 6: 创建监控脚本"
echo "------------------------------"

cat > monitor_hummingbot.py << 'EOF'
#!/usr/bin/env python3
"""
Hummingbot 监控脚本
实时监控做市表现
"""

import json
import time
from datetime import datetime
from pathlib import Path

def monitor_performance():
    """监控 Hummingbot 表现"""
    
    print("📊 Hummingbot 性能监控")
    print("=" * 50)
    
    log_dir = Path("hummingbot_files/hummingbot_logs")
    
    if not log_dir.exists():
        print("❌ 日志目录不存在，Hummingbot 可能未运行")
        return
    
    # 读取最新日志
    log_files = list(log_dir.glob("*.log"))
    
    if not log_files:
        print("⏳ 暂无日志文件")
        return
    
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    
    print(f"📄 监控日志: {latest_log.name}")
    print(f"⏰ 更新时间: {datetime.fromtimestamp(latest_log.stat().st_mtime)}")
    
    # 统计关键指标
    with open(latest_log, 'r') as f:
        lines = f.readlines()
    
    fills = [l for l in lines if 'filled' in l.lower()]
    orders = [l for l in lines if 'order' in l.lower()]
    errors = [l for l in lines if 'error' in l.lower()]
    
    print(f"\n📈 统计:")
    print(f"   总订单: {len(orders)}")
    print(f"   成交: {len(fills)}")
    print(f"   错误: {len(errors)}")
    
    if fills:
        print(f"\n✅ 最近成交:")
        for fill in fills[-3:]:
            print(f"   {fill.strip()}")

if __name__ == "__main__":
    while True:
        monitor_performance()
        print(f"\n⏳ {datetime.now().strftime('%H:%M:%S')} - 等待 60 秒...")
        time.sleep(60)
EOF

chmod +x monitor_hummingbot.py

echo "✅ 监控脚本创建完成"
echo ""

# 创建策略优化脚本
echo "📋 步骤 7: 创建策略优化指南"
echo "------------------------------"

cat > HUMMINGBOT_STRATEGY_GUIDE.md << 'EOF'
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
EOF

echo "✅ 策略指南创建完成"
echo ""

echo "=========================================="
echo "🤖 Phase 2 准备完成！"
echo "=========================================="
echo ""
echo "📦 已创建文件:"
echo "   - hummingbot_files/ - Hummingbot 配置目录"
echo "   - start_hummingbot.sh - 启动脚本"
echo "   - stop_hummingbot.sh - 停止脚本"
echo "   - monitor_hummingbot.py - 监控脚本"
echo "   - HUMMINGBOT_STRATEGY_GUIDE.md - 策略指南"
echo ""
echo "🚀 下一步行动:"
echo ""
echo "1. 确认 Docker 已安装: docker --version"
echo "2. 启动 Hummingbot: ./start_hummingbot.sh"
echo "3. 配置 Polymarket API 连接"
echo "4. 创建做市策略"
echo "5. 启动策略并监控"
echo ""
echo "⚠️  注意: 需要先完成 Phase 1 (USDC 存入)"
echo "    才能进行真实交易"
echo ""
echo "📚 参考文档:"
echo "   - HUMMINGBOT_STRATEGY_GUIDE.md"
echo "   - DEVELOPMENT_PLAN.md"
echo ""
echo "🎯 目标: 日交易量 > $1,000, 正收益做市"
echo "=========================================="
