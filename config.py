"""
TikTok数据分析面板配置文件
"""

import os
from typing import Optional

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # TikAPI (第三方API) 配置
    TIKAPI_KEY = os.environ.get('TIKAPI_KEY') or ''
    TIKAPI_BASE_URL = 'https://tikapi.io/api'
    
    # TikTok官方API配置 - 支持动态设置
    TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY') or ''
    TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET') or ''
    TIKTOK_REDIRECT_URI = os.environ.get('TIKTOK_REDIRECT_URI') or 'http://127.0.0.1:5000/callback'
    
    # TikTok API URLs
    TIKTOK_OAUTH_URL = 'https://www.tiktok.com/v2/auth/authorize'
    TIKTOK_TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token'
    TIKTOK_API_BASE_URL = 'https://open.tiktokapis.com/v2'
    
    # 数据更新间隔（秒）
    UPDATE_INTERVAL = 30
    
    # 运行时API配置存储
    _runtime_client_key = None
    _runtime_client_secret = None
    _runtime_redirect_uri = None
    
    @classmethod
    def set_runtime_api_config(cls, client_key, client_secret):
        """设置运行时API配置"""
        cls._runtime_client_key = client_key
        cls._runtime_client_secret = client_secret
    
    @classmethod
    def get_client_key(cls):
        """获取客户端密钥"""
        return cls._runtime_client_key or cls.TIKTOK_CLIENT_KEY
    
    @classmethod
    def get_client_secret(cls):
        """获取客户端密码"""
        return cls._runtime_client_secret or cls.TIKTOK_CLIENT_SECRET
    
    @classmethod
    def set_runtime_redirect_uri(cls, redirect_uri):
        """设置运行时重定向URI"""
        cls._runtime_redirect_uri = redirect_uri
    
    @classmethod
    def _get_auto_redirect_uri(cls):
        """根据环境自动生成回调URL"""
        # 检查是否有环境变量设置的URL
        if os.environ.get('TIKTOK_REDIRECT_URI'):
            return os.environ.get('TIKTOK_REDIRECT_URI')
        
        # 检查是否在Railway上运行
        if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
            return f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}/callback"
        
        # 检查是否在Render上运行
        if os.environ.get('RENDER_EXTERNAL_URL'):
            return f"{os.environ.get('RENDER_EXTERNAL_URL')}/callback"
        
        # 检查是否在Heroku上运行
        if os.environ.get('HEROKU_APP_NAME'):
            return f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com/callback"
        
        # 默认本地开发环境
        return cls.TIKTOK_REDIRECT_URI
    
    @classmethod
    def get_redirect_uri(cls):
        """获取重定向URI（优先使用运行时配置）"""
        return cls._runtime_redirect_uri or cls._get_auto_redirect_uri()
    
    @classmethod
    def clear_runtime_config(cls):
        """清除运行时配置"""
        cls._runtime_client_key = None
        cls._runtime_client_secret = None
        cls._runtime_redirect_uri = None
    
    @classmethod
    def has_api_config(cls):
        """检查是否有API配置"""
        return bool(cls.get_client_key() and cls.get_client_secret())
    
    @classmethod
    def has_official_api_config(cls):
        """检查是否配置了官方API"""
        return cls.has_api_config()
    
    @classmethod
    def has_third_party_api_config(cls):
        """检查是否配置了第三方API"""
        return bool(cls.TIKAPI_KEY)
    
    @classmethod
    def get_api_key(cls):
        """获取第三方API密钥"""
        return cls.TIKAPI_KEY
    
    @classmethod
    def get_api_type(cls):
        """获取当前API类型"""
        if cls.has_official_api_config():
            return 'official'
        elif cls.has_third_party_api_config():
            return 'third_party'
        else:
            return 'none'

# API服务配置
API_SERVICES = {
    'tikapi': {
        'name': 'TikAPI',
        'base_url': 'https://api.tikapi.io',
        'endpoints': {
            'user_info': '/public/check',
            'user_videos': '/public/posts',
            'video_info': '/public/video',
            'trending': '/public/explore'
        },
        'auth_header': 'X-API-KEY',
        'docs_url': 'https://tikapi.io/documentation/',
        'signup_url': 'https://tikapi.io/'
    },
    'official': {
        'name': 'TikTok Official API',
        'base_url': 'https://open-api.tiktok.com',
        'endpoints': {
            'user_info': '/v2/user/info/',
            'user_videos': '/v2/video/list/',
            'video_info': '/v2/video/query/'
        },
        'auth_header': 'Authorization',
        'docs_url': 'https://developers.tiktok.com/',
        'signup_url': 'https://developers.tiktok.com/'
    }
}

# 示例用户配置（用于测试）
SAMPLE_USERS = [
    'lilyachty',
    'charlidamelio', 
    'khaby.lame',
    'bellapoarch'
] 