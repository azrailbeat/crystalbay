"""
AI Insights Service для Crystal Bay Travel
ИИ-анализ метрик дашборда с использованием OpenAI GPT-4
"""

import os
import logging
import json
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIInsightsService:
    """Сервис для генерации ИИ-инсайтов на основе метрик"""
    
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            # Пытаемся получить из настроек
            try:
                from settings_service import settings_service
                api_key = settings_service.get('openai_api_key')
            except:
                pass
        
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = "gpt-4o"
    
    def analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ метрик с помощью ИИ"""
        if not self.client:
            return {
                'summary': 'ИИ-анализ недоступен. Настройте OpenAI API ключ в настройках.',
                'insights': [],
                'recommendations': [],
                'predictions': {}
            }
        
        try:
            # Формируем prompt для анализа
            prompt = self._build_analysis_prompt(metrics)
            
            # Запрос к OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты опытный бизнес-аналитик в сфере туризма. 
                        Анализируй метрики туроператора и предоставляй конкретные инсайты и рекомендации.
                        Отвечай на русском языке. Будь конкретным и практичным."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Парсим ответ
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                'summary': analysis.get('summary', ''),
                'insights': analysis.get('insights', []),
                'recommendations': analysis.get('recommendations', []),
                'predictions': analysis.get('predictions', {}),
                'alerts': self._generate_alerts(metrics)
            }
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                'summary': f'Ошибка ИИ-анализа: {str(e)}',
                'insights': [],
                'recommendations': [],
                'predictions': {},
                'alerts': []
            }
    
    def _build_analysis_prompt(self, metrics: Dict[str, Any]) -> str:
        """Построение prompt для анализа"""
        financial = metrics.get('financial', {})
        operational = metrics.get('operational', {})
        customer = metrics.get('customer', {})
        
        prompt = f"""
Проанализируй метрики туроператора Crystal Bay Travel за период {metrics.get('period', '30d')}:

**ФИНАНСОВЫЕ ПОКАЗАТЕЛИ:**
- Общая выручка: {financial.get('total_revenue', 0):,.2f} {financial.get('currency', 'KZT')}
- Средний чек: {financial.get('avg_booking_value', 0):,.2f} {financial.get('currency', 'KZT')}
- Рост выручки: {financial.get('revenue_growth', 0):.1f}%
- Маржа прибыли: {financial.get('profit_margin', 0):.1f}%
- Прогнозируемая прибыль: {financial.get('estimated_profit', 0):,.2f} {financial.get('currency', 'KZT')}

**ОПЕРАЦИОННЫЕ ПОКАЗАТЕЛИ:**
- Всего бронирований: {operational.get('total_bookings', 0)}
- Подтвержденных: {operational.get('confirmed_bookings', 0)}
- Конверсия: {operational.get('conversion_rate', 0):.1f}%
- Отмены: {operational.get('cancellation_rate', 0):.1f}%
- Средняя заполняемость тура: {operational.get('avg_occupancy', 0):.1f} человек
- Средний lead time: {operational.get('avg_lead_time', 0)} дней

**КЛИЕНТСКИЕ ПОКАЗАТЕЛИ:**
- Новых клиентов: {customer.get('new_clients', 0)}
- Повторных клиентов: {customer.get('repeat_clients', 0)}
- Процент повторных покупок: {customer.get('repeat_rate', 0):.1f}%
- Customer Lifetime Value: {customer.get('customer_lifetime_value', 0):,.2f} {financial.get('currency', 'KZT')}
- Customer Acquisition Cost: {customer.get('customer_acquisition_cost', 0):,.2f} {financial.get('currency', 'KZT')}
- NPS Score: {customer.get('nps_score', 0)}

Предоставь ответ в формате JSON со следующей структурой:
{{
    "summary": "Краткий общий анализ ситуации (2-3 предложения)",
    "insights": [
        "Ключевой инсайт 1",
        "Ключевой инсайт 2",
        "Ключевой инсайт 3"
    ],
    "recommendations": [
        "Конкретная рекомендация 1",
        "Конкретная рекомендация 2",
        "Конкретная рекомендация 3"
    ],
    "predictions": {{
        "revenue_forecast": "Прогноз выручки на следующий период",
        "growth_potential": "Оценка потенциала роста",
        "risk_areas": "Зоны риска"
    }}
}}
"""
        return prompt
    
    def _generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Генерация автоматических алертов на основе пороговых значений"""
        alerts = []
        
        financial = metrics.get('financial', {})
        operational = metrics.get('operational', {})
        customer = metrics.get('customer', {})
        
        # Проверка конверсии
        conversion = operational.get('conversion_rate', 0)
        if conversion < 50:
            alerts.append({
                'type': 'warning',
                'metric': 'Конверсия',
                'message': f'Низкая конверсия ({conversion:.1f}%). Рекомендуется оптимизация воронки продаж.'
            })
        
        # Проверка отмен
        cancellation = operational.get('cancellation_rate', 0)
        if cancellation > 20:
            alerts.append({
                'type': 'danger',
                'metric': 'Отмены',
                'message': f'Высокий процент отмен ({cancellation:.1f}%). Требуется анализ причин.'
            })
        
        # Проверка роста выручки
        growth = financial.get('revenue_growth', 0)
        if growth < 0:
            alerts.append({
                'type': 'danger',
                'metric': 'Рост выручки',
                'message': f'Отрицательный рост выручки ({growth:.1f}%). Необходимы срочные меры.'
            })
        elif growth > 20:
            alerts.append({
                'type': 'success',
                'metric': 'Рост выручки',
                'message': f'Отличный рост выручки ({growth:.1f}%)! Продолжайте в том же духе.'
            })
        
        # Проверка CAC vs CLV
        cac = customer.get('customer_acquisition_cost', 0)
        clv = customer.get('customer_lifetime_value', 0)
        if cac > 0 and clv / cac < 3:
            alerts.append({
                'type': 'warning',
                'metric': 'CAC/CLV',
                'message': f'Соотношение CAC/CLV ниже оптимального. Увеличьте ценность клиента или снизьте стоимость привлечения.'
            })
        
        # Проверка повторных клиентов
        repeat_rate = customer.get('repeat_rate', 0)
        if repeat_rate < 25:
            alerts.append({
                'type': 'warning',
                'metric': 'Повторные клиенты',
                'message': f'Низкий процент повторных покупок ({repeat_rate:.1f}%). Внедрите программу лояльности.'
            })
        
        return alerts
    
    def get_demand_forecast(self, trend_data: Dict[str, List]) -> Dict[str, Any]:
        """Прогнозирование спроса на основе исторических данных"""
        if not self.client:
            return {'forecast': [], 'confidence': 0}
        
        try:
            # Используем OpenAI для прогнозирования
            prompt = f"""
На основе исторических данных бронирований:
Дни: {trend_data.get('days', [])}
Бронирования: {trend_data.get('bookings', [])}

Создай прогноз бронирований на следующие 7 дней. 
Ответь в формате JSON: {{"forecast": [число_бронирований_день1, ...], "confidence": процент_уверенности}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты специалист по прогнозированию спроса в туризме."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            forecast = json.loads(response.choices[0].message.content)
            return forecast
            
        except Exception as e:
            logger.error(f"Demand forecast error: {e}")
            return {'forecast': [], 'confidence': 0}
