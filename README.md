# TikTok视频数据分析面板

一个实时更新的TikTok视频数据分析面板，提供可视化的数据展示和分析功能。

## 功能特性

### 📊 实时数据监控
- **实时数据更新**: 通过WebSocket连接实现30秒自动刷新
- **手动刷新**: 支持一键手动刷新数据
- **连接状态**: 实时显示WebSocket连接状态

### 📈 数据分析指标
- **视频基础数据**: 链接、产品、发布服务、发布日期
- **观看数据**: Views、人均观看时长、观看时长
- **用户互动**: 新增关注者数量
- **性能指标**: 完播率、跳出率
- **商业指标**: GMV MAX各活动数据
- **状态监控**: 视频活跃状态实时监控

### 🎨 可视化展示
- **统计卡片**: 总视频数、总观看数、平均完播率、新增关注
- **数据表格**: 完整的视频数据列表，支持链接跳转
- **趋势图表**: 观看数趋势折线图
- **分布图表**: 完播率分布饼图
- **响应式设计**: 支持移动端和桌面端

### 💫 用户体验
- **现代化UI**: 基于Bootstrap 5的现代化界面设计
- **动画效果**: 平滑的数据更新动画
- **实时通知**: Toast消息提示
- **加载状态**: 优雅的加载指示器

## 技术栈

### 后端技术
- **Flask**: Python Web框架
- **Flask-SocketIO**: WebSocket实时通信
- **Requests**: HTTP请求处理
- **Pandas**: 数据处理和分析
- **Schedule**: 定时任务调度

### 前端技术
- **Bootstrap 5**: 响应式UI框架
- **Chart.js**: 图表可视化
- **Socket.IO**: 客户端WebSocket
- **Font Awesome**: 图标库
- **原生JavaScript**: 前端交互逻辑

### 数据源
- **TikTok API**: 支持官方API接口
- **第三方API**: 支持TikAPI等第三方服务
- **模拟数据**: 内置数据生成器用于演示

## 安装和运行

### 环境要求
- Python 3.7+
- Windows/Linux/macOS

### 1. 克隆项目
```bash
git clone <repository-url>
cd project_2
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行应用
```bash
python app.py
```

### 5. 访问应用
打开浏览器访问: `http://localhost:5000`

## 项目结构

```
project_2/
├── app.py                 # Flask主应用
├── tiktok_api.py         # TikTok API集成
├── requirements.txt      # Python依赖
├── README.md            # 项目文档
├── templates/           # HTML模板
│   └── index.html      # 主页模板
├── static/             # 静态文件
│   ├── css/
│   │   └── style.css  # 自定义样式
│   └── js/
│       └── main.js    # 前端JavaScript
└── venv/              # 虚拟环境（可选）
```

## 配置说明

### API配置
如需使用真实的TikTok API，请在`tiktok_api.py`中配置API密钥：

```python
# 创建TikTok数据获取器时传入API密钥
fetcher = TikTokDataFetcher(api_key="your_api_key_here")
```

### 更新频率配置
在`app.py`中修改数据更新频率：

```python
# 修改更新间隔（秒）
schedule.every(30).seconds.do(update_data)  # 当前为30秒
```

## 数据字段说明

| 字段名称 | 描述 | 类型 |
|---------|------|------|
| video_link | 视频链接 | String |
| product | 产品名称 | String |
| service | 视频发布服务 | String |
| publish_date | 发布日期 | Date |
| views | 观看数 | Integer |
| avg_watch_time | 人均观看时长(秒) | Float |
| new_followers | 新增关注者 | Integer |
| completion_rate | 完播率(%) | String/Float |
| bounce_rate | 跳出率 | Float |
| watch_duration | 观看时长 | String |
| gmv_max_views | GMV MAX各活动 | String |
| performance | 状态(0/1) | Integer |

## API接口

### 获取数据
```
GET /api/data
```
返回当前所有视频数据

### 刷新数据
```
GET /api/refresh
```
手动触发数据刷新

### WebSocket事件
- `connect`: 客户端连接
- `disconnect`: 客户端断开
- `data_update`: 数据更新推送
- `request_update`: 请求数据更新

## 自定义和扩展

### 添加新的数据字段
1. 在`app.py`的`generate_sample_data()`中添加新字段
2. 在`templates/index.html`中添加对应的表格列
3. 在`static/js/main.js`中更新表格行生成逻辑

### 添加新的图表
1. 在`templates/index.html`中添加Canvas元素
2. 在`static/js/main.js`中初始化图表
3. 在数据更新时更新图表数据

### 集成真实API
1. 获取TikTok API或第三方服务的API密钥
2. 在`tiktok_api.py`中配置API调用
3. 根据API返回格式调整数据处理逻辑

## 故障排除

### 常见问题

1. **端口被占用**
   - 修改`app.py`中的端口号: `socketio.run(app, port=5001)`

2. **WebSocket连接失败**
   - 检查防火墙设置
   - 确认浏览器支持WebSocket

3. **依赖安装失败**
   - 升级pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

4. **图表不显示**
   - 检查网络连接，确保能访问CDN
   - 检查浏览器控制台错误信息

## 性能优化

- 数据更新频率可根据需要调整
- 大量数据时可考虑分页加载
- 图表数据可考虑缓存机制
- 可以添加数据持久化存储

## 许可证

本项目仅供学习和演示使用。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**注意**: 本项目当前使用模拟数据进行演示。如需连接真实的TikTok API，请遵循相关服务的使用条款和限制。 