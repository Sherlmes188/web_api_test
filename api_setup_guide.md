# TikTok API 连接设置指南

## 📋 概述

要连接你的TikTok账号数据，你需要获取API访问权限。有两个主要选项：

1. **TikAPI (推荐)** - 第三方服务，更容易设置
2. **TikTok官方API** - 需要开发者审批

## 🚀 方案一：使用TikAPI（推荐）

### 1. 注册TikAPI账号
1. 访问 [TikAPI官网](https://tikapi.io/)
2. 点击 "Sign Up" 注册账号
3. 选择合适的订阅计划（有免费试用）

### 2. 获取API密钥
1. 登录TikAPI控制台
2. 在Dashboard中找到你的API Key
3. 复制API密钥

### 3. 配置API密钥

#### 方法1：环境变量（推荐）
```bash
# Windows
set TIKAPI_KEY=your_api_key_here
set TIKTOK_USERNAME=your_tiktok_username

# Linux/macOS
export TIKAPI_KEY=your_api_key_here
export TIKTOK_USERNAME=your_tiktok_username
```

#### 方法2：直接修改代码
在 `config.py` 中直接设置：
```python
TIKAPI_KEY = "your_api_key_here"
TIKTOK_USERNAME = "your_tiktok_username"
```

### 4. 重启应用
```bash
python app.py
```

## 🏢 方案二：TikTok官方API

### 1. 申请开发者账号
1. 访问 [TikTok开发者平台](https://developers.tiktok.com/)
2. 申请开发者账号（需要审批）
3. 创建应用并获取API密钥

### 2. 配置OAuth认证
官方API需要OAuth认证流程，需要用户授权。

## 🔧 测试API连接

### 1. 检查配置
```python
# 在Python控制台中运行
from config import Config
print("API Key配置:", Config.has_api_key())
print("用户名配置:", Config.TIKTOK_USERNAME)
```

### 2. 测试API调用
```python
from tiktok_api import TikTokDataFetcher

# 创建API客户端
fetcher = TikTokDataFetcher(api_key=Config.get_api_key())

# 测试获取用户信息
user_info = fetcher.get_user_info("your_username")
print(user_info)
```

## 🎯 配置你的账号数据

### 1. 设置用户名
在配置中设置你的TikTok用户名：
```python
TIKTOK_USERNAME = "your_tiktok_username"
```

### 2. 修改数据源
编辑 `app.py`，将模拟数据替换为真实API调用：

```python
def update_data():
    """更新数据并通过WebSocket发送"""
    global current_data
    
    # 使用真实API数据
    if Config.has_api_key() and Config.TIKTOK_USERNAME:
        try:
            analytics_data = tiktok_fetcher.get_analytics_data(
                username=Config.TIKTOK_USERNAME
            )
            current_data = convert_analytics_to_display_format(analytics_data)
        except Exception as e:
            print(f"API调用失败，使用模拟数据: {e}")
            current_data = generate_sample_data()
    else:
        current_data = generate_sample_data()
    
    # 通过WebSocket发送更新的数据
    socketio.emit('data_update', {'data': current_data}, broadcast=True)
    print(f"数据更新于: {datetime.datetime.now()}")
```

## 📊 数据字段映射

你需要创建一个函数将API返回的数据转换为面板需要的格式：

```python
def convert_analytics_to_display_format(analytics_data):
    """将API数据转换为显示格式"""
    display_data = []
    
    for item in analytics_data:
        display_item = {
            'video_link': f"https://www.tiktok.com/@{item['author']}/video/{item['video_id']}",
            'product': '数据分析',  # 根据实际情况设置
            'service': 'TikTok',
            'publish_date': item['publish_time'].strftime('%Y/%m/%d'),
            'views': item['views'],
            'avg_watch_time': item['avg_watch_time'],
            'new_followers': 0,  # 需要额外API调用获取
            'completion_rate': f"{item['completion_rate']:.1f}%",
            'bounce_rate': item['bounce_rate'],
            'watch_duration': f"{item['avg_watch_time']:.1f}s",
            'gmv_max_views': '待计算',
            'performance': 1 if item['engagement_rate'] > 5 else 0
        }
        display_data.append(display_item)
    
    return display_data
```

## 🔐 安全注意事项

1. **不要在代码中硬编码API密钥**
2. **使用环境变量存储敏感信息**
3. **定期更换API密钥**
4. **监控API使用量**

## 🚨 常见问题

### API调用失败
- 检查API密钥是否正确
- 确认账号余额充足
- 检查网络连接

### 数据为空
- 确认用户名正确
- 检查账号是否为公开账号
- 验证API权限

### 超出限制
- 检查API调用频率
- 升级订阅计划
- 实现缓存机制

## 📞 获取帮助

1. **TikAPI支持**: [帮助文档](https://tikapi.io/documentation/)
2. **TikTok开发者**: [开发者论坛](https://developers.tiktok.com/)
3. **项目Issues**: 在GitHub创建Issue

---

配置完成后，你的面板将显示真实的TikTok账号数据！ 