from flask import Flask, render_template, jsonify, request, redirect, session, url_for
from flask_socketio import SocketIO, emit
import json
import random
import datetime
import time
import threading
import schedule
from tiktok_api import TikTokDataFetcher
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiktok_analytics_secret_key'

# 简化的SocketIO配置 - 让它自动选择最佳传输方式
import os
is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER') or os.environ.get('HEROKU')

socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='gevent' if is_production else None,  # 生产环境使用gevent
                   logger=False if is_production else True,
                   engineio_logger=False,
                   ping_timeout=120,  # 增加超时时间
                   ping_interval=60,  # 增加ping间隔
                   transports=['polling', 'websocket'])  # 明确指定传输方式优先级

# 为WSGI服务器提供应用入口点
application = socketio

# 初始化TikTok数据获取器
tiktok_fetcher = TikTokDataFetcher(api_key=Config.get_api_key())

# 全局变量存储实时数据
current_data = []

def generate_sample_data():
    """生成示例数据"""
    sample_videos = [
        {
            'video_link': 'https://www.tiktok.com/t/ZPRhUAJN/',
            'product': 'Cleaning Gel',
            'service': 'IMX.TOOLS',
            'publish_date': '2025/7/8',
            'views': random.randint(400, 600),
            'avg_watch_time': round(random.uniform(2.0, 3.0), 1),
            'new_followers': random.randint(0, 2),
            'completion_rate': f"{round(random.uniform(15, 20), 1)}%",
            'bounce_rate': round(random.uniform(1.5, 2.5), 2),
            'watch_duration': f"{random.randint(30, 40)}s",
            'gmv_max_views': f"{round(random.uniform(30, 40), 1)}s",
            'performance': random.randint(0, 1)
        },
        {
            'video_link': 'https://www.tiktok.com/t/ZPRhUJsj/',
            'product': '3-tier stackable box',
            'service': 'DNA.LIVE',
            'publish_date': '2025/7/9',
            'views': random.randint(300, 400),
            'avg_watch_time': round(random.uniform(2.0, 3.0), 1),
            'new_followers': random.randint(0, 1),
            'completion_rate': f"{round(random.uniform(13, 18), 1)}%",
            'bounce_rate': round(random.uniform(2.0, 3.0), 2),
            'watch_duration': f"{random.randint(20, 30)}s",
            'gmv_max_views': f"{round(random.uniform(20, 30), 1)}s",
            'performance': random.randint(0, 1)
        },
        {
            'video_link': 'https://www.tiktok.com/t/ZPRhVKsWK/',
            'product': 'Bottle Jack',
            'service': 'DNA.LIVE',
            'publish_date': '2025/7/12',
            'views': random.randint(1400, 1500),
            'avg_watch_time': round(random.uniform(4.5, 5.5), 1),
            'new_followers': random.randint(1, 2),
            'completion_rate': f"{round(random.uniform(20, 25), 1)}%",
            'bounce_rate': round(random.uniform(3.5, 4.5), 2),
            'watch_duration': f"{random.randint(20, 25)}s",
            'gmv_max_views': "是",
            'performance': 1
        },
        {
            'video_link': 'https://www.tiktok.com/t/ZPRhvTo2l/',
            'product': 'Cleaning Gel',
            'service': 'IMX.TOOLS',
            'publish_date': '2025/7/10',
            'views': random.randint(450, 500),
            'avg_watch_time': round(random.uniform(8.0, 9.0), 1),
            'new_followers': random.randint(1, 2),
            'completion_rate': f"{round(random.uniform(30, 35), 1)}%",
            'bounce_rate': round(random.uniform(1.0, 2.0), 2),
            'watch_duration': f"{random.randint(30, 35)}s",
            'gmv_max_views': f"{round(random.uniform(30, 35), 1)}s",
            'performance': 1
        }
    ]
    return sample_videos

