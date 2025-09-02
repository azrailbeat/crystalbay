"""
Демонстрационные данные для SAMO API
Используются когда API недоступен из-за IP ограничений
"""

# Валюты
CURRENCIES_DATA = {
    "SearchTour_CURRENCIES": [
        {"id": "1", "name": "KZT", "code": "KZT", "symbol": "₸"},
        {"id": "2", "name": "USD", "code": "USD", "symbol": "$"},
        {"id": "3", "name": "EUR", "code": "EUR", "symbol": "€"},
        {"id": "4", "name": "RUB", "code": "RUB", "symbol": "₽"},
        {"id": "5", "name": "UZS", "code": "UZS", "symbol": "сум"}
    ]
}

# Страны и направления
STATES_DATA = {
    "SearchTour_STATES": [
        {"id": "1", "name": "Турция", "code": "TR"},
        {"id": "2", "name": "Египет", "code": "EG"},
        {"id": "3", "name": "ОАЭ", "code": "AE"},
        {"id": "4", "name": "Мальдивы", "code": "MV"},
        {"id": "5", "name": "Таиланд", "code": "TH"},
        {"id": "6", "name": "Грузия", "code": "GE"},
        {"id": "7", "name": "Узбекистан", "code": "UZ"},
        {"id": "8", "name": "Киргизия", "code": "KG"},
        {"id": "9", "name": "Шри-Ланка", "code": "LK"},
        {"id": "10", "name": "Индия", "code": "IN"}
    ]
}

# Города отправления
TOWNFROMS_DATA = {
    "SearchTour_TOWNFROMS": [
        {"id": "1", "name": "Алматы", "code": "ALA"},
        {"id": "2", "name": "Нур-Султан", "code": "NQZ"},
        {"id": "3", "name": "Шымкент", "code": "CIT"},
        {"id": "4", "name": "Караганда", "code": "KGF"},
        {"id": "5", "name": "Атырау", "code": "GUW"},
        {"id": "6", "name": "Актау", "code": "SCO"},
        {"id": "7", "name": "Павлодар", "code": "PWQ"},
        {"id": "8", "name": "Семей", "code": "PLX"},
        {"id": "9", "name": "Усть-Каменогорск", "code": "UKK"},
        {"id": "10", "name": "Костанай", "code": "KSN"}
    ]
}

# Звезды отелей
STARS_DATA = {
    "SearchTour_STARS": [
        {"id": "3", "name": "3 звезды"},
        {"id": "4", "name": "4 звезды"},
        {"id": "5", "name": "5 звезд"},
        {"id": "0", "name": "Без категории"}
    ]
}

# Типы питания
MEALS_DATA = {
    "SearchTour_MEALS": [
        {"id": "1", "name": "BB", "description": "Завтрак"},
        {"id": "2", "name": "HB", "description": "Полупансион"},
        {"id": "3", "name": "FB", "description": "Полный пансион"},
        {"id": "4", "name": "AI", "description": "Все включено"},
        {"id": "5", "name": "UAI", "description": "Ультра все включено"},
        {"id": "6", "name": "RO", "description": "Без питания"}
    ]
}

# Количество ночей
NIGHTS_DATA = {
    "NIGHTS": [
        {"nights": "3", "name": "3 ночи"},
        {"nights": "4", "name": "4 ночи"},
        {"nights": "5", "name": "5 ночей"},
        {"nights": "6", "name": "6 ночей"},
        {"nights": "7", "name": "7 ночей"},
        {"nights": "8", "name": "8 ночей"},
        {"nights": "9", "name": "9 ночей"},
        {"nights": "10", "name": "10 ночей"},
        {"nights": "11", "name": "11 ночей"},
        {"nights": "12", "name": "12 ночей"},
        {"nights": "13", "name": "13 ночей"},
        {"nights": "14", "name": "14 ночей"}
    ]
}

