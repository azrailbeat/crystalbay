#!/bin/bash

# Crystal Bay Travel - Docker Run Script
# Скрипт для быстрого запуска в Docker

set -e

echo "🐳 Запуск Crystal Bay Travel в Docker..."

# Проверка существования .env файла
if [ ! -f ".env" ]; then
    echo "📋 Создание .env файла из шаблона..."
    cp .env.docker .env
    echo "⚠️  Отредактируйте .env файл с вашими настройками перед продолжением!"
    echo "   nano .env"
    read -p "Нажмите Enter после настройки .env файла..."
fi

# Выбор конфигурации
echo "Выберите режим запуска:"
echo "1) Разработка (docker-compose.yml)"
echo "2) Продакшн (docker-compose.production.yml)"
read -p "Введите номер (1-2): " choice

case $choice in
    1)
        COMPOSE_FILE="docker-compose.yml"
        echo "🔧 Режим разработки"
        ;;
    2)
        COMPOSE_FILE="docker-compose.production.yml"
        echo "🚀 Режим продакшн"
        ;;
    *)
        echo "❌ Неверный выбор. Используем режим разработки."
        COMPOSE_FILE="docker-compose.yml"
        ;;
esac

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose -f $COMPOSE_FILE down || true

# Сборка образов
echo "🔨 Сборка Docker образов..."
docker-compose -f $COMPOSE_FILE build --no-cache

# Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose -f $COMPOSE_FILE up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка health checks
echo "🔍 Проверка состояния сервисов..."
docker-compose -f $COMPOSE_FILE ps

# Проверка приложения
echo "🧪 Проверка приложения..."
for i in {1..10}; do
    if curl -s http://localhost/health > /dev/null; then
        echo "✅ Приложение успешно запущено!"
        echo "🌐 Доступно по адресу: http://localhost"
        echo "📊 Health check: http://localhost/health"
        echo "🔧 SAMO API тест: http://localhost/samo-testing"
        break
    else
        echo "⏳ Попытка $i/10..."
        sleep 5
    fi
done

echo ""
echo "📋 Полезные команды:"
echo "Просмотр логов:     docker-compose -f $COMPOSE_FILE logs -f"
echo "Остановка:          docker-compose -f $COMPOSE_FILE down"
echo "Перезапуск:         docker-compose -f $COMPOSE_FILE restart"
echo "Статус:             docker-compose -f $COMPOSE_FILE ps"
echo "Health check:       curl http://localhost/health"
echo "SAMO тест:          curl http://localhost/api/samo/test"
echo ""
echo "📖 Документация:"
echo "Полное руководство: cat DOCKER_GUIDE.md"
echo "Краткий справочник: cat DOCKER_QUICK_REFERENCE.md"
echo ""
echo "🔧 Отладка:"
echo "Логи ошибок:        docker-compose -f $COMPOSE_FILE logs web | grep ERROR"
echo "Подключение к БД:   docker-compose -f $COMPOSE_FILE exec db psql -U crystalbay crystalbay_db"
echo "Переменные среды:   docker-compose -f $COMPOSE_FILE exec web env | grep -E '(SAMO|DATABASE|FLASK)'"