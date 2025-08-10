# Диагностика подключения SAMO API

## Текущая проблема

**Ошибка:** 403 Client Error: Forbidden  
**URL:** https://booking-kz.crystalbay.com/export/default.php  
**Токен:** 27bd59a7ac67422189789f0188167379  

## Причина проблемы

SAMO API требует добавления IP адреса сервера в whitelist. Ваш сервер имеет IP **46.250.234.89**, который **НЕ** добавлен в whitelist SAMO.

## Логи системы

Из логов видно:
```
2025-08-10 09:51:17,074 - proxy_client - WARNING - No proxy host configured, requests will go direct
2025-08-10 09:51:17,074 - crystal_bay_samo_api - INFO - SAMO API запрос (direct): SearchTour_CURRENCIES
2025-08-10 09:51:17,453 - crystal_bay_samo_api - ERROR - SAMO API ошибка запроса SearchTour_CURRENCIES: 403 Client Error: Forbidden
```

Система пытается:
1. VPS proxy (не настроен)
2. TinyProxy (не настроен)
3. Прямое подключение (заблокировано IP whitelist)

## Решения

### Решение 1: Добавление IP в SAMO Whitelist (рекомендуется)

**Обратитесь к технической поддержке SAMO:**

📞 **Контакты SAMO:**
- Email: support@samo-tours.ru
- Телефон: указан в личном кабинете SAMO
- Онлайн чат: https://samo-tours.ru

**Информация для запроса:**
```
Тема: Добавление IP в whitelist для API
Компания: Crystal Bay Travel
IP адрес: 46.250.234.89
OAuth токен: 27bd59a7ac67422189789f0188167379
Назначение: Интеграция туристического сайта
```

### Решение 2: Использование прокси-сервера

Если у вас есть сервер с разрешенным IP:

```bash
# На сервере с разрешенным IP
sudo apt install tinyproxy
sudo nano /etc/tinyproxy/tinyproxy.conf

# Добавить:
# Allow 46.250.234.89
# Port 8888

sudo systemctl restart tinyproxy
```

Затем в .env на основном сервере:
```env
PROXY_HOST=разрешенный-ip-сервера
PROXY_PORT=8888
```

### Решение 3: Временный тест через другой IP

Для тестирования можно использовать VPN или прокси с разрешенным IP.

## Проверка текущего статуса

### Тест подключения

```bash
# На сервере 46.250.234.89
curl -X POST "https://booking-kz.crystalbay.com/export/default.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token=27bd59a7ac67422189789f0188167379"
```

**Ожидаемый результат:** 403 Forbidden (текущий статус)  
**После добавления в whitelist:** JSON с данными валют

### Проверка IP сервера

```bash
# Убедиться в IP адресе
curl ifconfig.me
# Результат: 46.250.234.89
```

### Тест с авторизованного IP

Если есть доступ к серверу с разрешенным IP, тест:

```bash
curl -X POST "https://booking-kz.crystalbay.com/export/default.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token=27bd59a7ac67422189789f0188167379"
```

## Альтернативные методы подключения

### Метод 1: SSH туннель

Если есть сервер с разрешенным IP:

```bash
# Создание SSH туннеля
ssh -L 8080:booking-kz.crystalbay.com:443 user@разрешенный-ip-сервер

# В приложении использовать localhost:8080
```

### Метод 2: Nginx proxy

На сервере с разрешенным IP:

```nginx
location /samo-proxy/ {
    proxy_pass https://booking-kz.crystalbay.com/export/;
    proxy_set_header Host booking-kz.crystalbay.com;
    proxy_ssl_server_name on;
}
```

## Что делать сейчас

### Немедленные действия:

1. **Отправьте запрос в SAMO** с указанными выше данными
2. **Дождитесь подтверждения** добавления IP в whitelist
3. **Протестируйте подключение** после подтверждения

### Временное решение:

Пока IP не добавлен, можно:
- Разработать и тестировать интерфейс с mock данными
- Настроить остальные функции системы
- Подготовить документацию

### После добавления IP:

```bash
# Тест подключения
curl http://46.250.234.89/api/samo/test

# Проверка данных
curl http://46.250.234.89/api/samo/currencies
curl http://46.250.234.89/api/samo/states
```

## Контрольный список

- [ ] Запрос отправлен в SAMO техподдержку
- [ ] Указан правильный IP: 46.250.234.89
- [ ] Указан OAuth токен: 27bd59a7ac67422189789f0188167379
- [ ] Получено подтверждение от SAMO
- [ ] Протестировано подключение
- [ ] SAMO API работает в приложении

## Время решения

**Обычно SAMO добавляет IP в whitelist в течение:**
- Рабочие часы: 1-4 часа
- Нерабочие часы: до 24 часов
- Выходные: до 48 часов

## Контактная информация

**Для техподдержки SAMO указать:**
- Компания: Crystal Bay Travel
- Сайт: crystalbay.com
- IP: 46.250.234.89
- Назначение: API интеграция туристического портала
- Токен: 27bd59a7ac67422189789f0188167379

---

**Статус:** IP не в whitelist - требуется обращение в SAMO  
**Приоритет:** Критический - блокирует основную функциональность  
**Действие:** Немедленно связаться с SAMO техподдержкой