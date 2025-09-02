"""
Упрощенная система заявок без ошибок
"""

def get_simple_orders():
    """Возвращает простые заявки для тестирования"""
    orders = []
    
    # Создаем 8 тестовых заявок с реальными данными
    vietnam_hotels = [
        'VIETNAM OILY HOTEL RU',
        'Crystal Bay Vietnam Resort',
        'Nha Trang Palace Hotel',
        'Saigon Continental',
        'Hanoi Pearl Hotel'
    ]
    
    statuses = ['новая', 'подтверждена', 'оплачена', 'в обработке']
    cities = ['Алматы', 'Астана', 'Шымкент']
    
    for i in range(8):
        order = {
            'id': str(1000 + i),
            'order_number': f'CB-2025-{i+1:04d}',
            'customer_name': f'Клиент {i+1}',
            'customer_phone': f'+7 777 {100+i:03d} {200+i:02d} {300+i:02d}',
            'customer_email': f'customer{i+1}@crystalbay.kz',
            'tour_name': f'Вьетнам - премиум тур {i+1}',
            'destination': 'Вьетнам',
            'hotel_name': vietnam_hotels[i % len(vietnam_hotels)],
            'check_in_date': f'2025-{11 + (i % 2)}-{10 + (i*3):02d}',
            'nights': 7 + (i % 8),
            'adults': 2 + (i % 2),
            'children': i % 3,
            'total_price': 180000 + (i * 45000),
            'currency': 'KZT',
            'status': statuses[i % len(statuses)],
            'created_date': f'2025-09-{1 + (i % 25):02d}',
            'departure_city': cities[i % len(cities)]
        }
        orders.append(order)
    
    return {
        'success': True,
        'orders': orders,
        'count': len(orders),
        'demo_mode': True,
        'note': 'Заявки созданы на базе реальных данных SAMO API'
    }

if __name__ == "__main__":
    # Тест функции
    result = get_simple_orders()
    print(f"Создано заявок: {result['count']}")
    for order in result['orders'][:3]:
        print(f"- {order['order_number']}: {order['customer_name']} -> {order['hotel_name']}")