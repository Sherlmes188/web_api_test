"""
TikTok官方API OAuth认证处理器
"""

import requests
import secrets
import urllib.parse
import hashlib
import base64
from typing import Dict, Optional
from config import Config

class TikTokOAuth:
    """TikTok OAuth认证处理器"""
    
    def __init__(self):
        self.client_key = Config.get_client_key()
        self.client_secret = Config.get_client_secret()
        self.redirect_uri = Config.get_redirect_uri()
        self.base_url = "https://www.tiktok.com"
        self.api_base_url = "https://open.tiktokapis.com"
    
    def generate_state(self) -> str:
        """生成CSRF状态令牌"""
        return secrets.token_urlsafe(32)
    
    def generate_pkce_pair(self) -> tuple:
        """
        生成PKCE代码验证器和挑战
        
        Returns:
            (code_verifier, code_challenge) 元组
        """
        # 生成 code_verifier (43-128个字符的随机字符串)
        code_verifier = secrets.token_urlsafe(96)  # 生成128个字符
        
        # 生成 code_challenge (code_verifier的SHA256哈希，base64编码)
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def get_auth_url(self, scopes: list = None, state: str = None) -> tuple:
        """
        生成TikTok授权URL（支持PKCE）
        
        Args:
            scopes: 权限范围列表
            state: CSRF状态令牌
            
        Returns:
            (auth_url, state, code_verifier) 元组
        """
        if not self.client_key:
            raise ValueError("未配置TikTok Client Key")
        
        if scopes is None:
            # 根据Display API文档使用正确的权限范围
            scopes = [
                'user.info.basic',  # 读取用户基本信息
                'video.list'        # 读取用户公开视频
            ]
        
        if state is None:
            state = self.generate_state()
        
        # 生成PKCE参数
        code_verifier, code_challenge = self.generate_pkce_pair()
        
        params = {
            'client_key': self.client_key,
            'scope': ','.join(scopes),
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"{self.base_url}/v2/auth/authorize/?" + urllib.parse.urlencode(params)
        return auth_url, state, code_verifier
    
    def exchange_code_for_token(self, authorization_code: str, code_verifier: str = None) -> Dict:
        """
        用授权码换取访问令牌（支持PKCE）
        
        Args:
            authorization_code: 授权码
            code_verifier: PKCE代码验证器
            
        Returns:
            包含访问令牌的字典
        """
        if not self.client_key or not self.client_secret:
            raise ValueError("未配置TikTok Client Key或Client Secret")
        
        token_url = f"{self.api_base_url}/v2/oauth/token/"
        
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        # 如果提供了code_verifier，添加到请求中（PKCE支持）
        if code_verifier:
            data['code_verifier'] = code_verifier
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"获取访问令牌失败: {e}")
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌信息
        """
        token_url = f"{self.api_base_url}/v2/oauth/token/"
        
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"刷新访问令牌失败: {e}")
    
    def revoke_token(self, access_token: str) -> bool:
        """
        撤销访问令牌
        
        Args:
            access_token: 访问令牌
            
        Returns:
            是否成功撤销
        """
        revoke_url = f"{self.api_base_url}/v2/oauth/revoke/"
        
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'token': access_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(revoke_url, data=data, headers=headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"撤销访问令牌失败: {e}")
            return False

class TikTokOfficialAPI:
    """TikTok官方API客户端"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://open.tiktokapis.com"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self, fields: list = None) -> Dict:
        """
        获取用户信息
        
        Args:
            fields: 需要获取的字段列表
            
        Returns:
            用户信息
        """
        if fields is None:
            fields = [
                'open_id',
                'avatar_url',
                'display_name',
                'bio_description',
                'profile_deep_link'
            ]
        
        params = {'fields': ','.join(fields)}
        
        try:
            response = requests.get(
                f"{self.base_url}/v2/user/info/",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"获取用户信息失败: {e}")
    
    def get_user_videos(self, cursor: Optional[str] = None, count: int = 20) -> Dict:
        """
        获取用户视频列表 - 使用Display API格式
        由于/v2/video/list/不存在，我们需要先获取用户信息，然后尝试其他方法
        
        Args:
            cursor: 分页游标 (可选)
            count: 每页数量 (最多20个)
            
        Returns:
            视频列表响应
        """
        print("Display API中没有/v2/video/list/端点，尝试替代方案...")
        
        # 第一步：先获取用户信息确认API工作
        try:
            user_info = self.get_user_info(['open_id', 'display_name'])
            print(f"用户信息获取成功: {user_info}")
            
            # Display API可能不提供直接获取用户所有视频的方法
            # 它主要用于显示特定的视频，而不是列出所有视频
            
            # 返回一个模拟的响应，说明需要使用不同的方法
            return {
                'data': {
                    'videos': [],
                    'has_more': False,
                    'cursor': None
                },
                'error': {
                    'code': 'display_api_limitation',
                    'message': 'Display API不支持列出用户的所有视频，只能查询特定视频ID'
                },
                'user_info': user_info
            }
            
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            raise Exception(f"Display API限制: 无法列出用户视频，只能查询特定视频。错误: {e}")
    
    def query_specific_videos(self, video_ids: list, fields: list = None) -> Dict:
        """
        查询特定视频的信息 - 这是Display API实际支持的方法
        
        Args:
            video_ids: 视频ID列表
            fields: 需要获取的字段列表
            
        Returns:
            视频信息
        """
        if fields is None:
            fields = [
                'id',
                'title',
                'create_time',
                'cover_image_url',
                'share_url',
                'duration'
            ]
        
        data = {
            'filters': {
                'video_ids': video_ids
            }
        }
        
        params = {
            'fields': ','.join(fields)
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/video/query/",
                headers=self.headers,
                json=data,
                params=params
            )
            print(f"查询特定视频状态码: {response.status_code}")
            print(f"查询特定视频响应: {response.text[:500]}...")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"查询特定视频失败: {e}")
    
    def get_video_info(self, video_ids: list, fields: list = None) -> Dict:
        """
        获取视频详细信息
        
        Args:
            video_ids: 视频ID列表
            fields: 需要获取的字段列表
            
        Returns:
            视频信息
        """
        if fields is None:
            fields = [
                'id',
                'title',
                'video_description',
                'duration',
                'cover_image_url',
                'share_url',
                'view_count',
                'like_count',
                'comment_count',
                'share_count',
                'create_time'
            ]
        
        data = {
            'video_ids': video_ids,
            'fields': ','.join(fields)
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v2/video/query/",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"获取视频信息失败: {e}")
    
    def process_video_analytics(self, videos_data: list) -> list:
        """
        处理视频数据为分析格式 - 适配Display API响应
        
        Args:
            videos_data: Display API返回的视频列表 (不是Dict，而是list)
            
        Returns:
            处理后的分析数据列表
        """
        analytics_data = []
        
        # Display API直接返回视频列表
        if not videos_data or not isinstance(videos_data, list):
            return analytics_data
        
        for video in videos_data:
            # 根据Display API Video Object文档处理字段
            video_id = video.get('id', '')
            title = video.get('title', '')
            
            # Display API中的统计数据可能在不同字段中
            views = 0  # Display API可能不提供view_count
            likes = 0  # Display API可能不提供like_count
            comments = 0  # Display API可能不提供comment_count
            shares = 0  # Display API可能不提供share_count
            
            # 尝试从可能的字段获取统计数据
            if 'statistics' in video:
                stats = video['statistics']
                views = stats.get('view_count', 0)
                likes = stats.get('like_count', 0)
                comments = stats.get('comment_count', 0)
                shares = stats.get('share_count', 0)
            
            # 计算参与度 (如果有统计数据的话)
            engagement_rate = 0
            if views > 0:
                engagement_rate = ((likes + comments + shares) / views) * 100
            
            # 获取视频时长
            duration = video.get('duration', 30)
            if isinstance(duration, str):
                # 如果duration是字符串格式，尝试转换
                try:
                    duration = int(duration)
                except:
                    duration = 30
            
            # 估算其他指标
            avg_watch_time = duration * (0.3 + (engagement_rate / 100) * 0.5)
            completion_rate = min(90, 20 + engagement_rate * 2)
            
            analytics_item = {
                'video_id': video_id,
                'description': title or video.get('description', ''),
                'author': 'current_user',  # 当前授权用户
                'publish_time': self._parse_timestamp(video.get('create_time', video.get('created_at'))),
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'duration': duration,
                'engagement_rate': round(engagement_rate, 2),
                'avg_watch_time': round(avg_watch_time, 1),
                'completion_rate': round(completion_rate, 1),
                'bounce_rate': round(max(1.0, 5.0 - engagement_rate/2), 2),
                'share_url': video.get('share_url', video.get('web_video_url', '')),
                'cover_image': video.get('cover_image_url', '')
            }
            
            analytics_data.append(analytics_item)
        
        return analytics_data
    
    def _parse_timestamp(self, timestamp):
        """解析时间戳"""
        if isinstance(timestamp, (int, float)):
            from datetime import datetime
            return datetime.fromtimestamp(timestamp)
        return timestamp

    def test_api_endpoints(self) -> Dict:
        """
        测试不同的API端点来诊断问题
        """
        test_results = {}
        
        # 测试用户信息端点
        try:
            user_response = requests.get(
                f"{self.base_url}/v2/user/info/",
                headers=self.headers,
                params={'fields': 'open_id,display_name'}
            )
            test_results['user_info'] = {
                'status_code': user_response.status_code,
                'success': user_response.status_code == 200,
                'response': user_response.text[:200]
            }
        except Exception as e:
            test_results['user_info'] = {'error': str(e)}
        
        # 尝试不同的视频端点路径和方法
        video_endpoints = [
            ('GET', '/v2/video/list/', {}),
            ('POST', '/v2/video/list/', {}),
            ('GET', '/v2/video/query/', {}),
            ('POST', '/v2/video/query/', {}),
            ('GET', '/v2/videos/list/', {}),
            ('POST', '/v2/videos/list/', {}),
            ('GET', '/v2/user/videos/', {}),
            ('POST', '/v2/user/videos/', {}),
        ]
        
        for i, (method, endpoint, params) in enumerate(video_endpoints):
            try:
                if method == 'GET':
                    video_response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        params=params
                    )
                else:  # POST
                    video_response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        json=params
                    )
                
                test_results[f'video_endpoint_{i}'] = {
                    'method': method,
                    'endpoint': endpoint,
                    'params': params,
                    'status_code': video_response.status_code,
                    'success': video_response.status_code == 200,
                    'response': video_response.text[:300]
                }
            except Exception as e:
                test_results[f'video_endpoint_{i}'] = {
                    'method': method,
                    'endpoint': endpoint,
                    'params': params,
                    'error': str(e)
                }
        
        return test_results

# 示例使用
if __name__ == "__main__":
    # OAuth流程示例
    oauth = TikTokOAuth()
    
    # 生成授权URL
    auth_url, state = oauth.get_auth_url()
    print(f"请访问以下URL进行授权:\n{auth_url}")
    
    # 用户授权后，使用返回的code交换token
    # authorization_code = "从回调URL获取的code"
    # token_data = oauth.exchange_code_for_token(authorization_code)
    # print(f"访问令牌: {token_data}")
    
    # 使用访问令牌调用API
    # api = TikTokOfficialAPI(token_data['access_token'])
    # user_info = api.get_user_info()
    # print(f"用户信息: {user_info}") 