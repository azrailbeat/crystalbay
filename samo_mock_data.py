"""
Демонстрационные данные для SAMO API
Используются когда API недоступен из-за IP ограничений
"""

# Валюты - Казахстан (приоритет KZT)
CURRENCIES_DATA = {
    "SearchTour_CURRENCIES": [
        {"id": "1", "name": "Казахстанский тенге", "code": "KZT", "symbol": "₸", "default": True},
        {"id": "2", "name": "Доллар США", "code": "USD", "symbol": "$"},
        {"id": "3", "name": "Евро", "code": "EUR", "symbol": "€"},
        {"id": "4", "name": "Российский рубль", "code": "RUB", "symbol": "₽"},
        {"id": "5", "name": "Узбекский сум", "code": "UZS", "symbol": "сум"}
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

# Города отправления - Казахстан
TOWNFROMS_DATA = {
    "SearchTour_TOWNFROMS": [
        {"id": "1", "name": "Алматы", "code": "ALA", "airport": "ALA", "region": "Алматинская область"},
        {"id": "2", "name": "Астана (Нур-Султан)", "code": "NQZ", "airport": "NQZ", "region": "Акмолинская область"},
        {"id": "3", "name": "Шымкент", "code": "CIT", "airport": "CIT", "region": "Туркестанская область"},
        {"id": "4", "name": "Караганда", "code": "KGF", "airport": "KGF", "region": "Карагандинская область"},
        {"id": "5", "name": "Атырау", "code": "GUW", "airport": "GUW", "region": "Атырауская область"},
        {"id": "6", "name": "Актау", "code": "SCO", "airport": "SCO", "region": "Мангистауская область"},
        {"id": "7", "name": "Павлодар", "code": "PWQ", "airport": "PWQ", "region": "Павлодарская область"},
        {"id": "8", "name": "Семей", "code": "PLX", "airport": "PLX", "region": "Восточно-Казахстанская область"},
        {"id": "9", "name": "Усть-Каменогорск", "code": "UKK", "airport": "UKK", "region": "Восточно-Казахстанская область"},
        {"id": "10", "name": "Костанай", "code": "KSN", "airport": "KSN", "region": "Костанайская область"},
        {"id": "11", "name": "Актобе", "code": "AKX", "airport": "AKX", "region": "Актюбинская область"},
        {"id": "12", "name": "Тараз", "code": "DMB", "airport": "DMB", "region": "Жамбылская область"},
        {"id": "13", "name": "Уральск", "code": "URA", "airport": "URA", "region": "Западно-Казахстанская область"},
        {"id": "14", "name": "Петропавловск", "code": "PPK", "airport": "PPK", "region": "Северо-Казахстанская область"},
        {"id": "15", "name": "Кокшетау", "code": "KOV", "airport": "KOV", "region": "Акмолинская область"}
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
        'SearchTour_ALL': DEMO_TOURS,
        'GetOrders': DEMO_ORDERS
    }
    
    return data_map.get(action, {})

# Демо заявки для системы
DEMO_ORDERS = {
    "GetOrders": [
        {
            "id": "ORD-001",
            "order_number": "CB-2025-001",
            "customer_name": "Иван Петров",
            "customer_phone": "+7 777 123 4567",
            "customer_email": "ivan.petrov@email.kz",
            "tour_name": "Crystal Sunset Resort - Турция",
            "destination": "Турция",
            "hotel_name": "Crystal Sunset Resort",
            "check_in_date": "2025-09-15",
            "nights": 7,
            "adults": 2,
            "children": 0,
            "total_price": 450000,
            "currency": "KZT",
            "status": "new",
            "created_at": "2025-09-02T10:30:00Z",
            "updated_at": "2025-09-02T10:30:00Z",
            "notes": "Предпочитает номер с видом на море"
        },
        {
            "id": "ORD-002",
            "order_number": "CB-2025-002",
            "customer_name": "Айгуль Нурланова",
            "customer_phone": "+7 701 234 5678",
            "customer_email": "aigul.n@gmail.com",
            "tour_name": "Royal Paradise Hotel - Египет",
            "destination": "Египет",
            "hotel_name": "Royal Paradise Hotel",
            "check_in_date": "2025-09-20",
            "nights": 10,
            "adults": 2,
            "children": 1,
            "total_price": 380000,
            "currency": "KZT",
            "status": "processing",
            "created_at": "2025-09-01T14:15:00Z",
            "updated_at": "2025-09-02T09:00:00Z",
            "notes": "Семейный отдых с ребенком 8 лет"
        },
        {
            "id": "ORD-003",
            "order_number": "CB-2025-003",
            "customer_name": "Дмитрий Казанцев",
            "customer_phone": "+7 702 345 6789",
            "customer_email": "d.kazantsev@mail.ru",
            "tour_name": "Emirates Palace Resort - ОАЭ",
            "destination": "ОАЭ",
            "hotel_name": "Emirates Palace Resort",
            "check_in_date": "2025-10-01",
            "nights": 5,
            "adults": 2,
            "children": 0,
            "total_price": 720000,
            "currency": "KZT",
            "status": "confirmed",
            "created_at": "2025-08-30T16:45:00Z",
            "updated_at": "2025-09-01T11:30:00Z",
            "notes": "VIP отдых, требуется трансфер класса люкс"
        },
        {
            "id": "ORD-004",
            "order_number": "CB-2025-004",
            "customer_name": "Марина Сидорова",
            "customer_phone": "+7 705 456 7890",
            "customer_email": "marina.sidorova@yahoo.com",
            "tour_name": "Tropical Island Resort - Мальдивы",
            "destination": "Мальдивы",
            "hotel_name": "Tropical Island Resort",
            "check_in_date": "2025-10-10",
            "nights": 7,
            "adults": 2,
            "children": 0,
            "total_price": 1200000,
            "currency": "KZT",
            "status": "paid",
            "created_at": "2025-08-25T12:00:00Z",
            "updated_at": "2025-08-28T10:15:00Z",
            "notes": "Медовый месяц, бунгало над водой"
        },
        {
            "id": "ORD-005",
            "order_number": "CB-2025-005",
            "customer_name": "Алексей Иванов",
            "customer_phone": "+7 707 567 8901",
            "customer_email": "a.ivanov@gmail.com",
            "tour_name": "Thai Beach Hotel - Таиланд",
            "destination": "Таиланд",
            "hotel_name": "Thai Beach Hotel",
            "check_in_date": "2025-09-25",
            "nights": 9,
            "adults": 2,
            "children": 2,
            "total_price": 520000,
            "currency": "KZT",
            "status": "cancelled",
            "created_at": "2025-08-20T09:30:00Z",
            "updated_at": "2025-08-22T14:00:00Z",
            "notes": "Отменено по просьбе клиента - изменились планы"
        }
    ]
}

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