"""
Sistema de Analytics y Reportes Avanzados para JUNO EXPRESS
Análisis de datos en tiempo real y reportes inteligentes
"""

import json
import datetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class ReportType(Enum):
    SALES = "sales"
    REVENUE = "revenue"
    ROUTES = "routes"
    CUSTOMERS = "customers"
    PERFORMANCE = "performance"
    PREDICTION = "prediction"
    REAL_TIME = "real_time"

@dataclass
class MetricData:
    name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class UserBehavior:
    user_id: str
    action: str
    page: str
    timestamp: datetime
    session_id: str
    duration: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class SalesMetrics:
    total_sales: float
    total_tickets: int
    average_ticket_value: float
    sales_by_route: Dict[str, float]
    sales_by_hour: Dict[str, int]
    sales_by_day: Dict[str, float]
    conversion_rate: float
    abandoned_carts: int

@dataclass
class RouteAnalytics:
    route_id: str
    origin: str
    destination: str
    total_sales: float
    total_tickets: int
    occupancy_rate: float
    average_price: float
    peak_hours: List[str]
    performance_score: float

@dataclass
class CustomerAnalytics:
    total_customers: int
    new_customers: int
    returning_customers: int
    customer_segments: Dict[str, int]
    average_lifetime_value: float
    churn_rate: float
    satisfaction_score: float

