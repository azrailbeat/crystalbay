"""
Демо-данные туров для тестирования интерфейса универсального поиска
Используются только для development сервера когда SAMO API недоступен
"""

def get_demo_tours_data():
    """Возвращает демо-туры для тестирования интерфейса"""
    return [
        {
            'id': 1,
            'hotel_name': 'ALMATY - PHU QUOC (VJ+SCAT)',
            'destination': 'Вьетнам',
            'stars': 4,
            'nights': 7,
            'meal': 'Завтрак',
            'adults': 2,
            'price': 289000,
            'currency': 'KZT',
            'description': 'Тур на остров Фукуок с вылетом из Алматы'
        },
        {
            'id': 2,
            'hotel_name': 'ALMATY - PHU QUOC (VJ+SCAT) EARLY BOOKING',
            'destination': 'Вьетнам', 
            'stars': 4,
            'nights': 7,
            'meal': 'Завтрак',
            'adults': 2,
            'price': 269000,
            'currency': 'KZT',
            'description': 'Раннее бронирование со скидкой'
        },
        {
            'id': 3,
            'hotel_name': 'C-LUXE АЛМАТЫ - Дананг а/к VIETJET AIRLINES',
            'destination': 'Вьетнам',
            'stars': 5,
            'nights': 7,
            'meal': 'Завтрак',
            'adults': 2,
            'price': 320000,
            'currency': 'KZT',
            'description': 'Люкс тур в Дананг с VietJet'
        },
        {
            'id': 4,
            'hotel_name': 'Анталья - Турция (Pegas)',
            'destination': 'Турция',
            'stars': 4,
            'nights': 7,
            'meal': 'Всё включено',
            'adults': 2,
            'price': 180000,
            'currency': 'KZT',
            'description': 'Классический тур в Анталью'
        },
        {
            'id': 5,
            'hotel_name': 'Хургада - Red Sea (Join Up)',
            'destination': 'Египет',
            'stars': 5,
            'nights': 7,
            'meal': 'Всё включено',
            'adults': 2,
            'price': 150000,
            'currency': 'KZT',
            'description': 'Отдых на Красном море'
        },
        {
            'id': 6,
            'hotel_name': 'Пхукет - Таиланд (Asia Travel)',
            'destination': 'Таиланд',
            'stars': 4,
            'nights': 10,
            'meal': 'Завтрак',
            'adults': 2,
            'price': 220000,
            'currency': 'KZT',
            'description': 'Экзотический отдых в Таиланде'
        }
    ]

def filter_demo_tours(tours, departure_city=None, destination=None, max_price=None):
    """Фильтрует демо-туры по параметрам"""
    filtered = tours
    
    # Фильтр по направлению (примерная логика)
    if destination:
        destination_map = {
            '15': 'Вьетнам',
            '1': 'Турция', 
            '2': 'Египет',
            '6': 'Таиланд'
        }
        target_destination = destination_map.get(str(destination))
        if target_destination:
            filtered = [t for t in filtered if t['destination'] == target_destination]
    
    # Фильтр по цене
    if max_price:
        filtered = [t for t in filtered if t['price'] <= max_price]
    
    return filtered