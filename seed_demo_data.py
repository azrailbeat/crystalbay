"""
Скрипт для генерации демонстрационных данных
Crystal Bay Travel - Demo Data Generator
"""

import os
import sys
from datetime import datetime, timedelta
import random

os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL'))
os.environ.setdefault('SESSION_SECRET', os.environ.get('SESSION_SECRET', 'demo-secret-key-12345'))

# Import app and models - порядок важен!
from app import app, db
# Импортируем все модели чтобы они были зарегистрированы в Base.metadata
from models import Base, Client, Order, OrderLog, Message, SamoCache, ApiLog, Settings

DEMO_CLIENTS = [
    {"name": "Айгерим Нурланова", "phone": "+77051234567", "email": "aigerim.n@mail.kz"},
    {"name": "Ержан Касымов", "phone": "+77052345678", "email": "yerzhan.k@gmail.com"},
    {"name": "Дина Сагадиева", "phone": "+77053456789", "email": "dina.s@inbox.kz"},
    {"name": "Асель Токтарова", "phone": "+77054567890", "email": "asel.t@yandex.kz"},
    {"name": "Мурат Абдуллаев", "phone": "+77055678901", "email": "murat.a@mail.ru"},
    {"name": "Жанна Искакова", "phone": "+77056789012", "email": "zhanna.i@gmail.com"},
    {"name": "Дархан Смагулов", "phone": "+77057890123", "email": "darkhan.s@inbox.kz"},
    {"name": "Сауле Жумабаева", "phone": "+77058901234", "email": "saule.zh@mail.kz"},
    {"name": "Нурлан Садыков", "phone": "+77059012345", "email": "nurlan.s@gmail.com"},
    {"name": "Гульнара Есенова", "phone": "+77050123456", "email": "gulnara.e@yandex.kz"},
]

DEMO_DESTINATIONS = [
    "Нячанг, Вьетнам",
    "Фантьет, Вьетнам", 
    "Фукуок, Вьетнам",
    "Ханой, Вьетнам",
    "Хошимин, Вьетнам",
    "Далат, Вьетнам",
]

DEMO_HOTELS = [
    {"name": "Vinpearl Resort & Spa", "stars": 5},
    {"name": "InterContinental Nha Trang", "stars": 5},
    {"name": "Sheraton Nha Trang", "stars": 5},
    {"name": "Novotel Phu Quoc Resort", "stars": 4},
    {"name": "Melia Ho Tram Beach Resort", "stars": 5},
    {"name": "Muong Thanh Luxury Nha Trang", "stars": 4},
    {"name": "Diamond Bay Resort & Spa", "stars": 4},
    {"name": "Sunrise Nha Trang Beach Hotel", "stars": 4},
    {"name": "Premier Village Phu Quoc", "stars": 5},
    {"name": "Fusion Resort Cam Ranh", "stars": 5},
]

MEAL_TYPES = ["BB", "HB", "FB", "AI", "UAI"]
STATUSES = ["new", "processing", "confirmed", "paid", "cancelled"]

DEMO_MESSAGES = [
    {
        "platform": "telegram",
        "text": "Здравствуйте! Интересует тур во Вьетнам на двоих, 10 дней",
        "from_username": "aigerim_n"
    },
    {
        "platform": "whatsapp",
        "text": "Добрый день! Какие отели есть в Нячанге с аквапарком?",
        "from_username": "Ержан"
    },
    {
        "platform": "telegram",
        "text": "Подскажите стоимость на 2 взрослых + 1 ребенок в октябре",
        "from_username": "dina_s"
    },
    {
        "platform": "whatsapp",
        "text": "Нужна помощь с визой во Вьетнам",
        "from_username": "Асель"
    },
    {
        "platform": "telegram",
        "text": "Хочу забронировать Vinpearl Resort на 7 ночей",
        "from_username": "murat_a"
    },
    {
        "platform": "whatsapp",
        "text": "Есть ли горящие туры на эту неделю?",
        "from_username": "Жанна"
    },
    {
        "platform": "telegram", 
        "text": "Можно ли продлить тур еще на 3 дня?",
        "from_username": "darkhan_s"
    },
    {
        "platform": "telegram",
        "text": "Спасибо за подборку! Беру второй вариант",
        "from_username": "saule_zh"
    },
    {
        "platform": "whatsapp",
        "text": "Когда нужно вносить предоплату?",
        "from_username": "Нурлан"
    },
    {
        "platform": "telegram",
        "text": "Отправьте, пожалуйста, программу экскурсий",
        "from_username": "gulnara_e"
    },
]

