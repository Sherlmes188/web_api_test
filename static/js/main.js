// TikTok数据分析面板 JavaScript
class TikTokAnalyticsDashboard {
    constructor() {
        this.socket = null;
        this.currentData = [];
        this.dataStatus = 'loading';
        this.statusMessage = '';
        this.charts = {};
        this.isConnected = false;
        this.pollingInterval = null; // HTTP轮询定时器
        this.authModalShown = false; // 授权弹窗状态
        
        this.init();
    }

    init() {
        // 初始化WebSocket连接
        this.initSocket();
        
        // 绑定事件处理器
        this.bindEvents();
        
        // 初始化图表
        this.initCharts();
        
        // 检查API状态
        this.checkApiStatus();
        
        // 加载初始数据
        this.loadInitialData();
        
        console.log('TikTok Analytics Dashboard initialized');
    }

    initSocket() {
        console.log('Initializing socket connection...');
        this.socket = io({
            transports: ['polling', 'websocket'],
            timeout: 15000,
            forceNew: true,
            upgrade: true,
            rememberUpgrade: false
        });

        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            // 停止HTTP轮询（如果正在运行）
            this.stopHttpPolling();
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            
            // WebSocket断开时启动HTTP轮询备选方案
            this.startHttpPolling();
        });

        this.socket.on('data_update', (response) => {
            console.log('Data updated via WebSocket:', response);
            if (response) {
                this.currentData = response.videos || [];
                this.updateData(this.currentData);
                this.updateStatusMessage(response.status, response.message);
                if (response.status === 'success' && this.currentData.length > 0) {
                    this.showNotification('数据已更新');
                }
            }
        });

        this.socket.on('connect_error', (error) => {
            console.log('WebSocket connection error:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            
            // 连接错误时启动HTTP轮询
            this.startHttpPolling();
        });

        // 添加重连错误处理
        this.socket.on('reconnect_error', (error) => {
            console.log('WebSocket reconnect error:', error);
            this.startHttpPolling();
        });

        // 添加重连失败处理
        this.socket.on('reconnect_failed', () => {
            console.log('WebSocket reconnect failed, falling back to HTTP polling');
            this.startHttpPolling();
        });
    }

    bindEvents() {
        // 刷新按钮
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // 授权按钮
        const authBtn = document.getElementById('authBtn');
        if (authBtn) {
            authBtn.addEventListener('click', () => {
                this.authenticateWithTikTok();
            });
        }

        // 窗口大小改变时重新绘制图表
        window.addEventListener('resize', () => {
            this.resizeCharts();
        });
    }

    async loadInitialData() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/data');
            const result = await response.json();
            
            // 处理新的数据结构
            this.currentData = result.videos || [];
            this.updateData(this.currentData);
            this.updateStatusMessage(result.status, result.message);
            console.log('Initial data loaded');
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('数据加载失败', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refreshBtn');
        const originalHtml = refreshBtn.innerHTML;
        
        // 显示加载状态
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 刷新中...';
        refreshBtn.disabled = true;
        
        try {
            const response = await fetch('/api/refresh');
            const result = await response.json();
            
            if (result.status === 'success') {
                console.log('Data refreshed manually');
                this.showNotification('数据已刷新');
            }
        } catch (error) {
            console.error('Failed to refresh data:', error);
            this.showNotification('刷新失败', 'error');
        } finally {
            // 恢复按钮状态
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
        }
    }

    updateData(data) {
        this.currentData = data;
        
        // 更新统计卡片
        this.updateStatistics();
        
        // 更新数据表格
        this.updateTable();
        
        // 更新图表
        this.updateCharts();
        
        // 更新最后更新时间
        this.updateLastUpdatedTime();
    }

    updateStatistics() {
        const data = this.currentData || [];
        
        // 计算真实统计数据
        const totalVideos = data.length;
        const totalViews = data.reduce((sum, item) => sum + (item.views || 0), 0);
        const totalLikes = data.reduce((sum, item) => sum + (item.likes || 0), 0);
        const totalNewFollowers = data.reduce((sum, item) => sum + (item.new_followers || 0), 0);
        
        // 计算平均参与度（基于真实数据）
        const avgEngagement = data.length > 0 
            ? (data.reduce((sum, item) => sum + (item.engagement_rate || 0), 0) / data.length).toFixed(2)
            : 0;

        // 更新DOM元素
        this.updateElement('totalVideos', totalVideos);
        this.updateElement('totalViews', this.formatNumber(totalViews));
        this.updateElement('avgCompletionRate', `${avgEngagement}%`); // 显示平均参与度
        this.updateElement('totalFollowers', this.formatNumber(totalNewFollowers)); // 显示新关注者总数
    }

    updateTable() {
        const tableBody = document.getElementById('dataTableBody');
        if (!tableBody) return;

        // 清空现有内容
        tableBody.innerHTML = '';

        // 检查是否有数据
        if (!this.currentData || this.currentData.length === 0) {
            // 显示无数据状态
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="10" class="text-center py-4">
                    <div class="text-muted">
                        <i class="fas fa-inbox fa-2x mb-3"></i>
                        <p class="mb-0">暂无数据</p>
                        <p class="mt-2">
                            <a href="/config" class="btn btn-warning btn-sm">
                                <i class="fas fa-cog me-1"></i>配置API
                            </a>
                        </p>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
            return;
        }

        // 生成表格行
        this.currentData.forEach((item, index) => {
            const row = this.createTableRow(item, index);
            tableBody.appendChild(row);
        });
    }

    createTableRow(item, index) {
        const row = document.createElement('tr');
        row.className = 'fade-in';
        row.style.animationDelay = `${index * 0.1}s`;

        // 处理完播率显示
        const completionRate = typeof item.completion_rate === 'string' 
            ? item.completion_rate 
            : `${item.completion_rate}%`;

        // 格式化发布时间
        const publishDate = this.formatPublishTime(item.publish_time);
        
        // 格式化视频链接
        const videoUrl = item.share_url || this.generateVideoUrl(item.video_id, item.author);
        
        // 显示真实的API数据
        row.innerHTML = `
            <td>
                <a href="${videoUrl}" target="_blank" class="video-link">
                    ${this.truncateUrl(videoUrl)}
                </a>
            </td>
            <td>
                <span class="author-tag">${item.author || '当前用户'}</span>
            </td>
            <td>${publishDate}</td>
            <td class="number-cell">${this.formatNumber(item.views || 0)}</td>
            <td class="number-cell">${item.avg_watch_time || 0}s</td>
            <td class="number-cell">${this.formatNumber(item.new_followers || 0)}</td>
            <td class="percentage-cell ${this.getPercentageClass(completionRate)}">${completionRate}</td>
            <td class="number-cell">${item.bounce_rate || 0}%</td>
            <td class="number-cell">${item.duration || 0}s</td>
            <td class="number-cell">${this.formatNumber(item.likes || 0)}</td>
            <td class="number-cell">${this.formatNumber(item.comments || 0)}</td>
            <td class="number-cell">${item.engagement_rate || 0}%</td>
            <td>
                <span class="status-indicator">
                    <span class="status-dot ${item.views > 1000 ? 'active' : 'inactive'}"></span>
                    ${item.views > 1000 ? '热门' : '正常'}
                </span>
            </td>
        `;

        return row;
    }

    initCharts() {
        // 初始化观看数趋势图表
        this.initViewsChart();
        
        // 初始化完播率分布图表
        this.initCompletionChart();
    }

    initViewsChart() {
        const ctx = document.getElementById('viewsChart');
        if (!ctx) return;

        this.charts.views = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '观看数',
                    data: [],
                    borderColor: '#ff0050',
                    backgroundColor: 'rgba(255, 0, 80, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value >= 1000 ? (value/1000).toFixed(1) + 'K' : value;
                            }
                        }
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 6
                        }
                    }
                }
            }
        });
    }

    initCompletionChart() {
        const ctx = document.getElementById('completionChart');
        if (!ctx) return;

        this.charts.completion = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['高完播率', '中等完播率', '低完播率'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        '#25d366',
                        '#ff9500',
                        '#ff3838'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateCharts() {
        this.updateViewsChart(this.currentData);
        this.updateCompletionChart(this.currentData);
    }

    updateViewsChart(data) {
        if (!this.charts.views || !data || data.length === 0) return;

        // 按发布时间排序
        const sortedData = [...data].sort((a, b) => 
            new Date(a.publish_time || 0) - new Date(b.publish_time || 0)
        );

        const labels = sortedData.map((item, index) => 
            item.publish_time ? 
                new Date(item.publish_time).toLocaleDateString('zh-CN') : 
                `视频 ${index + 1}`
        );
        
        const viewsData = sortedData.map(item => item.views || 0);

        this.charts.views.data.labels = labels;
        this.charts.views.data.datasets[0].data = viewsData;
        this.charts.views.update();
    }

    updateCompletionChart(data) {
        if (!this.charts.completion || !data || data.length === 0) return;

        // 处理完播率数据
        const completionRates = data.map(item => {
            const rate = item.completion_rate || 0;
            return typeof rate === 'string' ? parseFloat(rate.replace('%', '')) : rate;
        });

        // 分组统计
        const ranges = [
            { label: '0-20%', min: 0, max: 20, count: 0 },
            { label: '21-40%', min: 21, max: 40, count: 0 },
            { label: '41-60%', min: 41, max: 60, count: 0 },
            { label: '61-80%', min: 61, max: 80, count: 0 },
            { label: '81-100%', min: 81, max: 100, count: 0 }
        ];

        completionRates.forEach(rate => {
            const range = ranges.find(r => rate >= r.min && rate <= r.max);
            if (range) range.count++;
        });

        this.charts.completion.data.labels = ranges.map(r => r.label);
        this.charts.completion.data.datasets[0].data = ranges.map(r => r.count);
        this.charts.completion.update();
    }

    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (!statusElement) return;

        if (connected) {
            statusElement.className = 'badge bg-success';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> 已连接';
        } else {
            statusElement.className = 'badge bg-danger';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> 已断开';
        }
    }

    updateLastUpdatedTime() {
        const element = document.getElementById('lastUpdated');
        if (element) {
            const now = new Date();
            element.textContent = `最后更新: ${now.toLocaleTimeString()}`;
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.add('show');
            } else {
                overlay.classList.remove('show');
            }
        }
    }

    showNotification(message, type = 'info') {
        const toast = document.getElementById('notificationToast');
        const toastBody = toast.querySelector('.toast-body');
        
        if (toastBody) {
            toastBody.textContent = message;
        }
        
        // 更新图标颜色
        const icon = toast.querySelector('.toast-header i');
        if (icon) {
            icon.className = type === 'error' 
                ? 'fas fa-exclamation-circle text-danger me-2'
                : 'fas fa-info-circle text-primary me-2';
        }
        
        // 显示Toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            // 添加更新动画
            element.style.transform = 'scale(1.1)';
            element.textContent = value;
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatPublishTime(publishTime) {
        if (!publishTime) return '未知时间';
        
        try {
            // 处理不同的时间格式
            let date;
            if (typeof publishTime === 'string') {
                date = new Date(publishTime);
            } else if (typeof publishTime === 'number') {
                // Unix时间戳
                date = new Date(publishTime * 1000);
            } else {
                date = new Date(publishTime);
            }
            
            if (isNaN(date.getTime())) {
                return '未知时间';
            }
            
            return date.toLocaleDateString('zh-CN');
        } catch (error) {
            console.error('Failed to format publish time:', error);
            return '未知时间';
        }
    }

    generateVideoUrl(videoId, author) {
        if (videoId && author) {
            return `https://www.tiktok.com/@${author}/video/${videoId}`;
        }
        return '#';
    }

    truncateUrl(url) {
        // 检查url是否存在且不为undefined
        if (!url || typeof url !== 'string') {
            return '暂无链接';
        }
        if (url.length > 30) {
            return url.substring(0, 27) + '...';
        }
        return url;
    }

    getPercentageClass(percentage) {
        const value = typeof percentage === 'string' 
            ? parseFloat(percentage.replace('%', '')) 
            : percentage;
        
        if (value >= 25) return 'percentage-high';
        if (value >= 15) return 'percentage-medium';
        return 'percentage-low';
    }

    calculateDuration(item) {
        // 模拟计算视频时长
        const watchTime = typeof item.avg_watch_time === 'string' 
            ? parseFloat(item.avg_watch_time) 
            : item.avg_watch_time || 0;
        
        const estimatedDuration = Math.round(watchTime * 1.5);
        return `${estimatedDuration}s`;
    }

    async checkApiStatus() {
        try {
            const response = await fetch('/api/auth_status');
            const result = await response.json();
            
            this.updateApiStatus(result);
        } catch (error) {
            console.error('Failed to check API status:', error);
        }
    }

    updateApiStatus(status) {
        const apiTypeElement = document.getElementById('apiType');
        const authBtn = document.getElementById('authBtn');
        
        if (apiTypeElement) {
            switch(status.api_type) {
                case 'official':
                    if (status.authenticated) {
                        apiTypeElement.textContent = '官方API已授权';
                        apiTypeElement.parentElement.className = 'badge bg-success ms-2';
                        if (authBtn) authBtn.style.display = 'none';
                    } else {
                        apiTypeElement.textContent = '官方API未授权';
                        apiTypeElement.parentElement.className = 'badge bg-warning ms-2';
                        if (authBtn) {
                            authBtn.style.display = 'inline-block';
                            authBtn.onclick = () => this.authenticateWithTikTok();
                        }
                    }
                    break;
                case 'third_party':
                    apiTypeElement.textContent = `第三方API: ${status.username || '已配置'}`;
                    apiTypeElement.parentElement.className = 'badge bg-info ms-2';
                    if (authBtn) authBtn.style.display = 'none';
                    break;
                case 'none':
                default:
                    apiTypeElement.textContent = '未配置API';
                    apiTypeElement.parentElement.className = 'badge bg-secondary ms-2';
                    if (authBtn) authBtn.style.display = 'none';
                    break;
            }
        }
    }

    authenticateWithTikTok() {
        // 跳转到TikTok授权页面
        window.location.href = '/auth';
    }

    updateStatusMessage(status, message) {
        const statusAlert = document.getElementById('statusAlert');
        const statusMessage = document.getElementById('statusMessage');
        
        if (!statusAlert || !statusMessage) return;
        
        let alertClass = 'alert-info';
        let showConfigButton = false;
        
        switch(status) {
            case 'need_config':
                alertClass = 'alert-warning';
                showConfigButton = true;
                break;
            case 'need_auth':
                alertClass = 'alert-warning';
                break;
            case 'success':
                alertClass = 'alert-success';
                break;
            case 'error':
                alertClass = 'alert-danger';
                break;
            case 'api_limitation':
                alertClass = 'alert-info';
                message = message + ' 当前显示演示数据。';
                break;
            case 'no_data':
                alertClass = 'alert-secondary';
                break;
            case 'demo':
                alertClass = 'alert-info';
                showConfigButton = true;
                break;
        }
        
        // 更新alert样式
        statusAlert.className = `alert ${alertClass}`;
        statusMessage.textContent = message;
        
        // 显示或隐藏配置按钮
        const configButton = statusAlert.querySelector('.btn-outline-primary');
        if (configButton) {
            configButton.style.display = showConfigButton ? 'block' : 'none';
        }
        
        // 显示状态消息
        if (status !== 'success' || (status === 'success' && this.currentData.length === 0)) {
            statusAlert.style.display = 'block';
        } else {
            statusAlert.style.display = 'none';
        }
        
        console.log('Status message:', message);
    }
    
    showAuthorizationModal() {
        // 避免重复弹出
        if (this.authModalShown) {
            return;
        }
        this.authModalShown = true;
        
        // 延迟3秒后弹出，避免过于突兀
        setTimeout(() => {
            const confirmed = confirm('🔐 检测到您还未授权TikTok账号！\n\n为了获取真实的数据分析，需要授权您的TikTok账号。\n\n点击"确定"开始授权，点击"取消"继续查看演示数据。');
            
            if (confirmed) {
                this.authenticateWithTikTok();
            } else {
                // 用户选择取消，5分钟后可以再次提醒
                setTimeout(() => {
                    this.authModalShown = false;
                }, 300000); // 5分钟
            }
        }, 3000);
    }

    startHttpPolling() {
        if (this.pollingInterval) {
            return; // 已经在轮询了
        }
        
        console.log('Starting HTTP polling as WebSocket fallback...');
        
        // 立即执行一次
        this.fetchDataViaHttp();
        
        // 每30秒轮询一次
        this.pollingInterval = setInterval(() => {
            if (!this.isConnected) {
                this.fetchDataViaHttp();
            } else {
                // WebSocket重新连接，停止轮询
                this.stopHttpPolling();
            }
        }, 30000);
    }

    stopHttpPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log('Stopped HTTP polling');
        }
    }

    async fetchDataViaHttp() {
        try {
            const response = await fetch('/api/data');
            const data = await response.json();
            
            console.log('Data fetched via HTTP:', data);
            
            if (data.success && data.videos) {
                this.currentData = data.videos;
                this.updateData(this.currentData);
                this.updateStatusMessage(data.status, data.message);
                
                if (data.status === 'success' && this.currentData.length > 0) {
                    this.showNotification('数据已更新 (HTTP)');
                }
            }
        } catch (error) {
            console.error('HTTP polling error:', error);
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    new TikTokAnalyticsDashboard();
});

// 全局错误处理
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// 处理未捕获的Promise拒绝
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
}); 