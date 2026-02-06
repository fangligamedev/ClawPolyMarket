# GitHub 推送说明

## ⚠️ 重要提示

GitHub 已于 2021 年 8 月停止支持密码认证，需要使用 **Personal Access Token (PAT)**。

---

## 🔑 生成 Personal Access Token 步骤

### 步骤 1: 登录 GitHub
1. 访问 https://github.com
2. 使用账号: `232831576@qq.com`
3. 使用密码: `fl@232831576`

### 步骤 2: 进入 Token 设置
1. 点击右上角头像 → **Settings**
2. 左侧菜单最下方 → **Developer settings**
3. 点击 **Personal access tokens** → **Tokens (classic)**
4. 点击 **Generate new token (classic)**

### 步骤 3: 配置 Token
- **Note**: `ClawPolyMarket Token`
- **Expiration**: 选择 `No expiration` (或自定义)
- **Scopes**: 勾选以下权限
  - ✅ `repo` (完整仓库访问)
  - ✅ `workflow` (可选，如果需要GitHub Actions)

### 步骤 4: 生成并保存
1. 点击 **Generate token**
2. **⚠️ 立即复制 Token** (只显示一次！)
3. Token 格式: `ghp_xxxxxxxxxxxxxxxxxxxx`

---

## 🚀 使用 Token 推送

### 方法 1: 命令行推送 (推荐)

```bash
# 1. 进入项目目录
cd ClawPolyMarket

# 2. 配置远程仓库 (使用 Token)
git remote set-url origin https://[TOKEN]@github.com/fangligamedev/ClawPolyMarket.git

# 例如:
git remote set-url origin https://ghp_xxxxxxxx@github.com/fangligamedev/ClawPolyMarket.git

# 3. 推送
git push -u origin master
```

### 方法 2: Git Credential Manager

```bash
# 配置 Git 记住凭据
git config --global credential.helper store

# 推送时会提示输入用户名和密码
# 用户名: 232831576@qq.com
# 密码: [你的 Personal Access Token]
git push -u origin master
```

### 方法 3: GitHub Desktop (图形界面)

1. 下载 GitHub Desktop: https://desktop.github.com/
2. 登录账号
3. 导入本地仓库
4. 点击 "Publish repository"

---

## 📦 替代方案: 直接上传文件

如果不想使用 Token，可以直接在 GitHub 网页上传：

### 步骤:
1. 访问 https://github.com/fangligamedev/ClawPolyMarket
2. 点击 **"Add file"** → **"Upload files"**
3. 将 `ClawPolyMarket_20260206.tar.gz` 解压后的文件拖入
4. 点击 **"Commit changes"**

---

## 🔧 常见问题

### Q: 为什么不能用密码？
**A**: GitHub 为了安全，已于 2021 年 8 月 13 日停止支持密码认证，必须使用 Personal Access Token。

### Q: Token 忘记了怎么办？
**A**: 无法查看已生成的 Token，只能重新生成一个新的。

### Q: Token 泄露了怎么办？
**A**: 立即在 GitHub Settings → Developer settings → Personal access tokens 中删除该 Token，然后生成新的。

---

## 📞 需要帮助？

如果以上步骤遇到问题，可以：
1. 查看 GitHub 官方文档: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
2. 联系大Q协助

---

**重要**: Personal Access Token 相当于密码，请妥善保管，不要泄露给他人！
