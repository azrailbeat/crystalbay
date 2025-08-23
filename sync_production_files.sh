#!/bin/bash

# Скрипт для синхронизации исправленных файлов с продакшн сервером

echo "🔄 СИНХРОНИЗАЦИЯ С ПРОДАКШН СЕРВЕРОМ"
echo "===================================="

SERVER="46.250.234.89"
PROJECT_DIR="/home/runner/workspace"
REMOTE_DIR="~/crystalbay"

echo "📍 Сервер: $SERVER"
echo "📁 Локальная папка: $PROJECT_DIR"
echo "📁 Удаленная папка: $REMOTE_DIR"

echo ""
echo "1️⃣ Создание архива с исправленными файлами..."

# Создаем архив с исправленными файлами
tar -czf production_sync.tar.gz \
    templates/samo_testing.html \
    app_api.py \
    main.py \
    models.py \
    crystal_bay_samo_api.py

echo "✅ Архив создан: production_sync.tar.gz"

echo ""
echo "2️⃣ Команды для развертывания на сервере:"
echo "========================================"

cat << 'DEPLOYMENT_COMMANDS'
# Выполните эти команды на продакшн сервере:

# 1. Скопировать архив на сервер
scp production_sync.tar.gz root@46.250.234.89:~/

# 2. Подключиться к серверу
ssh root@46.250.234.89

# 3. На сервере выполнить:
cd ~/crystalbay
docker-compose down
tar -xzf ~/production_sync.tar.gz
docker-compose build --no-cache web
docker-compose up -d
sleep 30
curl http://127.0.0.1:5000/health

# 4. Проверить что исправления работают:
curl http://127.0.0.1:5000/api/diagnostics/samo
DEPLOYMENT_COMMANDS

echo ""
echo "3️⃣ Проверка того что нужно исправить:"
echo "====================================="

echo "❌ Текущие проблемы на продакшн:"
echo "   - Unexpected token '<' ошибки"
echo "   - API endpoints возвращают HTML вместо JSON"
echo "   - JavaScript функции не работают"
echo ""
echo "✅ После развертывания должно работать:"
echo "   - Зеленый статус 'SAMO API подключен успешно'"
echo "   - Диагностические кнопки без ошибок"
echo "   - JSON ответы от всех API endpoints"

echo ""
echo "📋 ГОТОВО К РАЗВЕРТЫВАНИЮ!"
echo "Архив production_sync.tar.gz содержит все исправления"