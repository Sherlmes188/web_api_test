# 🏢 TikTok官方API注册和使用指南

## 📋 概述

TikTok官方API（TikTok for Developers）提供了更可靠、更官方的数据访问方式。虽然申请过程相对复杂，但具有以下优势：

### ✅ 官方API优势
- **数据准确性最高** - 直接来源于TikTok官方
- **功能更全面** - 支持更多数据字段和操作
- **长期稳定** - 官方维护，不会突然停止服务
- **合规性** - 符合TikTok官方政策

### ❌ 限制
- **申请审核** - 需要开发者审核（1-2周）
- **商业用途** - 主要面向商业和企业用户
- **OAuth认证** - 需要用户授权，流程较复杂

## 🚀 申请步骤

### 第1步：注册TikTok开发者账号

1. **访问开发者平台**
   - 网址：https://developers.tiktok.com/
   - 点击 "Get Started" 开始注册

2. **创建开发者账号**
   - 使用你的TikTok账号登录
   - 或使用邮箱注册新账号

3. **完善个人/公司信息**
   - **个人开发者**：提供身份证明
   - **企业开发者**：提供营业执照等

### 第2步：提交应用申请

1. **创建新应用**
   - 在Dashboard点击 "Create App"
   - 填写应用基本信息

2. **应用信息要求**
   ```
   应用名称：TikTok Data Analytics Dashboard
   应用描述：用于TikTok视频数据分析和统计的仪表板
   应用类型：Analytics & Data
   用户类型：Creator/Business
   ```

3. **技术信息**
   ```
   平台：Web Application
   回调URL：http://localhost:5000/callback
   域名：localhost (开发环境)
   ```

### 第3步：申请API权限

选择需要的API权限范围：

#### 📊 数据分析相关权限
- **user.info.basic** - 基本用户信息
- **user.info.profile** - 用户档案信息
- **user.info.stats** - 用户统计数据
- **video.list** - 视频列表
- **video.info** - 视频详细信息

#### 📈 分析权限
- **research.adlib.basic** - 广告库基础访问
- **research.data.basic** - 研究数据基础访问

### 第4步：等待审核

- **审核时间**：通常1-2周
- **审核标准**：
  - 应用的合法性和合规性
  - 商业用途的合理性
  - 数据使用的透明度

## 🔧 技术集成

### 获取应用凭证

审核通过后，你将获得：
```
Client Key: your_client_key
Client Secret: your_client_secret
```

### OAuth认证流程

TikTok官方API使用OAuth 2.0认证：

1. **用户授权** - 跳转到TikTok授权页面
2. **获取授权码** - 用户同意后返回authorization code
3. **交换访问令牌** - 用code换取access token
4. **API调用** - 使用access token调用API

## 💻 代码配置

我为你创建了官方API集成代码：

### 1. 更新配置文件

```python
# config.py 添加官方API配置
class Config:
    # 官方API配置
    TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY') or None
    TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET') or None
    TIKTOK_REDIRECT_URI = "http://localhost:5000/callback"
    
    # OAuth配置
    TIKTOK_OAUTH_URL = "https://www.tiktok.com/auth/authorize/"
    TIKTOK_TOKEN_URL = "https://open-api.tiktok.com/oauth/access_token/"
    
    @classmethod
    def has_official_api_config(cls):
        return cls.TIKTOK_CLIENT_KEY and cls.TIKTOK_CLIENT_SECRET
```

### 2. OAuth认证流程

```python
# oauth_handler.py
import requests
from config import Config

class TikTokOAuth:
    def __init__(self):
        self.client_key = Config.TIKTOK_CLIENT_KEY
        self.client_secret = Config.TIKTOK_CLIENT_SECRET
        self.redirect_uri = Config.TIKTOK_REDIRECT_URI
    
    def get_auth_url(self):
        """生成授权URL"""
        auth_url = (
            f"{Config.TIKTOK_OAUTH_URL}?"
            f"client_key={self.client_key}&"
            f"scope=user.info.basic,user.info.profile,user.info.stats,video.list&"
            f"response_type=code&"
            f"redirect_uri={self.redirect_uri}&"
            f"state=your_csrf_state"
        )
        return auth_url
    
    def exchange_code_for_token(self, authorization_code):
        """用授权码换取访问令牌"""
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(Config.TIKTOK_TOKEN_URL, data=data)
        return response.json()
```

## 🔄 集成到现有面板

### 添加授权路由

在 `app.py` 中添加：

```python
@app.route('/auth')
def authorize():
    """跳转到TikTok授权页面"""
    from oauth_handler import TikTokOAuth
    oauth = TikTokOAuth()
    auth_url = oauth.get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """处理授权回调"""
    code = request.args.get('code')
    if code:
        from oauth_handler import TikTokOAuth
        oauth = TikTokOAuth()
        token_data = oauth.exchange_code_for_token(code)
        # 保存access token
        session['access_token'] = token_data.get('access_token')
        return redirect('/')
    return "授权失败"
```

### 使用官方API获取数据

```python
# tiktok_official_api.py
class TikTokOfficialAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://open-api.tiktok.com"
    
    def get_user_info(self):
        """获取用户信息"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f"{self.base_url}/v2/user/info/",
            headers=headers
        )
        return response.json()
    
    def get_user_videos(self, cursor=None, count=20):
        """获取用户视频列表"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'count': count}
        if cursor:
            params['cursor'] = cursor
            
        response = requests.get(
            f"{self.base_url}/v2/video/list/",
            headers=headers,
            params=params
        )
        return response.json()
```

## 🎯 申请技巧

### 提高申请成功率

1. **明确商业用途**
   - 详细说明数据分析的目的
   - 展示专业的应用界面
   - 提供完整的技术文档

2. **展示合规性**
   - 说明数据隐私保护措施
   - 遵守TikTok社区准则
   - 明确数据使用范围

3. **提供完整信息**
   - 详细的应用描述
   - 清晰的技术架构
   - 预期的用户群体

### 申请材料准备

```
📄 必需材料：
- 应用截图和演示
- 技术架构文档
- 数据使用说明
- 隐私政策文档
- 商业计划概述

🏢 企业用户额外需要：
- 营业执照
- 公司介绍
- 技术团队信息
```

## 🚨 注意事项

### API使用限制
- **请求频率限制** - 每分钟/小时有调用次数限制
- **数据访问范围** - 只能访问授权用户的数据
- **地区限制** - 某些地区可能有访问限制

### 费用说明
- **个人开发者** - 基础版免费，有调用次数限制
- **商业用户** - 根据调用量收费
- **企业版** - 联系TikTok销售团队

## 📞 获取帮助

- **开发者文档**：https://developers.tiktok.com/doc/
- **API参考**：https://developers.tiktok.com/doc/tiktok-api-reference/
- **开发者论坛**：https://developers.tiktok.com/community/
- **技术支持**：通过开发者平台提交工单

---

## 🚀 快速开始

1. **立即申请**：访问 https://developers.tiktok.com/
2. **准备材料**：按照上述清单准备申请材料
3. **提交申请**：填写详细的应用信息
4. **等待审核**：通常1-2周获得结果
5. **集成API**：使用上述代码示例

**💡 建议**：在等待审核期间，可以先使用TikAPI进行开发和测试，审核通过后再切换到官方API。 