def clear_demo_data():
    """Очистка демо-данных"""
    print("🗑️  Очистка старых демо-данных...")
    
    # Создаем таблицы если их нет
    db.create_all()
    
    # Очищаем данные (в правильном порядке - сначала зависимые таблицы)
    try:
        db.session.query(Message).delete()
    except:
        pass
    
    try:
        db.session.query(OrderLog).delete()
    except:
        pass
        
    try:
        db.session.query(Order).delete()
    except:
        pass
        
    try:
        db.session.query(Client).delete()
    except:
        pass
        
    db.session.commit()
    
    print("✅ Демо-данные очищены")

def create_demo_clients():
    """Создание демо-клиентов"""
    print("👥 Создание демо-клиентов...")
    
    clients = []
    for client_data in DEMO_CLIENTS:
        client = Client(
            name=client_data["name"],
            phone=client_data["phone"],
            email=client_data["email"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
        )
        db.session.add(client)
        clients.append(client)
    
    db.session.commit()
    print(f"✅ Создано {len(clients)} клиентов")
    return clients

def create_demo_orders(clients):
    """Создание демо-заявок"""
    print("📋 Создание демо-заявок...")
    
    orders = []
    for i, client in enumerate(clients):
        # Каждому клиенту создаем 1-2 заявки
        num_orders = random.randint(1, 2)
        
        for j in range(num_orders):
            order_num = f"CB{datetime.utcnow().year}{(i*10 + j + 1):04d}"
            
            destination = random.choice(DEMO_DESTINATIONS)
            hotel = random.choice(DEMO_HOTELS)
            nights = random.choice([7, 10, 12, 14])
            check_in_days = random.randint(-30, 60)
            check_in = datetime.utcnow() + timedelta(days=check_in_days)
            check_out = check_in + timedelta(days=nights)
            
            adults = random.randint(1, 4)
            children = random.randint(0, 2)
            meal_type = random.choice(MEAL_TYPES)
            
            # Рассчитываем стоимость
            base_price = 250000 * nights * adults
            if children > 0:
                base_price += 150000 * nights * children
            
            # Добавляем вариацию в цене
            total_amount = base_price * random.uniform(0.9, 1.3)
            
            # Определяем статус
            if check_in_days < -5:
                status = random.choice(["paid", "confirmed"])
            elif check_in_days < 0:
                status = "confirmed"
            elif check_in_days < 30:
                status = random.choice(["processing", "confirmed", "new"])
            else:
                status = random.choice(["new", "processing"])
            
            if random.random() < 0.1:
                status = "cancelled"
            
            order = Order(
                number=order_num,
                client_id=client.id,
                client_name=client.name,
                client_phone=client.phone,
                client_email=client.email,
                destination=destination,
                hotel_name=hotel["name"],
                hotel_stars=hotel["stars"],
                check_in=check_in,
                check_out=check_out,
                nights=nights,
                adults=adults,
                children=children,
                meal_type=meal_type,
                total_amount=round(total_amount, 2),
                currency='KZT',
                status=status,
                source='demo',
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            
            db.session.add(order)
            orders.append(order)
            
            # Добавляем лог создания
            log = OrderLog(
                order=order,
                action='created',
                description=f'Заявка создана для {client.name}',
                created_at=order.created_at
            )
            db.session.add(log)
            
            # Добавляем логи изменения статуса
            if status in ['confirmed', 'paid']:
                log = OrderLog(
                    order=order,
                    action='status_changed',
                    old_value='new',
                    new_value='processing',
                    description='Заявка взята в обработку',
                    created_at=order.created_at + timedelta(hours=2)
                )
                db.session.add(log)
                
                log = OrderLog(
                    order=order,
                    action='status_changed',
                    old_value='processing',
                    new_value='confirmed',
                    description='Бронь подтверждена',
                    created_at=order.created_at + timedelta(days=1)
                )
                db.session.add(log)
            
            if status == 'paid':
                log = OrderLog(
                    order=order,
                    action='status_changed',
                    old_value='confirmed',
                    new_value='paid',
                    description='Оплата получена',
                    created_at=order.created_at + timedelta(days=2)
                )
                db.session.add(log)
    
    db.session.commit()
    print(f"✅ Создано {len(orders)} заявок")
    return orders

def create_demo_messages(clients):
    """Создание демо-сообщений"""
    print("💬 Создание демо-сообщений...")
    
    messages = []
    for i, msg_data in enumerate(DEMO_MESSAGES):
        if i < len(clients):
            client = clients[i]
            
            # Входящее сообщение от клиента
            msg_id = f"msg_{msg_data['platform']}_{i+1000}"
            chat_id = f"chat_{msg_data['platform']}_{client.id}"
            
            message = Message(
                platform=msg_data["platform"],
                chat_id=chat_id,
                message_id=msg_id,
                from_user_id=str(client.id),
                from_username=msg_data["from_username"],
                from_phone=client.phone if msg_data["platform"] == "whatsapp" else None,
                text=msg_data["text"],
                message_type="text",
                direction="incoming",
                is_read=random.choice([True, False]),
                replied=random.choice([True, False]),
                client_id=client.id,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                received_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            
            db.session.add(message)
            messages.append(message)
            
            # Исходящий ответ (для половины сообщений)
            if random.random() < 0.5:
                reply_texts = [
                    "Спасибо за обращение! Сейчас подберу для вас лучшие варианты.",
                    "Здравствуйте! С удовольствием помогу с подбором тура.",
                    "Отлично! Отправляю вам подборку отелей.",
                    "Конечно! Вот актуальные предложения на ваши даты.",
                    "Добрый день! Все детали отправил вам на почту.",
                ]
                
                reply_msg = Message(
                    platform=msg_data["platform"],
                    chat_id=chat_id,
                    message_id=f"{msg_id}_reply",
                    from_user_id="agent_1",
                    from_username="Crystal Bay Travel",
                    text=random.choice(reply_texts),
                    message_type="text",
                    direction="outgoing",
                    is_read=True,
                    replied=False,
                    created_at=message.created_at + timedelta(minutes=random.randint(5, 120)),
                    received_at=message.received_at + timedelta(minutes=random.randint(5, 120))
                )
                
                db.session.add(reply_msg)
                messages.append(reply_msg)
    
    db.session.commit()
    print(f"✅ Создано {len(messages)} сообщений")
    return messages

def main():
    """Главная функция генерации демо-данных"""
    print("\n" + "="*60)
    print("🎭 ГЕНЕРАЦИЯ ДЕМОНСТРАЦИОННЫХ ДАННЫХ")
    print("Crystal Bay Travel - Demo Data Generator")
    print("="*60 + "\n")
    
    try:
        with app.app_context():
            # Очистка старых данных
            clear_demo_data()
            
            # Создание новых демо-данных
            clients = create_demo_clients()
            orders = create_demo_orders(clients)
            messages = create_demo_messages(clients)
            
            print("\n" + "="*60)
            print("🎉 ДЕМО-ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
            print("="*60)
            print(f"👥 Клиентов: {len(clients)}")
            print(f"📋 Заявок: {len(orders)}")
            print(f"💬 Сообщений: {len(messages)}")
            print("="*60 + "\n")
            
            print("✅ Дашборд готов к демонстрации!")
            print("🌐 Откройте веб-интерфейс для просмотра данных\n")
        
    except Exception as e:
        print(f"\n❌ Ошибка при генерации данных: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
