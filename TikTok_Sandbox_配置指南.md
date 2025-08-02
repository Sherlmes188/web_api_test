# TikTok Sandbox 环境配置指南

## 为什么需要使用Sandbox？

**问题原因**：TikTok要求验证所有redirect URL的域名所有权，而`localhost`和`127.0.0.1`无法进行域名验证。

**解决方案**：Sandbox环境专门用于开发测试，不需要验证redirect URL。

## 创建Sandbox的步骤

### 1. 登录TikTok开发者平台
访问：https://developers.tiktok.com
登录你的开发者账号

### 2. 进入你的应用管理
1. 点击右上角的 **Developer Portal**
2. 选择 **Manage apps**
3. 找到你的应用并点击进入

### 3. 创建Sandbox
1. 在应用页面顶部，找到并点击 **Sandbox** 标签
2. 点击 **Create Sandbox** 按钮
3. 填写Sandbox名称（比如：`Development Testing`）
4. **重要**：勾选 **Clone from Production or an existing Sandbox**
5. 点击 **Confirm**

### 4. 配置Sandbox设置
1. 在Sandbox环境中，确保以下产品已启用：
   - **Login Kit**
   - **Display API**（如果需要）

2. 在 **Login Kit** 配置中：
   - 设置 **Redirect URI** 为：`http://localhost:5000/callback`
   - 或者使用：`http://127.0.0.1:5000/callback`

3. 确保启用了正确的权限范围（Scopes）：
   - `user.info.basic`
   - `video.list`

### 5. 获取Sandbox凭据
1. 在Sandbox环境中，进入 **App details**
2. 在 **Credentials** 部分，复制：
   - **Client key**（沙盒专用）
   - **Client secret**（沙盒专用）

### 6. 在我们的应用中配置Sandbox凭据
1. 访问：`http://127.0.0.1:5000/config`
2. 输入Sandbox的Client Key和Client Secret
3. 点击保存

### 7. 邀请测试用户（重要！）
Sandbox环境只允许特定用户登录：

1. 在Sandbox页面，找到 **Test Users** 部分
2. 点击 **Add test user**
3. 输入要测试的TikTok账号用户名
4. 发送邀请

**注意**：只有被邀请的用户才能在Sandbox环境中进行授权测试。

## 测试流程

1. **配置完成后**：访问 `http://127.0.0.1:5000/debug`
2. **检查API状态**：确认显示"已配置但需要授权"
3. **点击授权**：现在应该能正常跳转到TikTok授权页面
4. **使用测试用户登录**：必须使用已邀请的测试账号
5. **完成授权**：授权成功后会跳转回应用

## 优势

✅ **无需域名验证**：Sandbox环境不需要验证redirect URL
✅ **完整功能测试**：可以测试完整的OAuth流程
✅ **安全隔离**：测试数据不会影响生产环境
✅ **快速部署**：立即可用，无需等待审核

## 注意事项

⚠️ **测试用户限制**：最多只能添加10个测试用户
⚠️ **功能限制**：某些高级功能可能在Sandbox中不可用
⚠️ **数据限制**：Sandbox中的数据可能有限制

## 下一步

配置完Sandbox后：
1. 测试OAuth授权流程
2. 验证数据获取功能
3. 准备生产环境部署（如果需要）

---

**需要帮助？** 如果在配置过程中遇到问题，请访问我们的调试页面：`http://127.0.0.1:5000/redirect_debug` 