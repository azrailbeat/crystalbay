# Post-Deployment Testing Guide

## После установки на новом сервере с whitelisted IP

### 🎯 Тестовый план для подтверждения работоспособности

#### 1. Базовые проверки системы
```bash
# Проверка доступности
curl http://server-ip:5000/health

# Проверка API endpoints
curl http://server-ip:5000/api/diagnostics/server
curl http://server-ip:5000/api/diagnostics/network
curl http://server-ip:5000/api/diagnostics/samo
```

#### 2. Веб-интерфейс тестирование
- Открыть http://server-ip:5000
- Перейти в "SAMO API & Тестирование"
- Проверить статус подключения (должен быть зеленый)
- Запустить "Быстрые тесты"

#### 3. SAMO API функциональность
Должны работать без ошибок:
- ✅ Валюты (SearchTour_CURRENCIES)
- ✅ Страны (SearchTour_STATES) 
- ✅ Города отправления (SearchTour_TOWNFROMS)
- ✅ Отели (SearchTour_HOTELS)
- ✅ Типы питания (SearchTour_MEALS)
- ✅ Звездность (SearchTour_STARS)
- ✅ Поиск туров (SearchTour)

#### 4. Ожидаемые изменения после whitelist
**До whitelist (текущее состояние):**
```
IP 34.139.145.98 НЕ в whitelist SAMO. Обратитесь в техподдержку SAMO.
HTTP 403 Forbidden - blacklisted address
```

**После whitelist (ожидаемый результат):**
```
✅ SAMO API подключен успешно
✅ Валюты получены: 15+ записей
✅ Страны получены: 20+ записей
✅ Поиск туров: найдено туров
```

#### 5. Curl команды для проверки
```bash
# Тест валют
curl "https://booking.crystalbay.com/export/default.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "apiKey=SAMO_TOKEN&action=SearchTour_CURRENCIES"

# Тест поиска туров
curl "https://booking.crystalbay.com/export/default.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "apiKey=SAMO_TOKEN&action=SearchTour&TOWNFROM=1&DATEBEG=2025-03-01&DATEEND=2025-03-31&NIGHTBEG=7&NIGHTEND=14&ADULT=2"
```

#### 6. Диагностика JavaScript
- Открыть Developer Tools (F12)
- Проверить Console на отсутствие ошибок
- Выполнить тесты через веб-интерфейс
- Убедиться что JSON парсится корректно

#### 7. Сравнение с предыдущими результатами
**Документировать изменения:**
- Скриншоты до и после
- Логи curl команд
- Результаты тестов в веб-интерфейсе
- Время отклика API

### 📊 Метрики успешной установки
- SAMO API: 100% успешных запросов
- Время отклика: < 2 секунд
- JavaScript: 0 ошибок в консоли
- Веб-интерфейс: полная функциональность
- Диагностика: все тесты зеленые

### 🔄 Если что-то не работает
1. Проверить переменные окружения
2. Убедиться что IP действительно в whitelist
3. Проверить логи приложения
4. Протестировать прямые curl команды
5. Обратиться к документации SAMO API