# Kimi Code 使用指南

## ✅ 安装完成

Kimi Code 已成功配置为编程助手！

## 🚀 使用方法

### 方法 1：命令行直接调用

```bash
# 生成代码
kimi-code generate "Write a Python function to calculate fibonacci numbers"

# 审查代码
kimi-code review myscript.py
```

### 方法 2：Python 脚本中调用

```python
import sys
sys.path.insert(0, '/usr/lib/node_modules/clawdbot/skills/kimi-code/scripts')
from kimi_code import generate_code, review_code

# 生成代码
code = generate_code("Create a web scraper using requests and BeautifulSoup")
print(code)

# 审查代码
with open('mycode.py') as f:
    feedback = review_code(f.read())
print(feedback)
```

### 方法 3：在 Clawdbot 任务中使用

当你需要编程时，我会自动使用 Kimi API：

```python
# 调用 Kimi 进行代码生成
exec(command="kimi-code generate 'Your programming task here'")
```

## 🔧 配置检查

环境变量：`KIMI_API_KEY` ✅ 已设置
API Key：`sk-kimi-uhznedo5UWHEYqfpS...` ✅
Base URL：`https://api.moonshot.cn/v1` ✅

## 💡 示例任务

### 示例 1：生成 Python 脚本
```bash
kimi-code generate "Write a Python script to download images from a URL list"
```

### 示例 2：代码审查
```bash
kimi-code review /path/to/your/code.py
```

### 示例 3：在对话中使用
直接告诉我：
> "用 Kimi 帮我写一个数据清洗的 Python 脚本"

我会自动调用 Kimi Code 生成代码！

## 🎯 优势

- ✅ **中文友好**：Kimi 对中文支持极好
- ✅ **代码质量高**：生成干净、规范的代码
- ✅ **上下文理解强**：适合复杂编程任务
- ✅ **无需翻墙**：国内 API 访问稳定

## 📚 文档

- Kimi 官方文档：https://platform.moonshot.cn
- API 参考：https://platform.moonshot.cn/docs

---

**Kimi Code 已就绪！开始编程吧！** 🌙✨
