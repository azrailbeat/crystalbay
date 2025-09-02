"""
Настройки для работы с реальным SAMO API
Только актуальные данные для маршрутов Алматы/Астана → Вьетнам
"""

# Приоритетные города отправления (Казахстан)
PRIORITY_DEPARTURE_CITIES = [
    {"id": "1", "name": "Алматы", "code": "ALA", "airport": "ALA"},
    {"id": "2", "name": "Астана (Нур-Султан)", "code": "NQZ", "airport": "NQZ"}
]

# Приоритетные направления
PRIORITY_DESTINATIONS = [
    {"id": "1", "name": "Вьетнам", "code": "VN", "priority": True}
]

# Валюта по умолчанию
DEFAULT_CURRENCY = "KZT"

# Системные настройки для SAMO API
API_SETTINGS = {
    "timeout": 30,
    "retry_attempts": 3,
    "demo_mode": False,  # Отключаем демо режим
    "use_fallback": False,  # Отключаем fallback данные
    "validate_responses": True,
    "log_all_requests": True
}

def validate_samo_connection():
    """Валидация подключения к SAMO API"""
    import os
    
    oauth_token = os.environ.get('SAMO_OAUTH_TOKEN')
    if not oauth_token:
        return False, "SAMO_OAUTH_TOKEN не найден в переменных окружения"
    
    if oauth_token == "your_samo_oauth_token_here":
        return False, "SAMO_OAUTH_TOKEN не настроен (placeholder значение)"
    
    return True, "Токен настроен корректно"

def get_search_params_vietnam(departure_city="ALA", adults=2, children=0, nights=7):
    """Базовые параметры поиска для Вьетнама"""
    from datetime import datetime, timedelta
    
    # Даты на следующий месяц
    start_date = datetime.now() + timedelta(days=30)
    
    return {
        "departure_city": departure_city,
        "destination": "VN",  # Вьетнам
        "date_from": start_date.strftime("%Y-%m-%d"),
        "nights": str(nights),
        "adults": str(adults),
        "children": str(children),
        "currency": DEFAULT_CURRENCY
    }