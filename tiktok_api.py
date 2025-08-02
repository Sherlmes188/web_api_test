import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TikTokDataFetcher:
    """TikTok数据获取器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化TikTok数据获取器
        
        Args:
            api_key: TikTok API密钥（可选，用于真实API调用）
        """
        self.api_key = api_key
        self.base_url = "https://api.tikapi.io"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TikTok-Analytics-Dashboard/1.0'
        }
        
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def get_video_info(self, video_id: str) -> Dict:
        """
        获取单个视频的详细信息
        
        Args:
            video_id: TikTok视频ID
            
        Returns:
            视频信息字典
        """
        if self.api_key:
            # 真实API调用
            try:
                url = f"{self.base_url}/public/video"
                params = {'id': video_id}
                response = requests.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"API请求失败: {response.status_code}")
                    return self._generate_mock_video_data(video_id)
            except Exception as e:
                print(f"API请求异常: {e}")
                return self._generate_mock_video_data(video_id)
        else:
            # 模拟数据
            return self._generate_mock_video_data(video_id)
    
    def get_user_videos(self, username: str, count: int = 30) -> List[Dict]:
        """
        获取用户的视频列表
        
        Args:
            username: TikTok用户名
            count: 获取视频数量
            
        Returns:
            视频列表
        """
        if self.api_key:
            try:
                # 首先获取用户信息
                user_info = self.get_user_info(username)
                if not user_info:
                    return []
                
                sec_uid = user_info.get('userInfo', {}).get('user', {}).get('secUid', '')
                
                # 获取用户视频
                url = f"{self.base_url}/public/posts"
                params = {
                    'secUid': sec_uid,
                    'count': count
                }
                response = requests.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('itemList', [])
                else:
                    print(f"获取视频列表失败: {response.status_code}")
                    return self._generate_mock_videos_list(count)
            except Exception as e:
                print(f"获取视频列表异常: {e}")
                return self._generate_mock_videos_list(count)
        else:
            return self._generate_mock_videos_list(count)
    
    def get_user_info(self, username: str) -> Dict:
        """
        获取用户基本信息
        
        Args:
            username: TikTok用户名
            
        Returns:
            用户信息字典
        """
        if self.api_key:
            try:
                url = f"{self.base_url}/public/check"
                params = {'username': username}
                response = requests.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"获取用户信息失败: {response.status_code}")
                    return self._generate_mock_user_data(username)
            except Exception as e:
                print(f"获取用户信息异常: {e}")
                return self._generate_mock_user_data(username)
        else:
            return self._generate_mock_user_data(username)
    
    def get_trending_videos(self, count: int = 30) -> List[Dict]:
        """
        获取热门视频列表
        
        Args:
            count: 获取视频数量
            
        Returns:
            热门视频列表
        """
        if self.api_key:
            try:
                url = f"{self.base_url}/public/explore"
                params = {'count': count}
                response = requests.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('itemList', [])
                else:
                    print(f"获取热门视频失败: {response.status_code}")
                    return self._generate_mock_videos_list(count)
            except Exception as e:
                print(f"获取热门视频异常: {e}")
                return self._generate_mock_videos_list(count)
        else:
            return self._generate_mock_videos_list(count)
    
    def _generate_mock_video_data(self, video_id: str) -> Dict:
        """生成模拟视频数据"""
        return {
            'id': video_id,
            'desc': f'模拟视频描述 {video_id}',
            'createTime': int(time.time()) - random.randint(3600, 86400),
            'stats': {
                'diggCount': random.randint(1000, 100000),
                'shareCount': random.randint(100, 10000),
                'commentCount': random.randint(50, 5000),
                'playCount': random.randint(10000, 1000000)
            },
            'author': {
                'uniqueId': f'user_{random.randint(1000, 9999)}',
                'nickname': f'用户{random.randint(100, 999)}',
                'followerCount': random.randint(1000, 100000)
            },
            'video': {
                'duration': random.randint(15, 60),
                'height': 1024,
                'width': 576
            }
        }
    
    def _generate_mock_user_data(self, username: str) -> Dict:
        """生成模拟用户数据"""
        return {
            'userInfo': {
                'user': {
                    'uniqueId': username,
                    'nickname': f'用户_{username}',
                    'secUid': f'mock_sec_uid_{username}',
                    'followerCount': random.randint(1000, 100000),
                    'followingCount': random.randint(100, 1000),
                    'heartCount': random.randint(10000, 1000000),
                    'videoCount': random.randint(50, 500)
                }
            }
        }
    
    def _generate_mock_videos_list(self, count: int) -> List[Dict]:
        """生成模拟视频列表"""
        videos = []
        for i in range(count):
            video_id = f'mock_video_{i}_{random.randint(1000, 9999)}'
            videos.append(self._generate_mock_video_data(video_id))
        return videos
    
    def process_video_analytics(self, video_data: Dict) -> Dict:
        """
        处理视频数据并计算分析指标
        
        Args:
            video_data: 原始视频数据
            
        Returns:
            处理后的分析数据
        """
        stats = video_data.get('stats', {})
        video_info = video_data.get('video', {})
        author_info = video_data.get('author', {})
        
        # 计算各种指标
        views = stats.get('playCount', 0)
        likes = stats.get('diggCount', 0)
        comments = stats.get('commentCount', 0)
        shares = stats.get('shareCount', 0)
        duration = video_info.get('duration', 30)
        
        # 计算参与度
        engagement_rate = ((likes + comments + shares) / max(views, 1)) * 100 if views > 0 else 0
        
        # 计算平均观看时长（模拟）
        avg_watch_time = duration * random.uniform(0.3, 0.8)
        
        # 计算完播率（模拟）
        completion_rate = random.uniform(15, 35)
        
        # 计算跳出率（模拟）
        bounce_rate = random.uniform(1.0, 4.0)
        
        return {
            'video_id': video_data.get('id', ''),
            'description': video_data.get('desc', ''),
            'author': author_info.get('uniqueId', ''),
            'publish_time': datetime.fromtimestamp(video_data.get('createTime', time.time())),
            'views': views,
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'duration': duration,
            'engagement_rate': round(engagement_rate, 2),
            'avg_watch_time': round(avg_watch_time, 1),
            'completion_rate': round(completion_rate, 1),
            'bounce_rate': round(bounce_rate, 2)
        }
    
    def get_analytics_data(self, video_ids: List[str] = None, username: str = None) -> List[Dict]:
        """
        获取综合分析数据
        
        Args:
            video_ids: 视频ID列表
            username: 用户名（用于获取该用户的视频）
            
        Returns:
            分析数据列表
        """
        analytics_data = []
        
        if video_ids:
            # 获取指定视频的分析数据
            for video_id in video_ids:
                video_data = self.get_video_info(video_id)
                if video_data:
                    analytics = self.process_video_analytics(video_data)
                    analytics_data.append(analytics)
        elif username:
            # 获取用户视频的分析数据
            videos = self.get_user_videos(username)
            for video in videos:
                analytics = self.process_video_analytics(video)
                analytics_data.append(analytics)
        else:
            # 获取热门视频的分析数据
            trending_videos = self.get_trending_videos()
            for video in trending_videos[:10]:  # 限制数量
                analytics = self.process_video_analytics(video)
                analytics_data.append(analytics)
        
        return analytics_data

# 示例用法
if __name__ == "__main__":
    # 创建数据获取器实例
    fetcher = TikTokDataFetcher()
    
    # 获取模拟数据
    analytics_data = fetcher.get_analytics_data()
    
    print("TikTok分析数据:")
    for data in analytics_data[:3]:  # 显示前3条
        print(f"视频ID: {data['video_id']}")
        print(f"作者: {data['author']}")
        print(f"观看数: {data['views']:,}")
        print(f"参与度: {data['engagement_rate']:.2f}%")
        print(f"平均观看时长: {data['avg_watch_time']:.1f}秒")
        print(f"完播率: {data['completion_rate']:.1f}%")
        print("-" * 40) 