# Crystal Bay Travel - Docker Краткий справочник

## Основные команды

### Запуск и остановка

```bash
# Автоматический запуск
./docker-run.sh

# Ручной запуск (разработка)
docker-compose up -d

# Ручной запуск (продакшн)
docker-compose -f docker-compose.production.yml up -d

# Остановка
docker-compose down

# Остановка с удалением volumes (ВНИМАНИЕ: удалит данные!)
docker-compose down -v
```

### Мониторинг

```bash
# Статус сервисов
docker-compose ps

# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Ресурсы
docker stats

# Health check
curl http://localhost/health
```

### Backup и восстановление

```bash
# Backup
docker-compose exec -T db pg_dump -U crystalbay crystalbay_db > backup_$(date +%Y%m%d).sql

# Восстановление
docker-compose exec -T db psql -U crystalbay crystalbay_db < backup_file.sql
```

### Обновление

```bash
# Простое обновление
git pull origin main
docker-compose build --no-cache web
docker-compose up -d

# Полное обновление
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose -f docker-compose.production.yml up -d
```

### Отладка

```bash
# Подключение к контейнеру
docker-compose exec web bash
docker-compose exec db psql -U crystalbay crystalbay_db

# Проверка переменных окружения
docker-compose exec web env | grep SAMO

# Проверка сети
docker network inspect crystalbay_crystal_bay_network

# Очистка системы
docker system prune -f
```

## Частые проблемы и решения

### Проблема: Контейнер не запускается

```bash
# Диагностика
docker-compose logs web
docker-compose ps

# Решение
docker-compose down
docker-compose up -d
```

### Проблема: База данных недоступна

```bash
# Проверка
docker-compose exec db pg_isready -U crystalbay

# Решение
docker-compose restart db
sleep 10
docker-compose restart web
```

### Проблема: SAMO API ошибки

```bash
# Проверка токена
docker-compose exec web env | grep SAMO_OAUTH_TOKEN

# Тест подключения
curl http://localhost/api/samo/test
```

### Проблема: Недостаточно места

```bash
# Очистка
docker image prune -f
docker container prune -f
docker volume prune -f
```

## Полезные эндпоинты

- **Главная:** http://localhost/
- **Health:** http://localhost/health
- **SAMO тест:** http://localhost/samo-testing
- **Админ:** http://localhost/admin (если настроено)

## Файлы конфигурации

- `docker-compose.yml` - Разработка
- `docker-compose.production.yml` - Продакшн
- `Dockerfile.optimized` - Образ приложения
- `nginx-docker.conf` - Настройки Nginx
- `.env` - Переменные окружения

## Переменные окружения

### Обязательные
```env
FLASK_SECRET_KEY=секретный-ключ
SAMO_OAUTH_TOKEN=samo-токен
DATABASE_URL=postgresql://crystalbay:password@db:5432/crystalbay_db
```

### Опциональные
```env
OPENAI_API_KEY=openai-ключ
TELEGRAM_BOT_TOKEN=telegram-токен
WAZZUP_API_KEY=wazzup-ключ
```

## Порты

- **80** - HTTP (Nginx)
- **443** - HTTPS (Nginx + SSL)
- **5000** - Flask приложение (только в dev режиме)
- **5432** - PostgreSQL (внутренний)
- **6379** - Redis (внутренний)

## Volumes

- `postgres_data` - Данные PostgreSQL
- `static_files` - Статические файлы
- `app_logs` - Логи приложения
- `redis_data` - Данные Redis

---

**Совет:** Добавьте этот файл в закладки для быстрого доступа к командам!