def update_data():
    """更新数据并通过WebSocket发送"""
    global current_data
    
    api_type = Config.get_api_type()
    
    try:
        if api_type == 'official':
            # 使用官方API
            if not Config.has_official_api_config():
                current_data = []
                message = "请配置API密钥并授权TikTok账号"
                status = 'need_config'
            else:
                # 检查是否有访问令牌 - 使用全局存储避免session问题
                access_token = getattr(app, '_access_token', None)
                if not access_token:
                    current_data = []
                    message = "需要授权TikTok账号才能获取数据"
                    status = 'need_auth'
                else:
                    # 用户已授权，获取实际数据
                    try:
                        from oauth_handler import TikTokOfficialAPI
                        api = TikTokOfficialAPI(access_token)
                        
                        # 获取用户视频数据
                        videos_response = api.get_user_videos(count=20)
                        
                        # Display API的响应格式: {"data": {"videos": [...], "cursor": ..., "has_more": bool}, "error": {...}}
                        if videos_response.get('data') and videos_response['data'].get('videos'):
                            raw_videos = videos_response['data']['videos']
                            current_data = api.process_video_analytics(raw_videos)
                            message = f"成功获取 {len(current_data)} 个视频数据"
                            status = 'success'
                        else:
                            current_data = []
                            message = "暂无视频数据"
                            status = 'no_data'
                    except Exception as e:
                        print(f"获取官方API数据失败: {e}")
                        current_data = []
                        message = f"获取数据失败: {str(e)}"
                        status = 'error'
                
        elif api_type == 'third_party':
            # 使用第三方API获取真实数据
            # 暂时返回空数据，因为我们不再使用模拟数据
            current_data = []
            message = "第三方API功能暂未实现"
            status = 'not_implemented'
            
        else:
            # 未配置API
            current_data = []
            message = "请先配置API密钥"
            status = 'no_config'
            
    except Exception as e:
        print(f"Error updating data: {e}")
        current_data = []
        message = f"数据获取失败: {str(e)}"
        status = 'error'
    
    # 构建完整的数据结构
    data_payload = {
        'videos': current_data,
        'status': status,
        'message': message,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # 通过WebSocket发送数据
    socketio.emit('data_update', data_payload)
    print(f"数据更新于: {datetime.datetime.now()}")

@app.route('/')
def index():
    """主页路由"""
    # 检查是否已配置API
    if not Config.has_api_config():
        return redirect(url_for('api_config'))
    return render_template('index.html')

@app.route('/config')
def api_config():
    """API配置页面"""
    return render_template('api_config.html')

@app.route('/terms')
def terms():
    """服务条款页面"""
    import datetime
    return render_template('terms.html', current_date=datetime.datetime.now().strftime('%Y年%m月%d日'))

@app.route('/privacy')
def privacy():
    """隐私政策页面"""
    import datetime
    return render_template('privacy.html', current_date=datetime.datetime.now().strftime('%Y年%m月%d日'))

@app.route('/debug')
def debug():
    """调试页面"""
    return render_template('debug.html')

@app.route('/test_pkce')
def test_pkce():
    """PKCE测试页面"""
    return render_template('test_pkce.html')

@app.route('/redirect_debug')
def redirect_debug():
    """重定向URI调试页面"""
    return render_template('redirect_debug.html')

@app.route('/auth_test')
def auth_test():
    """授权测试页面"""
    return render_template('auth_test.html')

@app.route('/api/data')
def get_data():
    """获取当前数据的API端点"""
    try:
        api_type = Config.get_api_type()
        
        if api_type == 'official':
            # 使用官方API
            if not Config.has_official_api_config():
                return jsonify({
                    'videos': [],
                    'status': 'need_config',
                    'message': '请配置API密钥并授权TikTok账号',
                    'timestamp': datetime.datetime.now().isoformat()
                })
            else:
                # 检查是否有访问令牌
                access_token = getattr(app, '_access_token', None) or session.get('access_token')
                if not access_token:
                    return jsonify({
                        'videos': [],
                        'status': 'need_auth',
                        'message': '需要授权TikTok账号才能获取数据',
                        'timestamp': datetime.datetime.now().isoformat()
                    })
                else:
                    # 用户已授权，获取实际数据
                    try:
                        from oauth_handler import TikTokOfficialAPI
                        api = TikTokOfficialAPI(access_token)
                        
                        # 获取用户视频数据
                        videos_response = api.get_user_videos(count=20)
                        if videos_response.get('data') and videos_response['data'].get('videos'):
                            raw_videos = videos_response['data']['videos']
                            video_data = api.process_video_analytics(raw_videos)
                            return jsonify({
                                'videos': video_data,
                                'status': 'success',
                                'message': f'成功获取 {len(video_data)} 个视频数据',
                                'timestamp': datetime.datetime.now().isoformat()
                            })
                        else:
                            return jsonify({
                                'videos': [],
                                'status': 'no_data',
                                'message': '暂无视频数据',
                                'timestamp': datetime.datetime.now().isoformat()
                            })
                    except Exception as e:
                        print(f"获取官方API数据失败: {e}")
                        return jsonify({
                            'videos': [],
                            'status': 'error',
                            'message': f'获取数据失败: {str(e)}',
                            'timestamp': datetime.datetime.now().isoformat()
                        })
        
        elif api_type == 'third_party':
            return jsonify({
                'videos': [],
                'status': 'not_implemented',
                'message': '第三方API功能暂未实现',
                'timestamp': datetime.datetime.now().isoformat()
            })
        
        else:
            # 未配置API
            return jsonify({
                'videos': [],
                'status': 'no_config',
                'message': '请先配置API密钥',
                'timestamp': datetime.datetime.now().isoformat()
            })
            
    except Exception as e:
        print(f"Error in get_data: {e}")
        return jsonify({
            'videos': [],
            'status': 'error',
            'message': f'获取数据失败: {str(e)}',
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.route('/api/refresh')
def refresh_data():
    """手动刷新数据"""
    try:
        update_data()
        return jsonify({'status': 'success', 'message': '数据已刷新'})
    except Exception as e:
        print(f"Error in refresh_data: {e}")
        return jsonify({'status': 'error', 'message': f'刷新失败: {str(e)}'}), 500

@app.route('/auth')
def authorize():
    """跳转到TikTok官方API授权页面"""
    print("=== 授权请求开始 ===")
    print(f"Client Key: {Config.get_client_key()}")
    print(f"Has API Config: {Config.has_official_api_config()}")
    
    if not Config.has_official_api_config():
        print("错误: 未配置API凭证")
        return jsonify({
            'status': 'error', 
            'message': '未配置TikTok官方API凭证'
        }), 400
    
    try:
        from oauth_handler import TikTokOAuth
        oauth = TikTokOAuth()
        auth_url, state, code_verifier = oauth.get_auth_url()
        
        print(f"生成的授权URL: {auth_url}")
        print(f"State: {state}")
        print(f"Code Verifier: {code_verifier[:30]}...")
        
        # 保存state和code_verifier到session用于验证
        session['oauth_state'] = state
        session['code_verifier'] = code_verifier
        
        return redirect(auth_url)
    except Exception as e:
        print(f"授权失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'生成授权链接失败: {str(e)}'
        }), 500

@app.route('/callback')
def callback():
    """处理TikTok授权回调"""
    print("=== 授权回调开始 ===")
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    print(f"Code: {code}")
    print(f"State: {state}")
    print(f"Error: {error}")
    print(f"Session State: {session.get('oauth_state')}")
    
    if error:
        print(f"授权错误: {error}")
        return f"授权失败: {error}", 400
    
    if not code:
        print("错误: 未收到授权码")
        return "未收到授权码", 400
    
    # 验证state
    if state != session.get('oauth_state'):
        print(f"State验证失败: {state} != {session.get('oauth_state')}")
        return "状态验证失败", 400
    
    try:
        from oauth_handler import TikTokOAuth
        oauth = TikTokOAuth()
        print("开始交换访问令牌...")
        
        # 获取保存的code_verifier（PKCE支持）
        code_verifier = session.get('code_verifier')
        print(f"使用Code Verifier: {code_verifier[:30] if code_verifier else 'None'}...")
        
        token_data = oauth.exchange_code_for_token(code, code_verifier)
        print(f"Token响应: {token_data}")
        
        if 'access_token' in token_data:
            # 保存访问令牌到session和app对象
            session['access_token'] = token_data['access_token']
            session['refresh_token'] = token_data.get('refresh_token')
            session['token_expires'] = token_data.get('expires_in', 3600)
            
            # 保存到app对象供WebSocket使用
            app._access_token = token_data['access_token']
            app._refresh_token = token_data.get('refresh_token')
            
            print(f"成功保存访问令牌: {token_data['access_token'][:20]}...")
            
            # 清除state和code_verifier
            session.pop('oauth_state', None)
            session.pop('code_verifier', None)
            
            return redirect('/')
        else:
            print(f"Token响应中没有access_token: {token_data}")
            return f"获取访问令牌失败: {token_data}", 400
            
    except Exception as e:
        print(f"回调处理异常: {e}")
        import traceback
        traceback.print_exc()
        return f"处理授权回调失败: {str(e)}", 500

@app.route('/api/config', methods=['POST'])
def save_config():
    """保存API配置"""
    try:
        data = request.get_json()
        client_key = data.get('clientKey', '').strip()
        client_secret = data.get('clientSecret', '').strip()
        
        if not client_key or not client_secret:
            return jsonify({
                'success': False,
                'message': '请提供有效的Client Key和Client Secret'
            })
        
        # 保存到运行时配置
        Config.set_runtime_api_config(client_key, client_secret)
        
        return jsonify({
            'success': True,
            'message': '✅ API配置保存成功！即将跳转到仪表板...'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'配置保存失败: {str(e)}'
        })

@app.route('/api/clear_config', methods=['POST'])
def clear_config():
    """清除API配置"""
    try:
        Config.clear_runtime_config()
        # 清除session中的OAuth相关数据
        session.pop('access_token', None)
        session.pop('refresh_token', None)
        session.pop('token_expires', None)
        session.pop('user_info', None)
        session.pop('oauth_state', None)
        session.pop('code_verifier', None)
        
        # 清除app对象中的访问令牌
        if hasattr(app, '_access_token'):
            delattr(app, '_access_token')
        if hasattr(app, '_refresh_token'):
            delattr(app, '_refresh_token')
        
        return jsonify({
            'success': True,
            'message': 'API配置已清除'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'清除配置失败: {str(e)}'
        })

@app.route('/api/test_connection', methods=['POST'])
def test_connection():
    """测试API连接"""
    try:
        data = request.get_json()
        client_key = data.get('clientKey', '').strip()
        client_secret = data.get('clientSecret', '').strip()
        
        if not client_key or not client_secret:
            return jsonify({
                'success': False,
                'message': '请提供有效的Client Key和Client Secret'
            })
        
        # 这里可以添加实际的连接测试逻辑
        # 目前只是验证格式
        if len(client_key) < 10 or len(client_secret) < 10:
            return jsonify({
                'success': False,
                'message': 'API密钥格式似乎不正确'
            })
        
        return jsonify({
            'success': True,
            'message': 'API密钥格式验证通过'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        })

@app.route('/api/redirect_uri_info')
def redirect_uri_info():
    """获取当前重定向URI信息"""
    return jsonify({
        'redirect_uri': Config.get_redirect_uri(),
        'is_runtime': Config._runtime_redirect_uri is not None
    })

@app.route('/api/set_redirect_uri', methods=['POST'])
def set_redirect_uri():
    """设置重定向URI"""
    try:
        data = request.get_json()
        redirect_uri = data.get('redirect_uri', '').strip()
        
        if not redirect_uri:
            return jsonify({
                'success': False,
                'message': '请提供有效的重定向URI'
            })
        
        # 基本格式验证
        if not (redirect_uri.startswith('http://') or redirect_uri.startswith('https://')):
            return jsonify({
                'success': False,
                'message': '重定向URI必须以http://或https://开头'
            })
        
        # 设置运行时重定向URI
        Config.set_runtime_redirect_uri(redirect_uri)
        
        return jsonify({
            'success': True,
            'message': f'重定向URI已设置为: {redirect_uri}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'设置失败: {str(e)}'
        })

@app.route('/api/manual_auth', methods=['POST'])
def manual_auth():
    """手动处理授权码"""
    try:
        data = request.get_json()
        authorization_code = data.get('code', '').strip()
        state = data.get('state', '').strip()
        
        if not authorization_code:
            return jsonify({
                'success': False,
                'message': '请提供授权码'
            })
        
        print(f"=== 手动授权开始 ===")
        print(f"Authorization Code: {authorization_code}")
        print(f"State: {state}")
        print(f"Session State: {session.get('oauth_state')}")
        
        # 验证state（仅在两边都有的情况下）
        if state and state.strip() and 'oauth_state' in session:
            if state != session.get('oauth_state'):
                return jsonify({
                    'success': False,
                    'message': 'State验证失败'
                })
        
        # 如果没有code_verifier，尝试重新生成授权参数
        code_verifier = session.get('code_verifier')
        if not code_verifier:
            print("警告: 未找到code_verifier，可能是会话过期")
            # 可以继续尝试，某些情况下可能不需要code_verifier
        
        # 交换访问令牌
        from oauth_handler import TikTokOAuth
        oauth = TikTokOAuth()
        
        print(f"Code Verifier: {code_verifier[:30] if code_verifier else 'Not found'}...")
        
        token_data = oauth.exchange_code_for_token(authorization_code, code_verifier)
        print(f"Token Response: {token_data}")
        
        if 'access_token' in token_data:
            # 保存访问令牌到session和app对象
            session['access_token'] = token_data['access_token']
            session['refresh_token'] = token_data.get('refresh_token')
            session['token_expires'] = token_data.get('expires_in', 3600)
            
            # 保存到app对象供WebSocket使用
            app._access_token = token_data['access_token']
            app._refresh_token = token_data.get('refresh_token')
            
            # 清除临时数据
            session.pop('oauth_state', None)
            session.pop('code_verifier', None)
            
            print(f"成功保存访问令牌: {token_data['access_token'][:20]}...")
            
            return jsonify({
                'success': True,
                'message': '授权成功！正在重定向...',
                'access_token': token_data['access_token'][:20] + '...'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'获取访问令牌失败: {token_data}'
            })
            
    except Exception as e:
        print(f"手动授权失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        })

@app.route('/api/auth_status')
def auth_status():
    """获取当前API配置和认证状态"""
    api_type = Config.get_api_type()
    
    status = {
        'api_type': api_type,
        'configured': False,
        'authenticated': False,
        'message': ''
    }
    
    if api_type == 'official':
        # 检查是否已配置客户端密钥
        if Config.has_official_api_config():
            status['configured'] = True
            # 检查是否已获得access_token（session或app对象）
            has_token = 'access_token' in session or hasattr(app, '_access_token')
            if has_token:
                status['authenticated'] = True
                status['message'] = '已成功连接TikTok官方API'
            else:
                status['message'] = '已配置API密钥，但需要用户授权'
        else:
            status['message'] = '请先配置TikTok官方API密钥'
    elif api_type == 'third_party':
        status['configured'] = True
        status['authenticated'] = True
        status['message'] = '正在使用第三方API'
    else:
        status['message'] = '未配置任何API'
    
    return jsonify(status)

@socketio.on('connect')
def handle_connect():
    """处理WebSocket连接"""
    print('客户端已连接')
    # 发送当前数据给新连接的客户端
    global current_data
    if not current_data:
        current_data = generate_sample_data()
    emit('data_update', {'data': current_data})

@socketio.on('disconnect')
def handle_disconnect():
    """处理WebSocket断开连接"""
    print('客户端已断开连接')

@socketio.on('request_update')
def handle_request_update():
    """处理客户端请求数据更新"""
    update_data()

def convert_analytics_to_display_format(analytics_data):
    """将API数据转换为显示格式"""
    display_data = []
    
    for item in analytics_data:
        # 安全地获取数据字段
        video_id = item.get('video_id', '')
        author = item.get('author', '')
        publish_time = item.get('publish_time')
        
        # 生成视频链接
        if video_id and author:
            video_link = f"https://www.tiktok.com/@{author}/video/{video_id}"
        else:
            video_link = "链接不可用"
        
        # 格式化发布时间
        if isinstance(publish_time, datetime.datetime):
            publish_date = publish_time.strftime('%Y/%m/%d')
        else:
            publish_date = datetime.datetime.now().strftime('%Y/%m/%d')
        
        display_item = {
            'video_link': video_link,
            'product': '内容创作',  # 可以根据实际情况设置
            'service': 'TikTok',
            'publish_date': publish_date,
            'views': item.get('views', 0),
            'avg_watch_time': round(item.get('avg_watch_time', 0), 1),
            'new_followers': item.get('new_followers', 0),
            'completion_rate': f"{item.get('completion_rate', 0):.1f}%",
            'bounce_rate': round(item.get('bounce_rate', 0), 2),
            'watch_duration': f"{item.get('avg_watch_time', 0):.1f}s",
            'gmv_max_views': '分析中',
            'performance': 1 if item.get('engagement_rate', 0) > 5 else 0
        }
        display_data.append(display_item)
    
    return display_data

def generate_sample_data_with_note(note="模拟数据"):
    """生成带说明的示例数据"""
    data = generate_sample_data()
    for item in data:
        item['product'] = f"{item['product']} ({note})"
    return data

def schedule_updates():
    """定时任务调度器"""
    schedule.every(Config.DATA_UPDATE_INTERVAL).seconds.do(update_data)  # 使用配置的更新间隔
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    import os
    
    # 初始化数据
    current_data = generate_sample_data()
    
    # 启动定时任务线程
    update_thread = threading.Thread(target=schedule_updates, daemon=True)
    update_thread.start()
    
    # 获取端口号（云平台会设置PORT环境变量）
    port = int(os.environ.get('PORT', 5000))
    
    print("TikTok数据分析面板启动中...")
    print(f"访问地址: http://localhost:{port}")
    
    # 根据环境判断是否为生产模式
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER') or os.environ.get('HEROKU')
    
    # 启动Flask-SocketIO应用
    if is_production:
        # 生产环境：让gunicorn处理，这里不应该执行到
        print("生产环境应使用gunicorn启动，而不是运行到这里")
        app.run(host='0.0.0.0', port=port)
    else:
        # 开发环境：使用内置服务器
        socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True) 