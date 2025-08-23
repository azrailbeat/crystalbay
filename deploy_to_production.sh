#!/bin/bash

# Скрипт для развертывания исправлений на продакшн сервере

echo "🚀 РАЗВЕРТЫВАНИЕ ИСПРАВЛЕНИЙ НА ПРОДАКШН"
echo "======================================="

SERVER="46.250.234.89"
echo "📍 Сервер: $SERVER"

echo "1️⃣ Копирование исправленных файлов на сервер..."

# Копируем исправленные файлы
scp templates/samo_testing.html root@$SERVER:~/crystalbay/templates/
scp app_api.py root@$SERVER:~/crystalbay/

echo "2️⃣ Перезапуск контейнеров на сервере..."

# Подключаемся к серверу и перезапускаем
ssh root@$SERVER << 'EOF'
cd ~/crystalbay
echo "Остановка контейнеров..."
docker-compose down
echo "Пересборка образов..."
docker-compose build --no-cache web
echo "Запуск контейнеров..."
docker-compose up -d
echo "Ожидание готовности..."
sleep 30
echo "Проверка статуса..."
docker-compose ps
curl -fsS http://127.0.0.1:5000/health
EOF

echo "3️⃣ Проверка исправлений..."
sleep 10

# Проверяем что исправления работают
if curl -fsS "http://$SERVER:5000/samo-testing" | grep -q "SAMO API подключен успешно"; then
    echo "✅ Исправления успешно развернуты!"
    echo "🎉 На продакшн сервере теперь показывается зеленый статус"
else
    echo "⚠️  Исправления развернуты, но требуется ручная проверка"
fi

echo ""
echo "🌐 Проверьте: http://$SERVER:5000/samo-testing"