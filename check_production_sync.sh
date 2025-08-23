#!/bin/bash

# Скрипт проверки синхронизации кода на продакшн сервере

echo "🔍 ПРОВЕРКА СИНХРОНИЗАЦИИ ПРОДАКШН СЕРВЕРА"
echo "=========================================="

SERVER="46.250.234.89"
PORT="5000"

echo "📍 Сервер: $SERVER:$PORT"
echo ""

# 1. Проверка доступности сервера
echo "1️⃣ Проверка доступности сервера..."
if curl -fsS "http://$SERVER:$PORT/health" >/dev/null 2>&1; then
    echo "✅ Сервер доступен"
else
    echo "❌ Сервер недоступен!"
    exit 1
fi

# 2. Проверка health endpoint
echo ""
echo "2️⃣ Проверка health endpoint..."
health_response=$(curl -fsS "http://$SERVER:$PORT/health" 2>/dev/null)
if echo "$health_response" | grep -q '"status":"healthy"'; then
    echo "✅ Health endpoint работает корректно"
    echo "   Response: $health_response"
else
    echo "❌ Health endpoint возвращает некорректный ответ"
    echo "   Response: $health_response"
fi

# 3. Проверка диагностических API (должны возвращать JSON)
echo ""
echo "3️⃣ Проверка диагностических API..."

api_endpoints=(
    "environment"
    "server" 
    "network"
    "samo"
)

for endpoint in "${api_endpoints[@]}"; do
    echo "   Проверка /api/diagnostics/$endpoint..."
    response=$(curl -fsS "http://$SERVER:$PORT/api/diagnostics/$endpoint" 2>/dev/null)
    
    if echo "$response" | grep -q '^{.*}$'; then
        echo "   ✅ $endpoint - возвращает JSON"
    elif echo "$response" | grep -q '<html\|<HTML\|<!DOCTYPE'; then
        echo "   ❌ $endpoint - возвращает HTML (старая версия!)"
    else
        echo "   ⚠️  $endpoint - неопределенный ответ"
        echo "      Первые 100 символов: ${response:0:100}"
    fi
done

# 4. Проверка curl функций
echo ""
echo "4️⃣ Проверка curl функций..."
curl_response=$(curl -fsS -X POST "http://$SERVER:$PORT/api/samo/execute-curl" \
    -H "Content-Type: application/json" \
    -d '{"method":"SearchTour_CURRENCIES","params":""}' 2>/dev/null)

if echo "$curl_response" | grep -q '"command".*"status_code"'; then
    echo "✅ Curl функции работают корректно (возвращают JSON)"
    # Извлекаем статус код
    status_code=$(echo "$curl_response" | grep -o '"status_code":[0-9]*' | cut -d':' -f2)
    echo "   HTTP Status Code: $status_code"
    
    if [ "$status_code" = "403" ]; then
        echo "   ⚠️  SAMO API блокирует IP (ожидаемо)"
    fi
else
    echo "❌ Curl функции возвращают некорректный ответ"
    echo "   Response: ${curl_response:0:200}"
fi

# 5. Проверка текущего IP
echo ""
echo "5️⃣ Получение текущего IP сервера..."
server_response=$(curl -fsS "http://$SERVER:$PORT/api/diagnostics/server" 2>/dev/null)
current_ip=$(echo "$server_response" | grep -o '"external_ip":"[^"]*' | cut -d'"' -f4)

if [ -n "$current_ip" ]; then
    echo "✅ IP сервера: $current_ip"
    echo "   💡 Для разблокировки SAMO API используйте этот IP"
else
    echo "❌ Не удалось получить IP сервера"
fi

# 6. Тест веб-интерфейса
echo ""
echo "6️⃣ Проверка веб-интерфейса..."
main_page=$(curl -fsS "http://$SERVER:$PORT/" 2>/dev/null)
if echo "$main_page" | grep -q "Crystal Bay Travel"; then
    echo "✅ Главная страница загружается"
else
    echo "❌ Проблема с главной страницей"
fi

samo_page=$(curl -fsS "http://$SERVER:$PORT/samo-testing" 2>/dev/null)
if echo "$samo_page" | grep -q "SAMO API"; then
    echo "✅ Страница SAMO тестирования доступна"
else
    echo "❌ Проблема со страницей SAMO тестирования"
fi

# 7. Итоговая оценка
echo ""
echo "🎯 ИТОГОВАЯ ОЦЕНКА СИНХРОНИЗАЦИИ"
echo "================================"

# Подсчет успешных проверок
checks_passed=0
total_checks=0

# Health
if echo "$health_response" | grep -q '"status":"healthy"'; then
    ((checks_passed++))
fi
((total_checks++))

# API endpoints
for endpoint in "${api_endpoints[@]}"; do
    response=$(curl -fsS "http://$SERVER:$PORT/api/diagnostics/$endpoint" 2>/dev/null)
    if echo "$response" | grep -q '^{.*}$'; then
        ((checks_passed++))
    fi
    ((total_checks++))
done

# Curl functions
if echo "$curl_response" | grep -q '"command".*"status_code"'; then
    ((checks_passed++))
fi
((total_checks++))

# Web interface
if echo "$main_page" | grep -q "Crystal Bay Travel"; then
    ((checks_passed++))
fi
((total_checks++))

echo "📊 Результат: $checks_passed/$total_checks проверок прошли успешно"

if [ $checks_passed -eq $total_checks ]; then
    echo "🎉 ПРОДАКШН СЕРВЕР ПОЛНОСТЬЮ СИНХРОНИЗИРОВАН"
    echo "   Все компоненты работают корректно"
elif [ $checks_passed -ge $((total_checks * 3 / 4)) ]; then
    echo "⚠️  ПРОДАКШН СЕРВЕР ЧАСТИЧНО СИНХРОНИЗИРОВАН"
    echo "   Большинство компонентов работает, но есть проблемы"
else
    echo "❌ ПРОДАКШН СЕРВЕР НЕ СИНХРОНИЗИРОВАН"
    echo "   Требуется обновление кода на сервере"
fi

echo ""
echo "📋 ДЕЙСТВИЯ ПРИ ПРОБЛЕМАХ:"
echo "1. Подключиться к серверу: ssh root@$SERVER"
echo "2. Перейти в папку проекта: cd ~/crystalbay"
echo "3. Остановить контейнеры: docker-compose down"
echo "4. Обновить файлы app_api.py и templates/samo_testing.html"
echo "5. Пересобрать: docker-compose build --no-cache"
echo "6. Запустить: docker-compose up -d"
echo "7. Повторить проверку: ./check_production_sync.sh"