import os

# 服务器配置
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1  # SocketIO需要单worker模式
worker_class = "eventlet"  # 异步worker类，支持WebSocket
worker_connections = 1000

# 日志配置
loglevel = "info"
accesslog = "-"  # 输出到stdout
errorlog = "-"   # 输出到stderr

# 超时配置
timeout = 120
keepalive = 5

# 进程命名
proc_name = "tiktok-analytics"

# 预加载应用
preload_app = True

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100 