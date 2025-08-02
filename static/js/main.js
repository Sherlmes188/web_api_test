// TikTok数据分析面板 JavaScript
class TikTokAnalyticsDashboard {
    constructor() {
        this.socket = null;
        this.currentData = [];
        this.dataStatus = 'loading';
        this.statusMessage = '';
        this.charts = {};
        this.isConnected = false;
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
        try {
            this.socket = io();
            
            // 连接成功
            this.socket.on('connect', () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus(true);
            });

            // 连接断开
            this.socket.on('disconnect', () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
            });

            // 数据更新
            this.socket.on('data_update', (response) => {
                console.log('Data updated via WebSocket:', response);
                
                // 处理新的数据结构
                if (response) {
                    this.currentData = response.videos || [];
                    this.updateData(this.currentData);
                    this.updateStatusMessage(response.status, response.message);
                    
                    if (response.status === 'success' && this.currentData.length > 0) {
                        this.showNotification('数据已更新');
                    }
                }
            });

        } catch (error) {
            console.error('WebSocket initialization failed:', error);
            this.updateConnectionStatus(false);
        }
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
        
        // 计算统计数据
        const totalVideos = data.length;
        const totalViews = data.reduce((sum, item) => sum + (item.views || 0), 0);
        const totalFollowers = data.reduce((sum, item) => sum + (item.new_followers || 0), 0);
        
        // 计算平均完播率
        const completionRates = data.map(item => {
            const rate = typeof item.completion_rate === 'string' 
                ? parseFloat(item.completion_rate.replace('%', '')) 
                : item.completion_rate || 0;
            return rate;
        }).filter(rate => !isNaN(rate));
        
        const avgCompletionRate = completionRates.length > 0 
            ? (completionRates.reduce((sum, rate) => sum + rate, 0) / completionRates.length).toFixed(1)
            : 0;

        // 更新DOM元素
        this.updateElement('totalVideos', totalVideos);
        this.updateElement('totalViews', this.formatNumber(totalViews));
        this.updateElement('avgCompletionRate', `${avgCompletionRate}%`);
        this.updateElement('totalFollowers', totalFollowers);
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

        // 处理服务标签样式
        const serviceClass = item.service === 'IMX.TOOLS' ? 'service-imx' : 'service-dna';
        
        // 处理状态显示
        const statusHtml = item.performance === 1 
            ? '<span class="status-indicator"><span class="status-dot active"></span>活跃</span>'
            : '<span class="status-indicator"><span class="status-dot inactive"></span>非活跃</span>';

        row.innerHTML = `
            <td>
                <a href="${item.video_link}" target="_blank" class="video-link">
                    ${this.truncateUrl(item.video_link)}
                </a>
            </td>
            <td>
                <span class="product-tag">${item.product}</span>
            </td>
            <td>
                <span class="badge service-badge ${serviceClass}">${item.service}</span>
            </td>
            <td>${item.publish_date}</td>
            <td class="number-cell">${this.formatNumber(item.views)}</td>
            <td class="number-cell">${item.avg_watch_time}s</td>
            <td class="number-cell">${item.new_followers}</td>
            <td class="percentage-cell ${this.getPercentageClass(completionRate)}">${completionRate}</td>
            <td class="number-cell">${item.bounce_rate}</td>
            <td class="number-cell">${item.watch_duration}</td>
            <td class="number-cell">${item.gmv_max_views}</td>
            <td class="number-cell">${this.calculateDuration(item)}</td>
            <td>${statusHtml}</td>
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
        this.updateViewsChart();
        this.updateCompletionChart();
    }

    updateViewsChart() {
        if (!this.charts.views) return;

        const labels = this.currentData.map(item => {
            const date = new Date(item.publish_date);
            return `${date.getMonth() + 1}/${date.getDate()}`;
        });

        const views = this.currentData.map(item => item.views);

        this.charts.views.data.labels = labels;
        this.charts.views.data.datasets[0].data = views;
        this.charts.views.update();
    }

    updateCompletionChart() {
        if (!this.charts.completion) return;

        // 计算完播率分布
        const completionRates = this.currentData.map(item => {
            const rate = typeof item.completion_rate === 'string' 
                ? parseFloat(item.completion_rate.replace('%', '')) 
                : item.completion_rate || 0;
            return rate;
        }).filter(rate => !isNaN(rate));

        const high = completionRates.filter(rate => rate >= 25).length;
        const medium = completionRates.filter(rate => rate >= 15 && rate < 25).length;
        const low = completionRates.filter(rate => rate < 15).length;

        this.charts.completion.data.datasets[0].data = [high, medium, low];
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

    truncateUrl(url) {
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
        // 更新状态消息显示
        const statusElement = document.querySelector('.navbar .badge');
        if (statusElement) {
            // 更新API状态显示
            switch(status) {
                case 'need_config':
                    statusElement.textContent = '需要配置';
                    statusElement.className = 'badge bg-warning';
                    break;
                case 'need_auth':
                    statusElement.textContent = '需要授权';
                    statusElement.className = 'badge bg-info';
                    // 自动弹出授权确认框
                    this.showAuthorizationModal();
                    break;
                case 'success':
                    statusElement.textContent = '已连接';
                    statusElement.className = 'badge bg-success';
                    break;
                case 'error':
                    statusElement.textContent = '错误';
                    statusElement.className = 'badge bg-danger';
                    break;
                default:
                    statusElement.textContent = '未知';
                    statusElement.className = 'badge bg-secondary';
            }
        }
        
        // 显示授权按钮
        const authBtn = document.getElementById('authBtn');
        if (authBtn) {
            if (status === 'need_auth') {
                authBtn.style.display = 'inline-block';
            } else {
                authBtn.style.display = 'none';
            }
        }
        
        // 如果有消息，可以在控制台显示
        if (message) {
            console.log('Status message:', message);
        }
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