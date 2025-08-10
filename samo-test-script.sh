#!/bin/bash

# Скрипт для тестирования SAMO API подключения
# Используется для диагностики проблем с IP whitelist

echo "🔍 Диагностика SAMO API подключения"
echo "=================================="

# Проверка IP адреса сервера
echo "📍 IP адрес сервера:"
CURRENT_IP=$(curl -s ifconfig.me)
echo "   $CURRENT_IP"
echo ""

# Тест прямого подключения к SAMO API
echo "🧪 Тест подключения к SAMO API..."

SAMO_URL="https://booking-kz.crystalbay.com/export/default.php"
OAUTH_TOKEN="27bd59a7ac67422189789f0188167379"

# Создание временного файла с данными запроса
cat > /tmp/samo_test_data << EOF
samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token=$OAUTH_TOKEN
EOF

echo "📤 Отправка запроса к SAMO API..."
echo "   URL: $SAMO_URL"
echo "   Токен: $OAUTH_TOKEN"
echo ""

# Выполнение запроса с подробным выводом
HTTP_CODE=$(curl -w "%{http_code}" -o /tmp/samo_response.txt -s \
  -X POST "$SAMO_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Crystal Bay Travel Integration/1.0" \
  -d @/tmp/samo_test_data)

echo "📊 Результат:"
echo "   HTTP код: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Успешное подключение!"
    echo ""
    echo "📄 Ответ SAMO API:"
    cat /tmp/samo_response.txt | python3 -m json.tool 2>/dev/null || cat /tmp/samo_response.txt
elif [ "$HTTP_CODE" = "403" ]; then
    echo "   ❌ Ошибка 403 - Доступ запрещен"
    echo ""
    echo "🚨 ДИАГНОЗ: IP адрес $CURRENT_IP НЕ добавлен в whitelist SAMO"
    echo ""
    echo "📞 РЕШЕНИЕ:"
    echo "   1. Обратитесь в техподдержку SAMO:"
    echo "      Email: support@samo-tours.ru"
    echo "      Сайт: https://samo-tours.ru"
    echo ""
    echo "   2. Укажите следующие данные:"
    echo "      - Компания: Crystal Bay Travel"
    echo "      - IP для добавления: $CURRENT_IP"
    echo "      - OAuth токен: $OAUTH_TOKEN"
    echo "      - Назначение: API интеграция"
    echo ""
    echo "📄 Ответ сервера:"
    cat /tmp/samo_response.txt
else
    echo "   ❌ Неожиданная ошибка (код: $HTTP_CODE)"
    echo ""
    echo "📄 Ответ сервера:"
    cat /tmp/samo_response.txt
fi

echo ""
echo "=================================="

# Тест подключения через приложение
echo "🖥️  Тест через приложение Crystal Bay:"

if command -v curl >/dev/null 2>&1; then
    APP_RESPONSE=$(curl -s http://localhost:5000/api/samo/test 2>/dev/null || curl -s http://localhost/api/samo/test 2>/dev/null)
    
    if [ -n "$APP_RESPONSE" ]; then
        echo "   Ответ приложения:"
        echo "$APP_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$APP_RESPONSE"
    else
        echo "   ❌ Приложение не отвечает на SAMO тест"
    fi
else
    echo "   ❌ curl не установлен"
fi

echo ""

# Проверка доступности других эндпоинтов
echo "🌐 Проверка доступности основных функций:"

# Health check
HEALTH_CHECK=$(curl -s http://localhost:5000/health 2>/dev/null || curl -s http://localhost/health 2>/dev/null)
if echo "$HEALTH_CHECK" | grep -q "healthy\|success" 2>/dev/null; then
    echo "   ✅ Health check: OK"
else
    echo "   ❌ Health check: Недоступен"
fi

# Главная страница
MAIN_PAGE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ 2>/dev/null || curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
if [ "$MAIN_PAGE" = "200" ]; then
    echo "   ✅ Главная страница: OK"
else
    echo "   ❌ Главная страница: Код $MAIN_PAGE"
fi

echo ""
echo "📋 Резюме:"
echo "   - Сервер IP: $CURRENT_IP"
echo "   - SAMO API: $([ "$HTTP_CODE" = "200" ] && echo "✅ Работает" || echo "❌ Заблокирован (IP не в whitelist)")"
echo "   - Приложение: $([ -n "$HEALTH_CHECK" ] && echo "✅ Запущено" || echo "❌ Не отвечает")"

if [ "$HTTP_CODE" != "200" ]; then
    echo ""
    echo "🎯 СЛЕДУЮЩИЕ ШАГИ:"
    echo "   1. Отправьте запрос в SAMO для добавления IP: $CURRENT_IP"
    echo "   2. Дождитесь подтверждения (обычно 1-4 часа в рабочее время)"
    echo "   3. Запустите этот скрипт снова для проверки"
    echo "   4. После успешного подключения протестируйте все функции SAMO API"
fi

# Очистка временных файлов
rm -f /tmp/samo_test_data /tmp/samo_response.txt

echo ""
echo "✅ Диагностика завершена"