// Dashboard de Analytics y Reportes Avanzados para JUNO EXPRESS
class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.realTimeInterval = null;
        this.currentPeriod = '7d';
        this.autoRefresh = true;
        this.refreshInterval = 30000; // 30 segundos
        this.init();
    }

    init() {
        this.createDashboardLayout();
        this.setupEventListeners();
        this.loadInitialData();
        this.startRealTimeUpdates();
        console.log('Analytics Dashboard initialized');
    }

    createDashboardLayout() {
        // Crear estructura del dashboard
        const dashboardHTML = `
            <div id="analytics-dashboard" class="analytics-dashboard">
                <!-- Header -->
                <div class="dashboard-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h4 class="mb-0">Analytics JUNO EXPRESS</h4>
                            <small class="text-muted">Panel de análisis en tiempo real</small>
                        </div>
                        <div class="dashboard-controls">
                            <select id="period-selector" class="form-select form-select-sm me-2">
                                <option value="24h">Últimas 24 horas</option>
                                <option value="7d" selected>Últimos 7 días</option>
                                <option value="30d">Últimos 30 días</option>
                                <option value="90d">Últimos 90 días</option>
                            </select>
                            <div class="btn-group btn-group-sm me-2">
                                <button class="btn btn-outline-primary active" data-refresh="30s">30s</button>
                                <button class="btn btn-outline-primary" data-refresh="1m">1m</button>
                                <button class="btn btn-outline-primary" data-refresh="5m">5m</button>
                                <button class="btn btn-outline-secondary" id="toggle-auto-refresh">
                                    <i class="fas fa-pause"></i>
                                </button>
                            </div>
                            <button class="btn btn-primary btn-sm" id="export-report">
                                <i class="fas fa-download me-1"></i> Exportar
                            </button>
                        </div>
                    </div>
                </div>

                <!-- KPI Cards -->
                <div class="row mb-4">
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="kpi-card sales-kpi">
                            <div class="kpi-header">
                                <div class="kpi-icon">
                                    <i class="fas fa-dollar-sign"></i>
                                </div>
                                <div class="kpi-trend positive">
                                    <i class="fas fa-arrow-up"></i> +12.5%
                                </div>
                            </div>
                            <div class="kpi-content">
                                <h3 class="kpi-value">S/. <span id="total-sales">15,000</span></h3>
                                <p class="kpi-label">Ventas Totales</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="kpi-card tickets-kpi">
                            <div class="kpi-header">
                                <div class="kpi-icon">
                                    <i class="fas fa-ticket-alt"></i>
                                </div>
                                <div class="kpi-trend positive">
                                    <i class="fas fa-arrow-up"></i> +8.3%
                                </div>
                            </div>
                            <div class="kpi-content">
                                <h3 class="kpi-value"><span id="total-tickets">250</span></h3>
                                <p class="kpi-label">Boletos Vendidos</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="kpi-card customers-kpi">
                            <div class="kpi-header">
                                <div class="kpi-icon">
                                    <i class="fas fa-users"></i>
                                </div>
                                <div class="kpi-trend positive">
                                    <i class="fas fa-arrow-up"></i> +15.2%
                                </div>
                            </div>
                            <div class="kpi-content">
                                <h3 class="kpi-value"><span id="total-customers">500</span></h3>
                                <p class="kpi-label">Clientes Totales</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="kpi-card conversion-kpi">
                            <div class="kpi-header">
                                <div class="kpi-icon">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div class="kpi-trend negative">
                                    <i class="fas fa-arrow-down"></i> -2.1%
                                </div>
                            </div>
                            <div class="kpi-content">
                                <h3 class="kpi-value"><span id="conversion-rate">12.5</span>%</h3>
                                <p class="kpi-label">Tasa Conversión</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row 1 -->
                <div class="row mb-4">
                    <div class="col-lg-8 mb-3">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Ventas y Tendencias</h5>
                                <div class="chart-controls">
                                    <button class="btn btn-sm btn-outline-secondary" data-chart="sales-trend" data-type="line">
                                        <i class="fas fa-chart-line"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" data-chart="sales-trend" data-type="bar">
                                        <i class="fas fa-chart-bar"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="chart-container">
                                <canvas id="sales-trend-chart"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 mb-3">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Ventas por Ruta</h5>
                            </div>
                            <div class="chart-container">
                                <canvas id="route-sales-chart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row 2 -->
                <div class="row mb-4">
                    <div class="col-lg-6 mb-3">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Distribución Horaria</h5>
                            </div>
                            <div class="chart-container">
                                <canvas id="hourly-distribution-chart"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6 mb-3">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Segmentación de Clientes</h5>
                            </div>
                            <div class="chart-container">
                                <canvas id="customer-segments-chart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Real-time Metrics -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Métricas en Tiempo Real</h5>
                                <div class="real-time-indicator">
                                    <span class="indicator-dot"></span>
                                    <span>Actualizando...</span>
                                </div>
                            </div>
                            <div class="real-time-metrics">
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="metric-item">
                                            <div class="metric-label">Usuarios Activos</div>
                                            <div class="metric-value" id="active-users">0</div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="metric-item">
                                            <div class="metric-label">Visitas Página</div>
                                            <div class="metric-value" id="page-views">0</div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="metric-item">
                                            <div class="metric-label">Ventas Última Hora</div>
                                            <div class="metric-value">S/. <span id="sales-last-hour">0</span></div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="metric-item">
                                            <div class="metric-label">Tiempo Respuesta</div>
                                            <div class="metric-value"><span id="response-time">0</span>ms</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Predictions -->
                <div class="row mb-4">
                    <div class="col-lg-8 mb-3">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Predicción de Ventas</h5>
                                <div class="prediction-confidence">
                                    <span>Confianza: </span>
                                    <span id="prediction-confidence">85%</span>
                                </div>
                            </div>
                            <div class="chart-container">
                                <canvas id="sales-forecast-chart"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 mb-3">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5>Recomendaciones</h5>
                            </div>
                            <div class="recommendations-list" id="recommendations-list">
                                <!-- Las recomendaciones se cargarán dinámicamente -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar al DOM
        document.body.insertAdjacentHTML('beforeend', dashboardHTML);
        
        // Agregar estilos
        this.addDashboardStyles();
    }

    addDashboardStyles() {
        const styles = `
            <style id="analytics-dashboard-styles">
                .analytics-dashboard {
                    padding: 20px;
                    background: #f8f9fa;
                    min-height: 100vh;
                }
                
                .dashboard-header {
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                
                .dashboard-controls {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .kpi-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    height: 100%;
                }
                
                .kpi-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
                }
                
                .kpi-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                
                .kpi-icon {
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    color: white;
                }
                
                .sales-kpi .kpi-icon { background: linear-gradient(135deg, #10b981, #059669); }
                .tickets-kpi .kpi-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
                .customers-kpi .kpi-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
                .conversion-kpi .kpi-icon { background: linear-gradient(135deg, #ef4444, #dc2626); }
                
                .kpi-trend {
                    font-size: 12px;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }
                
                .kpi-trend.positive { color: #10b981; }
                .kpi-trend.negative { color: #ef4444; }
                
                .kpi-value {
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 5px;
                    color: #1f2937;
                }
                
                .kpi-label {
                    color: #6b7280;
                    font-size: 14px;
                    margin: 0;
                }
                
                .chart-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    height: 100%;
                }
                
                .chart-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                
                .chart-header h5 {
                    margin: 0;
                    color: #1f2937;
                    font-weight: 600;
                }
                
                .chart-controls {
                    display: flex;
                    gap: 5px;
                }
                
                .chart-container {
                    position: relative;
                    height: 300px;
                }
                
                .real-time-indicator {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 14px;
                    color: #6b7280;
                }
                
                .indicator-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #10b981;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                .real-time-metrics {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                }
                
                .metric-item {
                    text-align: center;
                    padding: 10px;
                }
                
                .metric-label {
                    font-size: 12px;
                    color: #6b7280;
                    margin-bottom: 5px;
                }
                
                .metric-value {
                    font-size: 24px;
                    font-weight: 700;
                    color: #1f2937;
                }
                
                .prediction-confidence {
                    font-size: 14px;
                    color: #6b7280;
                }
                
                .recommendations-list {
                    max-height: 300px;
                    overflow-y: auto;
                }
                
                .recommendation-item {
                    padding: 12px;
                    border-left: 4px solid #3b82f6;
                    background: #f8f9fa;
                    margin-bottom: 10px;
                    border-radius: 0 8px 8px 0;
                }
                
                .recommendation-item h6 {
                    margin: 0 0 5px 0;
                    color: #1f2937;
                    font-size: 14px;
                }
                
                .recommendation-item p {
                    margin: 0;
                    font-size: 12px;
                    color: #6b7280;
                }
                
                /* Responsive */
                @media (max-width: 768px) {
                    .analytics-dashboard {
                        padding: 10px;
                    }
                    
                    .dashboard-controls {
                        flex-direction: column;
                        align-items: stretch;
                        gap: 10px;
                    }
                    
                    .kpi-value {
                        font-size: 24px;
                    }
                    
                    .chart-container {
                        height: 250px;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    setupEventListeners() {
        // Selector de período
        document.getElementById('period-selector').addEventListener('change', (e) => {
            this.currentPeriod = e.target.value;
            this.refreshData();
        });

        // Controles de auto-refresh
        document.querySelectorAll('[data-refresh]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const interval = e.target.dataset.refresh;
                this.setRefreshInterval(interval);
                
                // Actualizar botón activo
                document.querySelectorAll('[data-refresh]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Toggle auto-refresh
        document.getElementById('toggle-auto-refresh').addEventListener('click', () => {
            this.toggleAutoRefresh();
        });

        // Exportar reporte
        document.getElementById('export-report').addEventListener('click', () => {
            this.exportReport();
        });

        // Controles de charts
        document.querySelectorAll('[data-chart]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chartId = e.target.dataset.chart;
                const chartType = e.target.dataset.type;
                this.switchChartType(chartId, chartType);
            });
        });
    }

    async loadInitialData() {
        try {
            // Cargar métricas principales
            await this.loadSalesMetrics();
            await this.loadCustomerMetrics();
            await this.loadRouteAnalytics();
            
            // Inicializar charts
            this.initializeCharts();
            
            // Cargar predicciones
            await this.loadPredictions();
            
            // Cargar recomendaciones
            await this.loadRecommendations();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadSalesMetrics() {
        try {
            const response = await fetch(`/api/analytics/sales?period=${this.currentPeriod}`);
            if (response.ok) {
                const data = await response.json();
                this.updateSalesKPIs(data);
            }
        } catch (error) {
            console.error('Error loading sales metrics:', error);
        }
    }

    async loadCustomerMetrics() {
        try {
            const response = await fetch(`/api/analytics/customers?period=${this.currentPeriod}`);
            if (response.ok) {
                const data = await response.json();
                this.updateCustomerKPIs(data);
            }
        } catch (error) {
            console.error('Error loading customer metrics:', error);
        }
    }

    async loadRouteAnalytics() {
        try {
            const response = await fetch(`/api/analytics/routes?period=${this.currentPeriod}`);
            if (response.ok) {
                const data = await response.json();
                this.updateRouteCharts(data);
            }
        } catch (error) {
            console.error('Error loading route analytics:', error);
        }
    }

    async loadPredictions() {
        try {
            const response = await fetch(`/api/analytics/predictions`);
            if (response.ok) {
                const data = await response.json();
                this.updatePredictionCharts(data);
            }
        } catch (error) {
            console.error('Error loading predictions:', error);
        }
    }

    async loadRecommendations() {
        try {
            const response = await fetch(`/api/analytics/recommendations`);
            if (response.ok) {
                const data = await response.json();
                this.updateRecommendations(data);
            }
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    updateSalesKPIs(data) {
        document.getElementById('total-sales').textContent = this.formatNumber(data.total_sales);
        document.getElementById('total-tickets').textContent = data.total_tickets;
        document.getElementById('conversion-rate').textContent = data.conversion_rate.toFixed(1);
    }

    updateCustomerKPIs(data) {
        document.getElementById('total-customers').textContent = data.total_customers;
    }

    updateRouteCharts(data) {
        // Actualizar chart de ventas por ruta
        if (this.charts.routeSales) {
            const labels = data.map(route => `${route.origin}-${route.destination}`);
            const values = data.map(route => route.total_sales);
            
            this.charts.routeSales.data.labels = labels;
            this.charts.routeSales.data.datasets[0].data = values;
            this.charts.routeSales.update();
        }
    }

    updatePredictionCharts(data) {
        // Actualizar confianza
        document.getElementById('prediction-confidence').textContent = `${(data.confidence_level * 100).toFixed(0)}%`;
        
        // Actualizar chart de predicción
        if (this.charts.salesForecast && data.sales_forecast) {
            const labels = data.sales_forecast.map(f => f.date);
            const values = data.sales_forecast.map(f => f.predicted_sales);
            
            this.charts.salesForecast.data.labels = labels;
            this.charts.salesForecast.data.datasets[0].data = values;
            this.charts.salesForecast.update();
        }
    }

    updateRecommendations(data) {
        const container = document.getElementById('recommendations-list');
        
        if (data && data.length > 0) {
            container.innerHTML = data.map(rec => `
                <div class="recommendation-item">
                    <h6>${rec.title}</h6>
                    <p>${rec.description}</p>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="text-muted">No hay recomendaciones disponibles en este momento.</p>';
        }
    }

    initializeCharts() {
        // Chart de tendencia de ventas
        const salesTrendCtx = document.getElementById('sales-trend-chart').getContext('2d');
        this.charts.salesTrend = new Chart(salesTrendCtx, {
            type: 'line',
            data: {
                labels: this.getLastDays(7),
                datasets: [{
                    label: 'Ventas',
                    data: [12000, 15000, 13500, 17000, 16000, 18500, 15000],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => 'S/. ' + value.toLocaleString()
                        }
                    }
                }
            }
        });

        // Chart de ventas por ruta
        const routeSalesCtx = document.getElementById('route-sales-chart').getContext('2d');
        this.charts.routeSales = new Chart(routeSalesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Chincha-Pisco', 'Chincha-Ica', 'Pisco-Ica'],
                datasets: [{
                    data: [5000, 7000, 3000],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });

        // Chart de distribución horaria
        const hourlyCtx = document.getElementById('hourly-distribution-chart').getContext('2d');
        this.charts.hourlyDistribution = new Chart(hourlyCtx, {
            type: 'bar',
            data: {
                labels: ['6:00', '8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
                datasets: [{
                    label: 'Boletos',
                    data: [15, 45, 30, 25, 60, 35, 80, 40, 20],
                    backgroundColor: '#10b981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // Chart de segmentación de clientes
        const segmentsCtx = document.getElementById('customer-segments-chart').getContext('2d');
        this.charts.customerSegments = new Chart(segmentsCtx, {
            type: 'pie',
            data: {
                labels: ['Nuevos', 'Recurrentes', 'Inactivos'],
                datasets: [{
                    data: [200, 150, 150],
                    backgroundColor: ['#10b981', '#3b82f6', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });

        // Chart de predicción de ventas
        const forecastCtx = document.getElementById('sales-forecast-chart').getContext('2d');
        this.charts.salesForecast = new Chart(forecastCtx, {
            type: 'line',
            data: {
                labels: this.getNextDays(7),
                datasets: [{
                    label: 'Predicción',
                    data: [16000, 17000, 16500, 18000, 17500, 19000, 18500],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderDash: [5, 5],
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => 'S/. ' + value.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    startRealTimeUpdates() {
        if (this.autoRefresh) {
            this.realTimeInterval = setInterval(() => {
                this.updateRealTimeMetrics();
            }, this.refreshInterval);
        }
    }

    async updateRealTimeMetrics() {
        try {
            const response = await fetch('/api/analytics/real-time');
            if (response.ok) {
                const data = await response.json();
                
                document.getElementById('active-users').textContent = data.active_users;
                document.getElementById('page-views').textContent = data.page_views;
                document.getElementById('sales-last-hour').textContent = this.formatNumber(data.sales_last_hour);
                document.getElementById('response-time').textContent = data.server_response_time.toFixed(0);
                
                // Actualizar indicador
                const indicator = document.querySelector('.indicator-dot');
                indicator.style.background = '#10b981';
                
                setTimeout(() => {
                    indicator.style.background = '#6b7280';
                }, 2000);
            }
        } catch (error) {
            console.error('Error updating real-time metrics:', error);
        }
    }

    setRefreshInterval(interval) {
        const intervals = {
            '30s': 30000,
            '1m': 60000,
            '5m': 300000
        };
        
        this.refreshInterval = intervals[interval];
        
        if (this.autoRefresh) {
            clearInterval(this.realTimeInterval);
            this.startRealTimeUpdates();
        }
    }

    toggleAutoRefresh() {
        this.autoRefresh = !this.autoRefresh;
        const btn = document.getElementById('toggle-auto-refresh');
        const icon = btn.querySelector('i');
        
        if (this.autoRefresh) {
            icon.className = 'fas fa-pause';
            this.startRealTimeUpdates();
        } else {
            icon.className = 'fas fa-play';
            clearInterval(this.realTimeInterval);
        }
    }

    async refreshData() {
        // Mostrar loading
        this.showLoading(true);
        
        try {
            await this.loadSalesMetrics();
            await this.loadCustomerMetrics();
            await this.loadRouteAnalytics();
            await this.loadPredictions();
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        // Implementar indicador de carga
        const charts = document.querySelectorAll('.chart-container');
        charts.forEach(chart => {
            if (show) {
                chart.style.opacity = '0.5';
            } else {
                chart.style.opacity = '1';
            }
        });
    }

    switchChartType(chartId, type) {
        if (this.charts[chartId]) {
            this.charts[chartId].config.type = type;
            this.charts[chartId].update();
        }
    }

    exportReport() {
        // Implementar exportación a PDF/Excel
        const reportData = {
            period: this.currentPeriod,
            timestamp: new Date().toISOString(),
            kpis: {
                total_sales: document.getElementById('total-sales').textContent,
                total_tickets: document.getElementById('total-tickets').textContent,
                total_customers: document.getElementById('total-customers').textContent,
                conversion_rate: document.getElementById('conversion-rate').textContent
            }
        };
        
        // Crear y descargar archivo
        const dataStr = JSON.stringify(reportData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `juno-analytics-${this.currentPeriod}-${Date.now()}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    // Métodos de utilidad
    getLastDays(days) {
        const dates = [];
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString('es-PE', { month: 'short', day: 'numeric' }));
        }
        return dates;
    }

    getNextDays(days) {
        const dates = [];
        for (let i = 1; i <= days; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);
            dates.push(date.toLocaleDateString('es-PE', { month: 'short', day: 'numeric' }));
        }
        return dates;
    }

    formatNumber(num) {
        return new Intl.NumberFormat('es-PE').format(num);
    }

    // Métodos públicos
    destroy() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
        }
        
        // Destruir charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        // Remover dashboard del DOM
        const dashboard = document.getElementById('analytics-dashboard');
        if (dashboard) dashboard.remove();
        
        // Remover estilos
        const styles = document.getElementById('analytics-dashboard-styles');
        if (styles) styles.remove();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si estamos en página de analytics
    if (window.location.pathname.includes('analytics') || window.location.pathname.includes('admin')) {
        window.analyticsDashboard = new AnalyticsDashboard();
        
        // Exponer globalmente
        window.AnalyticsDashboard = AnalyticsDashboard;
    }
});

// Exportar para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnalyticsDashboard;
}
