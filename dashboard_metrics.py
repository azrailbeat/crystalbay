"""
Dashboard Metrics Service для Crystal Bay Travel
Расчет ключевых показателей эффективности (KPI) для туроператора
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import func
from models import Order, Client

logger = logging.getLogger(__name__)

class DashboardMetricsService:
    """Сервис для расчета метрик дашборда туроператора"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_all_metrics(self, period: str = '30d') -> Dict[str, Any]:
        """Получить все ключевые метрики дашборда"""
        try:
            # Определяем период
            start_date = self._get_period_start(period)
            
            metrics = {
                'financial': self._get_financial_metrics(start_date),
                'operational': self._get_operational_metrics(start_date),
                'customer': self._get_customer_metrics(start_date),
                'trends': self._get_trend_data(start_date),
                'period': period,
                'last_updated': datetime.now().isoformat()
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating dashboard metrics: {e}")
            return self._get_empty_metrics()
    
    def _get_financial_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Финансовые метрики"""
        try:
            # Получаем заказы за период
            orders = self.db.query(Order).filter(
                Order.created_at >= start_date,
                Order.status != 'cancelled'
            ).all()
            
            # Расчет метрик
            total_revenue = sum(order.total_amount or 0 for order in orders)
            booking_count = len(orders)
            avg_booking_value = total_revenue / booking_count if booking_count > 0 else 0
            
            # Рост выручки (сравнение с предыдущим периодом)
            prev_period_start = start_date - (datetime.now() - start_date)
            prev_orders = self.db.query(Order).filter(
                Order.created_at >= prev_period_start,
                Order.created_at < start_date,
                Order.status != 'cancelled'
            ).all()
            prev_revenue = sum(order.total_amount or 0 for order in prev_orders)
            revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            
            # Прибыльность (упрощенный расчет - 15% маржа)
            profit_margin = 15.0  # Можно сделать динамическим
            estimated_profit = total_revenue * (profit_margin / 100)
            
            return {
                'total_revenue': round(total_revenue, 2),
                'avg_booking_value': round(avg_booking_value, 2),
                'revenue_growth': round(revenue_growth, 2),
                'profit_margin': profit_margin,
                'estimated_profit': round(estimated_profit, 2),
                'currency': 'KZT'
            }
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {e}")
            return {
                'total_revenue': 0,
                'avg_booking_value': 0,
                'revenue_growth': 0,
                'profit_margin': 0,
                'estimated_profit': 0,
                'currency': 'KZT'
            }
    
    def _get_operational_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Операционные метрики"""
        try:
            # Всего бронирований
            total_bookings = self.db.query(Order).filter(
                Order.created_at >= start_date
            ).count()
            
            # Подтвержденные бронирования
            confirmed_bookings = self.db.query(Order).filter(
                Order.created_at >= start_date,
                Order.status.in_(['confirmed', 'paid'])
            ).count()
            
            # Отмененные бронирования
            cancelled_bookings = self.db.query(Order).filter(
                Order.created_at >= start_date,
                Order.status == 'cancelled'
            ).count()
            
            # Конверсия (подтвержденные / всего)
            conversion_rate = (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0
            
            # Отмены (%)
            cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
            
            # Заполняемость (среднее количество человек на тур)
            avg_occupancy = self.db.query(func.avg(Order.adults + Order.children)).filter(
                Order.created_at >= start_date,
                Order.status != 'cancelled'
            ).scalar() or 0
            
            # Средний lead time (дней до поездки)
            orders_with_dates = self.db.query(Order).filter(
                Order.created_at >= start_date,
                Order.check_in.isnot(None),
                Order.status != 'cancelled'
            ).all()
            
            if orders_with_dates:
                lead_times = [(order.check_in - order.created_at).days for order in orders_with_dates]
                avg_lead_time = sum(lead_times) / len(lead_times)
            else:
                avg_lead_time = 0
            
            return {
                'total_bookings': total_bookings,
                'confirmed_bookings': confirmed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'conversion_rate': round(conversion_rate, 2),
                'cancellation_rate': round(cancellation_rate, 2),
                'avg_occupancy': round(avg_occupancy, 1),
                'avg_lead_time': round(avg_lead_time, 0)
            }
        except Exception as e:
            logger.error(f"Error calculating operational metrics: {e}")
            return {
                'total_bookings': 0,
                'confirmed_bookings': 0,
                'cancelled_bookings': 0,
                'conversion_rate': 0,
                'cancellation_rate': 0,
                'avg_occupancy': 0,
                'avg_lead_time': 0
            }
    
    def _get_customer_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Клиентские метрики"""
        try:
            # Новые клиенты
            new_clients = self.db.query(Client).filter(
                Client.created_at >= start_date
            ).count()
            
            # Повторные клиенты
            repeat_clients = self.db.query(Client).filter(
                Client.created_at < start_date
            ).join(Order).filter(
                Order.created_at >= start_date
            ).distinct().count()
            
            # Всего активных клиентов за период
            total_active_clients = new_clients + repeat_clients
            
            # Процент повторных клиентов
            repeat_rate = (repeat_clients / total_active_clients * 100) if total_active_clients > 0 else 0
            
            # Customer Lifetime Value (упрощенный расчет)
            avg_order_value = self.db.query(func.avg(Order.total_amount)).filter(
                Order.status != 'cancelled'
            ).scalar() or 0
            
            avg_orders_per_client = self.db.query(
                func.count(Order.id)
            ).join(Client).group_by(Client.id).all()
            
            avg_frequency = sum([count for count, in avg_orders_per_client]) / len(avg_orders_per_client) if avg_orders_per_client else 1
            customer_lifetime_value = avg_order_value * avg_frequency * 3  # 3 года средний срок жизни клиента
            
            # Customer Acquisition Cost (упрощенный - 10% от выручки на маркетинг)
            total_revenue = self.db.query(func.sum(Order.total_amount)).filter(
                Order.created_at >= start_date,
                Order.status != 'cancelled'
            ).scalar() or 0
            
            marketing_spend = total_revenue * 0.10  # 10% на маркетинг
            cac = marketing_spend / new_clients if new_clients > 0 else 0
            
            # NPS (упрощенный - можно заменить на реальные отзывы)
            nps_score = 42  # Placeholder - нужна интеграция с системой отзывов
            
            return {
                'new_clients': new_clients,
                'repeat_clients': repeat_clients,
                'total_active': total_active_clients,
                'repeat_rate': round(repeat_rate, 2),
                'customer_lifetime_value': round(customer_lifetime_value, 2),
                'customer_acquisition_cost': round(cac, 2),
                'nps_score': nps_score
            }
        except Exception as e:
            logger.error(f"Error calculating customer metrics: {e}")
            return {
                'new_clients': 0,
                'repeat_clients': 0,
                'total_active': 0,
                'repeat_rate': 0,
                'customer_lifetime_value': 0,
                'customer_acquisition_cost': 0,
                'nps_score': 0
            }
    
    def _get_trend_data(self, start_date: datetime) -> Dict[str, List]:
        """Данные для графиков трендов"""
        try:
            # Получаем данные по дням для графиков
            days = []
            revenue_trend = []
            bookings_trend = []
            
            current_date = start_date
            while current_date <= datetime.now():
                next_date = current_date + timedelta(days=1)
                
                # Выручка за день
                daily_revenue = self.db.query(func.sum(Order.total_amount)).filter(
                    Order.created_at >= current_date,
                    Order.created_at < next_date,
                    Order.status != 'cancelled'
                ).scalar() or 0
                
                # Бронирования за день
                daily_bookings = self.db.query(Order).filter(
                    Order.created_at >= current_date,
                    Order.created_at < next_date
                ).count()
                
                days.append(current_date.strftime('%Y-%m-%d'))
                revenue_trend.append(round(daily_revenue, 2))
                bookings_trend.append(daily_bookings)
                
                current_date = next_date
            
            return {
                'days': days,
                'revenue': revenue_trend,
                'bookings': bookings_trend
            }
        except Exception as e:
            logger.error(f"Error calculating trend data: {e}")
            return {
                'days': [],
                'revenue': [],
                'bookings': []
            }
    
    def _get_period_start(self, period: str) -> datetime:
        """Получить начальную дату периода"""
        now = datetime.now()
        
        if period == '7d':
            return now - timedelta(days=7)
        elif period == '30d':
            return now - timedelta(days=30)
        elif period == '90d':
            return now - timedelta(days=90)
        elif period == 'ytd':
            return datetime(now.year, 1, 1)
        else:
            return now - timedelta(days=30)  # По умолчанию 30 дней
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Пустые метрики при ошибке"""
        return {
            'financial': {
                'total_revenue': 0,
                'avg_booking_value': 0,
                'revenue_growth': 0,
                'profit_margin': 0,
                'estimated_profit': 0,
                'currency': 'KZT'
            },
            'operational': {
                'total_bookings': 0,
                'confirmed_bookings': 0,
                'cancelled_bookings': 0,
                'conversion_rate': 0,
                'cancellation_rate': 0,
                'avg_occupancy': 0,
                'avg_lead_time': 0
            },
            'customer': {
                'new_clients': 0,
                'repeat_clients': 0,
                'total_active': 0,
                'repeat_rate': 0,
                'customer_lifetime_value': 0,
                'customer_acquisition_cost': 0,
                'nps_score': 0
            },
            'trends': {
                'days': [],
                'revenue': [],
                'bookings': []
            },
            'period': '30d',
            'last_updated': datetime.now().isoformat()
        }
