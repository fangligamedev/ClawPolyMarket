# Torn API 执行操作研究

## 核心发现

### 1. API 是只读的
根据官方文档：
> "The goal of the Torn API is to provide a fully supported and **read-only** method"

这意味着：
- ✅ API 可以获取数据（状态、金钱、属性）
- ❌ API 不能执行操作（犯罪、训练、战斗）

### 2. 执行操作的替代方案

#### 方案A: HTTP POST 请求
Torn 游戏操作通过 POST 请求实现：
```
POST https://www.torn.com/crimes.php?step=commit
POST https://www.torn.com/gym.php?step=train
```

需要：
- Session Cookie
- CSRF Token
- Form Data

#### 方案B: 浏览器自动化
使用 Selenium/Playwright 模拟真人操作
- 登录游戏
- 点击按钮
- 执行犯罪/训练

### 3. 改进算法设计

#### 智能决策系统
```python
class TornIntelligence:
    def decide_action(self, state):
        # 基于当前状态的智能决策
        if state['nerve'] >= 2 and state['life'] > 50:
            return self.select_best_crime(state)
        elif state['energy'] >= 25:
            return self.select_best_training(state)
        else:
            return self.wait_for_recovery()
    
    def select_best_crime(self, state):
        # 选择最优犯罪
        crimes = [
            {'name': 'Search for Cash', 'nerve': 2, 'reward': 50, 'risk': 'low'},
            {'name': 'Pickpocket', 'nerve': 3, 'reward': 150, 'risk': 'medium'},
        ]
        # 基于风险评估选择
        return max(crimes, key=lambda c: c['reward']/c['nerve'])
```

#### 执行系统
```python
class TornExecutor:
    def __init__(self, session_cookie):
        self.session = requests.Session()
        self.session.cookies.update(session_cookie)
    
    def execute_crime(self, crime_id):
        # 实际执行犯罪
        url = f"https://www.torn.com/crimes.php?step=commit&crime={crime_id}"
        response = self.session.post(url)
        return self.parse_result(response)
    
    def train_stat(self, stat, duration):
        # 实际执行训练
        url = "https://www.torn.com/gym.php?step=train"
        data = {'stat': stat, 'duration': duration}
        response = self.session.post(url, data=data)
        return self.parse_result(response)
```

### 4. 实施建议

#### 第一步: 获取 Session
1. 用户登录 Torn
2. 从浏览器获取 Cookie
3. 提供给我

#### 第二步: 测试执行
1. 测试简单的 GET 请求
2. 测试犯罪 POST 请求
3. 测试训练 POST 请求

#### 第三步: 自动化
1. 创建智能决策循环
2. 每10分钟检查并执行
3. 错误处理和重试机制

### 5. 风险考虑

```
⚠️ 注意:
- 频繁的 POST 请求可能触发反作弊
- 建议使用随机延迟 (2-5秒)
- 不要24/7不间断运行
- 模拟人类操作模式
```

### 6. 技术实现

需要用户提供：
1. Session Cookie (从浏览器开发者工具获取)
2. 确认允许的操作类型
3. 运行时间偏好

然后我可以创建：
- ✅ 完整的执行系统
- ✅ 智能决策算法
- ✅ 定时自动化
- ✅ 状态监控