# Отели для демонстрации
HOTELS_DATA = {
    "SearchTour_HOTELS": [
        {
            "id": "1001", 
            "name": "Crystal Sunset Resort", 
            "state_id": "1", 
            "stars": "5",
            "location": "Анталия, Турция"
        },
        {
            "id": "1002", 
            "name": "Royal Paradise Hotel", 
            "state_id": "2", 
            "stars": "4",
            "location": "Хургада, Египет"
        },
        {
            "id": "1003", 
            "name": "Emirates Palace Resort", 
            "state_id": "3", 
            "stars": "5",
            "location": "Дубай, ОАЭ"
        },
        {
            "id": "1004", 
            "name": "Tropical Island Resort", 
            "state_id": "4", 
            "stars": "5",
            "location": "Мале, Мальдивы"
        },
        {
            "id": "1005", 
            "name": "Thai Beach Hotel", 
            "state_id": "5", 
            "stars": "4",
            "location": "Пхукет, Таиланд"
        }
    ]
}

# Демо туры для поиска
DEMO_TOURS = {
    "SearchTour_ALL": [
        {
            "id": "T001",
            "hotel_name": "Crystal Sunset Resort",
            "state_name": "Турция",
            "city": "Анталия",
            "stars": 5,
            "nights": 7,
            "adults": 2,
            "children": 0,
            "meal": "AI",
            "meal_name": "Все включено",
            "price": 450000,
            "currency": "KZT",
            "date_from": "2025-09-15",
            "date_to": "2025-09-22"
        },
        {
            "id": "T002",
            "hotel_name": "Royal Paradise Hotel",
            "state_name": "Египет",
            "city": "Хургада",
            "stars": 4,
            "nights": 10,
            "adults": 2,
            "children": 1,
            "meal": "AI",
            "meal_name": "Все включено",
            "price": 380000,
            "currency": "KZT",
            "date_from": "2025-09-20",
            "date_to": "2025-09-30"
        },
        {
            "id": "T003",
            "hotel_name": "Emirates Palace Resort",
            "state_name": "ОАЭ",
            "city": "Дубай",
            "stars": 5,
            "nights": 5,
            "adults": 2,
            "children": 0,
            "meal": "BB",
            "meal_name": "Завтрак",
            "price": 720000,
            "currency": "KZT",
            "date_from": "2025-10-01",
            "date_to": "2025-10-06"
        },
        {
            "id": "T004",
            "hotel_name": "Tropical Island Resort",
            "state_name": "Мальдивы",
            "city": "Мале",
            "stars": 5,
            "nights": 7,
            "adults": 2,
            "children": 0,
            "meal": "FB",
            "meal_name": "Полный пансион",
            "price": 1200000,
            "currency": "KZT",
            "date_from": "2025-10-10",
            "date_to": "2025-10-17"
        },
        {
            "id": "T005",
            "hotel_name": "Thai Beach Hotel",
            "state_name": "Таиланд",
            "city": "Пхукет",
            "stars": 4,
            "nights": 9,
            "adults": 2,
            "children": 2,
            "meal": "HB",
            "meal_name": "Полупансион",
            "price": 520000,
            "currency": "KZT",
            "date_from": "2025-09-25",
            "date_to": "2025-10-04"
        }
    ]
}

def get_mock_data(action: str) -> dict:
    """Получить демонстрационные данные для API команды"""
    
    data_map = {
        'SearchTour_CURRENCIES': CURRENCIES_DATA,
        'SearchTour_STATES': STATES_DATA,
        'SearchTour_TOWNFROMS': TOWNFROMS_DATA,
        'SearchTour_STARS': STARS_DATA,
        'SearchTour_MEALS': MEALS_DATA,
        'NIGHTS': NIGHTS_DATA,
        'SearchTour_HOTELS': HOTELS_DATA,
        'SearchTour_ALL': DEMO_TOURS
    }
    
    return data_map.get(action, {})

def create_mock_response(action: str, success: bool = True) -> dict:
    """Создать mock ответ в формате SAMO API"""
    
    if not success:
        return {
            'success': False,
            'error': 'Demo mode - SAMO API недоступен (IP заблокирован)',
            'demo_mode': True
        }
    
    mock_data = get_mock_data(action)
    
    return {
        'success': True,
        'data': mock_data,
        'demo_mode': True,
        'execution_time': 0.1
    }