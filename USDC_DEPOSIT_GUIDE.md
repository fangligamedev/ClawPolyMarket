# 💰 Polymarket USDC 存入完整指南

**最后更新**: 2026-02-06  
**适用对象**: Polymarket 新用户  
**建议存入金额**: $500 - $1,000（起始测试）

---

## 📋 准备工作

### 你需要准备

1. ✅ Polymarket 账户（已注册）
2. ✅ MetaMask 或其他 Web3 钱包
3. ✅ 交易所账户（Binance、Coinbase、OKX 等）
4. ✅ 少量 ETH（作为 Gas 费）

---

## 🛣️ 存入路径概览

```
交易所/法币 → 购买 USDC → 提现到钱包 → 跨链到 Polygon → 存入 Polymarket
```

---

## 步骤 1: 购买 USDC

### 选项 A: 通过中心化交易所（推荐新手）

#### Binance
1. 登录 Binance 账户
2. 点击 **"买币"** → **"C2C 交易"** 或 **"快捷买币"**
3. 选择 **USDC**
4. 输入购买金额（建议 $500-1000）
5. 完成支付，USDC 将存入你的 Binance 钱包

#### Coinbase
1. 登录 Coinbase
2. 点击 **"Buy / Sell"**
3. 选择 **USDC**
4. 输入金额并购买
5. USDC 将存入你的 Coinbase 钱包

#### OKX
1. 登录 OKX
2. 点击 **"买币"**
3. 选择 **USDC** 和支付方式
4. 完成购买

### 选项 B: 通过去中心化交易所（适合已有加密资产）

#### Uniswap
1. 打开 https://app.uniswap.org
2. 连接钱包
3. 选择要兑换的代币 → USDC
4. 确认交易

---

## 步骤 2: 准备 Polygon 网络

### 添加 Polygon 网络到 MetaMask

1. 打开 MetaMask
2. 点击网络下拉菜单 → **"添加网络"**
3. 填写 Polygon 网络信息：

```
网络名称: Polygon Mainnet
RPC URL: https://polygon-rpc.com
链 ID: 137
货币符号: MATIC
区块浏览器: https://polygonscan.com
```

4. 点击 **"保存"**

---

## 步骤 3: 提现 USDC 到钱包

### 从 Binance 提现

1. 登录 Binance
2. 点击 **"钱包"** → **"现货钱包"**
3. 找到 **USDC**，点击 **"提现"**
4. 选择网络：**Polygon (MATIC)** ⚠️ 非常重要！
5. 打开 MetaMask，复制你的钱包地址
6. 粘贴到 Binance 提现地址栏
7. 输入提现金额（建议先小额测试 $50）
8. 确认并提交
9. 等待到账（通常 5-30 分钟）

### 从 Coinbase 提现

1. 登录 Coinbase
2. 点击 **"Send / Receive"**
3. 选择 **USDC**
4. 在 "To" 栏粘贴你的 MetaMask 地址
5. 选择网络：**Polygon** ⚠️
6. 输入金额
7. 确认并发送

### 从 OKX 提现

1. 登录 OKX
2. 点击 **"资产"** → **"提现"**
3. 选择 **USDC**
4. 选择链：**Polygon**
5. 输入你的 MetaMask 地址
6. 输入金额
7. 确认提现

---

## 步骤 4: 确认 USDC 到账

### 在 MetaMask 中查看

1. 确保网络切换到 **Polygon Mainnet**
2. 如果没有显示 USDC，需要手动添加代币：
   - 点击 **"导入代币"**
   - 代币合约地址: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
   - 代币符号: USDC
   - 小数位数: 6
3. 确认 USDC 余额显示正确

---

## 步骤 5: 存入 Polymarket

### 方法 A: 通过 Polymarket 网页（推荐）

1. 打开 https://polymarket.com
2. 点击右上角 **"Deposit"** 或 **"存入"**
3. 连接你的 MetaMask 钱包
4. 选择存入金额
5. 确认交易（需要支付少量 MATIC 作为 Gas）
6. 等待确认（通常 1-5 分钟）
7. 在 Polymarket 查看余额

### 方法 B: 通过直接转账

1. 在 Polymarket 获取你的存款地址：
   - 登录 Polymarket
   - 点击 **"Deposit"**
   - 复制显示的地址

2. 从 MetaMask 发送 USDC：
   - 打开 MetaMask
   - 确保在 Polygon 网络
   - 点击 **"发送"**
   - 粘贴 Polymarket 地址
   - 输入金额
   - 确认交易

---

## 💡 费用说明

| 步骤 | 费用 | 估计金额 |
|------|------|----------|
| 购买 USDC | 交易所手续费 | 0.1% - 1% |
| 提现到钱包 | 网络费 | ~$0.5-2 |
| 跨链桥接 | 桥接费 | ~$1-5 |
| 存入 Polymarket | Gas 费 (MATIC) | ~$0.01-0.1 |
| **总计** | | **~$2-10** |

---

## ⚠️ 重要提醒

### 安全注意事项

1. **网络选择**: 提现时一定要选择 **Polygon** 网络！
   - ❌ 不要选择 Ethereum (Gas 费太贵)
   - ❌ 不要选择 BSC 或其他网络
   - ✅ 必须选择 **Polygon (MATIC)**

2. **地址确认**: 
   - 仔细检查钱包地址
   - 建议先发送小额测试（$10-50）
   - 确认到账后再发送大额

3. **Gas 费准备**:
   - 确保钱包有少量 MATIC（0.5-1 MATIC 足够）
   - 如果没有，可以从交易所购买并提现到 Polygon 网络

### 常见问题

**Q: 为什么我的 USDC 没到账？**
- 检查网络是否正确（必须是 Polygon）
- 查看交易状态：https://polygonscan.com
- 联系交易所客服

**Q: 需要准备多少 MATIC？**
- 0.5-1 MATIC 足够多次交易
- 可以从 Binance 购买并提现到 Polygon

**Q: 存款需要多长时间？**
- 交易所提现: 5-30 分钟
- Polymarket 确认: 1-5 分钟

---

## 🚀 快速检查清单

存入前确认：

- [ ] 已购买 USDC（$500-1000）
- [ ] 已添加 Polygon 网络到 MetaMask
- [ ] 已确认 USDC 代币在 MetaMask 显示
- [ ] 钱包有少量 MATIC（Gas 费）
- [ ] 已复制正确的 Polymarket 存款地址
- [ ] 先小额测试（$50）
- [ ] 确认到账后再存入大额

---

## 📞 获取帮助

如果遇到问题：

1. **Polymarket 帮助中心**: https://help.polymarket.com
2. **Discord 社区**: https://discord.gg/Polymarket
3. **Polygon 浏览器**: https://polygonscan.com

---

## 🎯 存入后下一步

1. ✅ **验证 API 连接**（已完成）
2. ✅ **运行套利扫描**（已自动化）
3. ✅ **启动市场监控**（已自动化）
4. 🚀 **开始小额测试交易**（建议 $50-100）
5. 🚀 **部署跟单机器人**（跟随 swisstony）
6. 🚀 **启动做市策略**（赚取价差）

---

**准备好存入 USDC 后，告诉我，我帮你开始第一笔交易！** 🦞

*本指南由大Q为您准备，如有问题随时询问*