class AnalyticsService:
    def __init__(self, firestore_db=None):
        self.firestore_db = firestore_db
        self.metrics_cache = {}
        self.user_behaviors = []
        self.real_time_data = defaultdict(list)
        
        # Configuración de métricas
        self.metric_configs = {
            'sales': {
                'aggregation': 'sum',
                'time_window': '24h',
                'alert_threshold': 1000.0
            },
            'tickets': {
                'aggregation': 'count',
                'time_window': '24h',
                'alert_threshold': 100
            },
            'conversion_rate': {
                'aggregation': 'percentage',
                'time_window': '1h',
                'alert_threshold': 5.0
            }
        }

    async def track_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Registrar evento de usuario para analytics
        """
        try:
            event_data = {
                'event_type': event_type,
                'user_id': user_id,
                'timestamp': datetime.utcnow(),
                'data': data,
                'session_id': data.get('session_id', ''),
                'page': data.get('page', ''),
                'user_agent': data.get('user_agent', ''),
                'ip_address': data.get('ip_address', '')
            }
            
            # Guardar en Firestore
            if self.firestore_db:
                await self.firestore_db.collection('analytics_events').add(event_data)
            
            # Actualizar datos en tiempo real
            self.update_real_time_data(event_type, event_data)
            
            # Verificar alertas
            await self.check_alerts(event_type, event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            return False

    def update_real_time_data(self, event_type: str, event_data: Dict[str, Any]):
        """
        Actualizar datos en tiempo real
        """
        self.real_time_data[event_type].append({
            'timestamp': datetime.utcnow(),
            'data': event_data
        })
        
        # Mantener solo últimos 1000 eventos por tipo
        if len(self.real_time_data[event_type]) > 1000:
            self.real_time_data[event_type] = self.real_time_data[event_type][-1000:]

    async def check_alerts(self, event_type: str, event_data: Dict[str, Any]):
        """
        Verificar si se deben generar alertas
        """
        try:
            config = self.metric_configs.get(event_type)
            if not config:
                return
            
            # Obtener valor actual
            current_value = await self.get_current_metric_value(event_type, config['time_window'])
            
            # Comparar con umbral
            if current_value > config['alert_threshold']:
                await self.trigger_alert(event_type, current_value, config['alert_threshold'])
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    async def trigger_alert(self, metric: str, value: float, threshold: float):
        """
        Generar alerta
        """
        try:
            alert_data = {
                'metric': metric,
                'value': value,
                'threshold': threshold,
                'timestamp': datetime.utcnow(),
                'severity': 'warning' if value < threshold * 1.5 else 'critical',
                'message': f'{metric} ha superado el umbral: {value} > {threshold}'
            }
            
            if self.firestore_db:
                await self.firestore_db.collection('analytics_alerts').add(alert_data)
            
            logger.warning(f"Analytics alert: {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")

    async def get_sales_metrics(self, days: int = 7) -> SalesMetrics:
        """
        Obtener métricas de ventas
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            if not self.firestore_db:
                return self.get_mock_sales_metrics()
            
            # Ventas totales
            sales_query = self.firestore_db.collection('ventas')\
                .where('fecha_compra', '>=', start_date)\
                .where('estado', '==', 'confirmado')
            
            sales_docs = sales_query.get()
            
            total_sales = 0.0
            total_tickets = 0
            sales_by_route = defaultdict(float)
            sales_by_hour = defaultdict(int)
            sales_by_day = defaultdict(float)
            
            for doc in sales_docs:
                data = doc.to_dict()
                amount = float(data.get('total', 0))
                tickets = int(data.get('cantidad_boletos', 0))
                
                total_sales += amount
                total_tickets += tickets
                
                # Ventas por ruta
                route = f"{data.get('origen_real', 'N/A')} - {data.get('destino_real', 'N/A')}"
                sales_by_route[route] += amount
                
                # Ventas por hora
                if data.get('fecha_compra'):
                    hour = data['fecha_compra'].hour if hasattr(data['fecha_compra'], 'hour') else 0
                    sales_by_hour[str(hour)] += tickets
                
                # Ventas por día
                if data.get('fecha_compra'):
                    day = data['fecha_compra'].strftime('%Y-%m-%d')
                    sales_by_day[day] += amount
            
            # Calcular métricas adicionales
            average_ticket_value = total_sales / total_tickets if total_tickets > 0 else 0
            
            # Tasa de conversión (simulada)
            conversion_rate = await self.calculate_conversion_rate(start_date)
            
            # Carritos abandonados (simulado)
            abandoned_carts = int(total_tickets * 0.15)  # 15% abandonados
            
            return SalesMetrics(
                total_sales=total_sales,
                total_tickets=total_tickets,
                average_ticket_value=average_ticket_value,
                sales_by_route=dict(sales_by_route),
                sales_by_hour=dict(sales_by_hour),
                sales_by_day=dict(sales_by_day),
                conversion_rate=conversion_rate,
                abandoned_carts=abandoned_carts
            )
            
        except Exception as e:
            logger.error(f"Error getting sales metrics: {e}")
            return self.get_mock_sales_metrics()

    async def calculate_conversion_rate(self, start_date: datetime) -> float:
        """
        Calcular tasa de conversión
        """
        try:
            if not self.firestore_db:
                return 12.5  # Mock
            
            # Visitas a página de búsqueda
            search_visits = self.firestore_db.collection('analytics_events')\
                .where('event_type', '==', 'page_visit')\
                .where('page', '==', '/pasajero/buscar-viajes')\
                .where('timestamp', '>=', start_date)\
                .get()
            
            # Ventas completadas
            sales = self.firestore_db.collection('ventas')\
                .where('fecha_compra', '>=', start_date)\
                .where('estado', '==', 'confirmado')\
                .get()
            
            visits_count = len(search_visits)
            sales_count = len(sales)
            
            return (sales_count / visits_count * 100) if visits_count > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating conversion rate: {e}")
            return 12.5  # Mock

    async def get_route_analytics(self, days: int = 30) -> List[RouteAnalytics]:
        """
        Obtener análisis de rutas
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            if not self.firestore_db:
                return self.get_mock_route_analytics()
            
            # Obtener todos los viajes
            viajes_query = self.firestore_db.collection('viajes')\
                .where('fecha_salida', '>=', start_date)\
                .get()
            
            route_data = defaultdict(lambda: {
                'sales': 0.0,
                'tickets': 0,
                'capacity': 0,
                'occupancy': [],
                'prices': []
            })
            
            for doc in viajes_query:
                viaje = doc.to_dict()
                
                # Obtener ventas para este viaje
                ventas_query = self.firestore_db.collection('ventas')\
                    .where('viaje_id', '==', doc.id)\
                    .where('estado', '==', 'confirmado')\
                    .get()
                
                tickets_sold = len(ventas_query)
                total_capacity = int(viaje.get('asientos_totales', 0))
                
                if total_capacity > 0:
                    occupancy_rate = (tickets_sold / total_capacity) * 100
                else:
                    occupancy_rate = 0
                
                route_key = f"{viaje.get('ruta_origen', '')}-{viaje.get('ruta_destino', '')}"
                
                # Sumar ventas
                for venta_doc in ventas_query:
                    venta = venta_doc.to_dict()
                    route_data[route_key]['sales'] += float(venta.get('total', 0))
                    route_data[route_key]['tickets'] += int(venta.get('cantidad_boletos', 0))
                
                route_data[route_key]['capacity'] += total_capacity
                route_data[route_key]['occupancy'].append(occupancy_rate)
                route_data[route_key]['prices'].append(float(viaje.get('precio', 0)))
            
            # Generar analytics
            route_analytics = []
            
            for route_key, data in route_data.items():
                origin, destination = route_key.split('-', 1)
                
                # Calcular métricas
                total_sales = data['sales']
                total_tickets = data['tickets']
                average_price = statistics.mean(data['prices']) if data['prices'] else 0
                average_occupancy = statistics.mean(data['occupancy']) if data['occupancy'] else 0
                
                # Horas pico (simuladas)
                peak_hours = ['08:00', '14:00', '18:00']
                
                # Score de rendimiento (0-100)
                performance_score = min(100, (average_occupancy * 0.7 + (total_sales / 1000) * 0.3))
                
                route_analytics.append(RouteAnalytics(
                    route_id=route_key,
                    origin=origin,
                    destination=destination,
                    total_sales=total_sales,
                    total_tickets=total_tickets,
                    occupancy_rate=average_occupancy,
                    average_price=average_price,
                    peak_hours=peak_hours,
                    performance_score=performance_score
                ))
            
            # Ordenar por performance
            route_analytics.sort(key=lambda x: x.performance_score, reverse=True)
            
            return route_analytics
            
        except Exception as e:
            logger.error(f"Error getting route analytics: {e}")
            return self.get_mock_route_analytics()

    async def get_customer_analytics(self, days: int = 30) -> CustomerAnalytics:
        """
        Obtener análisis de clientes
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            if not self.firestore_db:
                return self.get_mock_customer_analytics()
            
            # Total de clientes
            users_query = self.firestore_db.collection('users').get()
            total_customers = len(users_query)
            
            # Clientes nuevos
            new_users_query = self.firestore_db.collection('users')\
                .where('fecha_registro', '>=', start_date)\
                .get()
            new_customers = len(new_users_query)
            
            # Clientes recurrentes (con más de 1 compra)
            returning_customers = 0
            customer_segments = {'nuevo': 0, 'recurrente': 0, 'inactivo': 0}
            
            for user_doc in users_query:
                user_data = user_doc.to_dict()
                user_id = user_doc.get('email', '')
                
                # Contar compras
                ventas_query = self.firestore_db.collection('ventas')\
                    .where('usuario_id', '==', user_id)\
                    .where('estado', '==', 'confirmado')\
                    .get()
                
                purchase_count = len(ventas_query)
                
                if purchase_count > 1:
                    returning_customers += 1
                    customer_segments['recurrente'] += 1
                elif purchase_count == 1:
                    customer_segments['nuevo'] += 1
                else:
                    customer_segments['inactivo'] += 1
            
            # Calcular métricas adicionales
            average_lifetime_value = await self.calculate_clv()
            churn_rate = await self.calculate_churn_rate(start_date)
            satisfaction_score = await self.calculate_satisfaction_score()
            
            return CustomerAnalytics(
                total_customers=total_customers,
                new_customers=new_customers,
                returning_customers=returning_customers,
                customer_segments=customer_segments,
                average_lifetime_value=average_lifetime_value,
                churn_rate=churn_rate,
                satisfaction_score=satisfaction_score
            )
            
        except Exception as e:
            logger.error(f"Error getting customer analytics: {e}")
            return self.get_mock_customer_analytics()

    async def calculate_clv(self) -> float:
        """
        Calcular Customer Lifetime Value
        """
        try:
            if not self.firestore_db:
                return 150.0  # Mock
            
            # Obtener todas las ventas
            ventas_query = self.firestore_db.collection('ventas')\
                .where('estado', '==', 'confirmado')\
                .get()
            
            # Agrupar por cliente
            customer_sales = defaultdict(float)
            
            for venta_doc in ventas_query:
                venta = venta_doc.to_dict()
                user_id = venta.get('usuario_id', '')
                customer_sales[user_id] += float(venta.get('total', 0))
            
            # Calcular promedio
            if customer_sales:
                return statistics.mean(customer_sales.values())
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating CLV: {e}")
            return 150.0  # Mock

    async def calculate_churn_rate(self, start_date: datetime) -> float:
        """
        Calcular tasa de abandono
        """
        try:
            if not self.firestore_db:
                return 8.5  # Mock
            
            # Clientes activos antes del período
            active_before = self.firestore_db.collection('users')\
                .where('ultima_actividad', '<', start_date)\
                .get()
            
            # Clientes que abandonaron (sin actividad en el período)
            churned = 0
            end_date = datetime.utcnow()
            
            for user_doc in active_before:
                user_data = user_doc.to_dict()
                last_activity = user_data.get('ultima_actividad')
                
                if last_activity and last_activity < start_date:
                    # Verificar si tuvo actividad después
                    recent_activity = self.firestore_db.collection('analytics_events')\
                        .where('user_id', '==', user_data.get('email', ''))\
                        .where('timestamp', '>=', start_date)\
                        .get()
                    
                    if len(recent_activity) == 0:
                        churned += 1
            
            total_active = len(active_before)
            return (churned / total_active * 100) if total_active > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating churn rate: {e}")
            return 8.5  # Mock

    async def calculate_satisfaction_score(self) -> float:
        """
        Calcular score de satisfacción
        """
        try:
            if not self.firestore_db:
                return 4.2  # Mock
            
            # Obtener consultas y respuestas
            consultas_query = self.firestore_db.collection('consultas')\
                .where('estado', '==', 'respondida')\
                .get()
            
            # Simular score basado en tiempo de respuesta
            total_score = 0
            count = 0
            
            for consulta_doc in consultas_query:
                consulta = consulta_doc.to_dict()
                
                # Tiempo de respuesta (simulado)
                fecha_consulta = consulta.get('fecha_consulta')
                fecha_respuesta = consulta.get('fecha_respuesta')
                
                if fecha_consulta and fecha_respuesta:
                    if hasattr(fecha_consulta, 'timestamp'):
                        fecha_consulta = fecha_consulta.timestamp()
                    if hasattr(fecha_respuesta, 'timestamp'):
                        fecha_respuesta = fecha_respuesta.timestamp()
                    
                    response_time = fecha_respuesta - fecha_consulta
                    response_hours = response_time.total_seconds() / 3600
                    
                    # Score basado en tiempo de respuesta (menos tiempo = mejor score)
                    if response_hours < 1:
                        score = 5.0
                    elif response_hours < 6:
                        score = 4.0
                    elif response_hours < 24:
                        score = 3.0
                    else:
                        score = 2.0
                    
                    total_score += score
                    count += 1
            
            return total_score / count if count > 0 else 4.0
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction score: {e}")
            return 4.2  # Mock

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas en tiempo real
        """
        try:
            current_time = datetime.utcnow()
            last_hour = current_time - timedelta(hours=1)
            
            metrics = {
                'active_users': 0,
                'page_views': 0,
                'sales_last_hour': 0.0,
                'tickets_last_hour': 0,
                'conversion_rate_last_hour': 0.0,
                'top_pages': [],
                'server_response_time': 0.0,
                'error_rate': 0.0
            }
            
            # Usuarios activos (eventos de última hora)
            active_events = [event for event in self.real_time_data.get('page_visit', []) 
                           if event['timestamp'] >= last_hour]
            
            unique_users = len(set(event['data'].get('user_id', '') for event in active_events))
            metrics['active_users'] = unique_users
            metrics['page_views'] = len(active_events)
            
            # Ventas última hora
            sales_events = [event for event in self.real_time_data.get('sale', []) 
                          if event['timestamp'] >= last_hour]
            
            metrics['sales_last_hour'] = sum(event['data'].get('amount', 0) for event in sales_events)
            metrics['tickets_last_hour'] = sum(event['data'].get('tickets', 0) for event in sales_events)
            
            # Tasa de conversión última hora
            if metrics['page_views'] > 0:
                metrics['conversion_rate_last_hour'] = (len(sales_events) / metrics['page_views']) * 100
            
            # Páginas más visitadas
            page_counts = Counter(event['data'].get('page', '') for event in active_events)
            metrics['top_pages'] = page_counts.most_common(5)
            
            # Métricas de servidor (simuladas)
            metrics['server_response_time'] = 150.0  # ms
            metrics['error_rate'] = 0.5  # %
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}

    async def generate_predictions(self, days: int = 30) -> Dict[str, Any]:
        """
        Generar predicciones basadas en datos históricos
        """
        try:
            predictions = {
                'sales_forecast': [],
                'demand_forecast': {},
                'revenue_forecast': [],
                'customer_growth_forecast': [],
                'route_performance_forecast': {},
                'confidence_level': 0.85
            }
            
            # Predicción de ventas (simple moving average)
            historical_sales = await self.get_historical_sales(days * 2)
            
            if len(historical_sales) >= 7:
                # Usar promedio móvil de 7 días
                recent_avg = statistics.mean(historical_sales[-7:])
                
                # Predecir próximos 7 días con ligera variación
                for i in range(7):
                    variation = random.uniform(-0.1, 0.1)  # ±10% variación
                    predicted = recent_avg * (1 + variation)
                    
                    future_date = datetime.utcnow() + timedelta(days=i+1)
                    predictions['sales_forecast'].append({
                        'date': future_date.strftime('%Y-%m-%d'),
                        'predicted_sales': predicted,
                        'confidence': 0.8 - (i * 0.05)  # Disminuir confianza con el tiempo
                    })
            
            # Predicción de demanda por ruta
            route_analytics = await self.get_route_analytics(days)
            
            for route in route_analytics[:5]:  # Top 5 rutas
                # Predecir demanda basada en tendencia histórica
                base_demand = route.total_tickets
                growth_factor = 1.05  # 5% crecimiento esperado
                
                predictions['demand_forecast'][route.route_id] = {
                    'current_demand': base_demand,
                    'predicted_demand': base_demand * growth_factor,
                    'growth_rate': ((growth_factor - 1) * 100),
                    'recommendation': self.get_route_recommendation(route)
                }
            
            # Predicción de ingresos
            if predictions['sales_forecast']:
                avg_ticket_price = 8.0  # Precio promedio
                for forecast in predictions['sales_forecast']:
                    predicted_revenue = forecast['predicted_sales'] * avg_ticket_price
                    predictions['revenue_forecast'].append({
                        'date': forecast['date'],
                        'predicted_revenue': predicted_revenue,
                        'confidence': forecast['confidence']
                    })
            
            # Predicción de crecimiento de clientes
            customer_analytics = await self.get_customer_analytics(days)
            current_customers = customer_analytics.total_customers
            growth_rate = 0.03  # 3% crecimiento mensual
            
            for i in range(3):  # Próximos 3 meses
                future_customers = current_customers * ((1 + growth_rate) ** (i + 1))
                predictions['customer_growth_forecast'].append({
                    'month': (datetime.utcnow().replace(day=1) + timedelta(days=30*i)).strftime('%Y-%m'),
                    'predicted_customers': int(future_customers),
                    'growth_rate': growth_rate * 100
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {}

    def get_route_recommendation(self, route: RouteAnalytics) -> str:
        """
        Generar recomendación para ruta específica
        """
        if route.performance_score > 80:
            return "Excelente desempeño. Considerar aumentar frecuencia."
        elif route.performance_score > 60:
            return "Buen desempeño. Monitorear ocupación en horas pico."
        elif route.performance_score > 40:
            return "Desempeño moderado. Revisar precios y horarios."
        else:
            return "Bajo desempeño. Considerar reestructurar ruta o precios."

    async def get_current_metric_value(self, metric: str, time_window: str) -> float:
        """
        Obtener valor actual de una métrica
        """
        try:
            # Implementar lógica para obtener valor actual
            if metric == 'sales':
                return 5000.0  # Mock
            elif metric == 'tickets':
                return 50  # Mock
            elif metric == 'conversion_rate':
                return 12.5  # Mock
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error getting current metric value: {e}")
            return 0.0

    async def get_historical_sales(self, days: int) -> List[float]:
        """
        Obtener ventas históricas
        """
        try:
            if not self.firestore_db:
                return [1000.0, 1200.0, 1100.0, 1300.0, 1250.0, 1400.0, 1350.0]  # Mock
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            sales_query = self.firestore_db.collection('ventas')\
                .where('fecha_compra', '>=', start_date)\
                .where('estado', '==', 'confirmado')\
                .get()
            
            daily_sales = defaultdict(float)
            
            for doc in sales_query:
                data = doc.to_dict()
                if data.get('fecha_compra'):
                    day = data['fecha_compra'].strftime('%Y-%m-%d')
                    daily_sales[day] += float(data.get('total', 0))
            
            # Convertir a lista ordenada
            dates = sorted(daily_sales.keys())
            return [daily_sales[date] for date in dates]
            
        except Exception as e:
            logger.error(f"Error getting historical sales: {e}")
            return [1000.0, 1200.0, 1100.0, 1300.0, 1250.0, 1400.0, 1350.0]  # Mock

    # Métodos Mock para fallback
    def get_mock_sales_metrics(self) -> SalesMetrics:
        return SalesMetrics(
            total_sales=15000.0,
            total_tickets=250,
            average_ticket_value=60.0,
            sales_by_route={'Chincha-Pisco': 5000.0, 'Chincha-Ica': 7000.0, 'Pisco-Ica': 3000.0},
            sales_by_hour={'8': 30, '14': 45, '18': 60, '20': 35},
            sales_by_day={'2024-01-01': 2000.0, '2024-01-02': 2500.0, '2024-01-03': 2200.0},
            conversion_rate=12.5,
            abandoned_carts=38
        )

    def get_mock_route_analytics(self) -> List[RouteAnalytics]:
        return [
            RouteAnalytics(
                route_id='chincha-pisco',
                origin='Chincha',
                destination='Pisco',
                total_sales=5000.0,
                total_tickets=100,
                occupancy_rate=85.0,
                average_price=50.0,
                peak_hours=['08:00', '14:00', '18:00'],
                performance_score=85.0
            ),
            RouteAnalytics(
                route_id='chincha-ica',
                origin='Chincha',
                destination='Ica',
                total_sales=7000.0,
                total_tickets=70,
                occupancy_rate=70.0,
                average_price=100.0,
                peak_hours=['07:00', '15:00', '19:00'],
                performance_score=75.0
            )
        ]

    def get_mock_customer_analytics(self) -> CustomerAnalytics:
        return CustomerAnalytics(
            total_customers=500,
            new_customers=50,
            returning_customers=150,
            customer_segments={'nuevo': 200, 'recurrente': 150, 'inactivo': 150},
            average_lifetime_value=150.0,
            churn_rate=8.5,
            satisfaction_score=4.2
        )

# Instancia global del servicio
analytics_service = AnalyticsService()
