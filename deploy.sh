#!/bin/bash

# Crystal Bay Travel - Deployment Script
# Скрипт для автоматического развертывания на сервере

set -e

echo "🚀 Начинаем развертывание Crystal Bay Travel..."

# Проверка Python версии
echo "📋 Проверка системных требований..."
python3 --version || { echo "❌ Python 3 не найден"; exit 1; }

# Обновление кода
if [ -d ".git" ]; then
    echo "📥 Обновление кода из репозитория..."
    git pull origin main
fi

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "🔧 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация окружения и установка зависимостей
echo "📦 Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt

# Проверка переменных окружения
echo "🔐 Проверка конфигурации..."
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден! Скопируйте .env.example в .env и настройте переменные."
    cp .env.example .env
    echo "📝 Создан файл .env из шаблона. Отредактируйте его перед следующим запуском."
    exit 1
fi

# Проверка подключения к базе данных
echo "🗄️ Проверка подключения к базе данных..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('❌ DATABASE_URL не настроен')
    exit(1)
print('✅ DATABASE_URL настроен')
"

# Тестовый запуск
echo "🧪 Тестовый запуск приложения..."
timeout 10s python3 main.py &
MAIN_PID=$!
sleep 5

# Проверка health endpoint
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Приложение успешно запущено"
    kill $MAIN_PID 2>/dev/null || true
else
    echo "❌ Приложение не отвечает на health check"
    kill $MAIN_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 Развертывание завершено успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте .env файл с вашими API ключами"
echo "2. Настройте Nginx (опционально)"
echo "3. Создайте systemd сервис для автозапуска"
echo "4. Запустите приложение:"
echo "   source venv/bin/activate"
echo "   gunicorn --bind 0.0.0.0:5000 --workers 3 main:app"
echo ""
echo "📖 Полная инструкция в файле DEPLOYMENT_GUIDE.md"