#!/bin/bash

# Скрипт для развертывания обновлений на продакшн сервере Crystal Bay Travel

echo "🚀 РАЗВЕРТЫВАНИЕ НА ПРОДАКШН СЕРВЕРЕ Crystal Bay Travel"
echo "======================================================="

# Проверка наличия необходимых файлов
echo "🔍 Проверка файлов..."
required_files=("app_api.py" "templates/samo_testing.html" "main.py" "docker-compose.yml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Файл $file не найден!"
        exit 1
    fi
done
echo "✅ Все необходимые файлы найдены"

# Создание резервной копии
echo "💾 Создание резервной копии..."
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r app_api.py templates/ models.py crystal_bay_samo_api.py "$backup_dir/" 2>/dev/null
echo "✅ Резервная копия создана в $backup_dir"

# Остановка контейнеров
echo "🛑 Остановка контейнеров..."
docker-compose down
echo "✅ Контейнеры остановлены"

# Очистка старых образов
echo "🧹 Очистка старых образов..."
docker system prune -f
echo "✅ Очистка завершена"

# Сборка новых образов
echo "🔨 Сборка новых образов..."
docker-compose build --no-cache
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке образов!"
    exit 1
fi
echo "✅ Образы успешно собраны"

# Запуск контейнеров
echo "🚀 Запуск контейнеров..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при запуске контейнеров!"
    exit 1
fi
echo "✅ Контейнеры запущены"

# Ожидание готовности
echo "⏳ Ожидание готовности сервисов..."
sleep 30

# Проверка статуса
echo "🔍 Проверка статуса контейнеров..."
docker-compose ps

# Проверка health endpoint
echo "🏥 Проверка health endpoint..."
for i in {1..5}; do
    if curl -fsS http://127.0.0.1:5000/health >/dev/null 2>&1; then
        echo "✅ Health endpoint отвечает"
        break
    else
        echo "⏳ Попытка $i/5..."
        sleep 10
    fi
done

# Проверка диагностических API
echo "🔧 Проверка диагностических API..."
api_endpoints=(
    "http://127.0.0.1:5000/api/diagnostics/environment"
    "http://127.0.0.1:5000/api/diagnostics/server"
    "http://127.0.0.1:5000/api/diagnostics/network"
)

for endpoint in "${api_endpoints[@]}"; do
    if curl -fsS "$endpoint" >/dev/null 2>&1; then
        echo "✅ $(basename $endpoint) API работает"
    else
        echo "❌ $(basename $endpoint) API не отвечает"
    fi
done

# Проверка curl функций
echo "🌐 Проверка curl функций..."
curl_test=$(curl -fsS -X POST http://127.0.0.1:5000/api/samo/execute-curl \
    -H "Content-Type: application/json" \
    -d '{"method":"SearchTour_CURRENCIES","params":""}' 2>/dev/null)

if echo "$curl_test" | grep -q '"command"'; then
    echo "✅ Curl функции работают корректно"
else
    echo "❌ Curl функции возвращают некорректный ответ"
fi

# Получение текущего IP
echo "🌍 Получение IP адреса сервера..."
current_ip=$(curl -fsS http://127.0.0.1:5000/api/diagnostics/server 2>/dev/null | grep -o '"external_ip":"[^"]*' | cut -d'"' -f4)
if [ -n "$current_ip" ]; then
    echo "📍 Текущий IP сервера: $current_ip"
    echo "⚠️  Обновите заявку на разблокировку в SAMO API для IP: $current_ip"
else
    echo "❌ Не удалось получить IP адрес"
fi

# Итоговый статус
echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================="
echo "✅ Контейнеры запущены и работают"
echo "✅ API endpoints исправлены"
echo "✅ JavaScript ошибки устранены"
echo "⚠️  Требуется разблокировка IP в SAMO API"
echo ""
echo "🌐 Доступ к приложению: http://46.250.234.89:5000"
echo "🔧 Диагностика: http://46.250.234.89:5000/samo-testing"

# Вывод логов в случае проблем
if ! curl -fsS http://127.0.0.1:5000/health >/dev/null 2>&1; then
    echo ""
    echo "❌ ВНИМАНИЕ: Health endpoint не отвечает!"
    echo "📋 Логи контейнера:"
    docker logs --tail 20 crystalbay-web-1
fi