# Crystal Bay Travel - Docker Deployment Guide

## Обзор

Docker контейнеризация позволяет легко развернуть приложение Crystal Bay Travel на любом сервере с минимальными зависимостями.

## Файлы конфигурации

- `Dockerfile.optimized` - Оптимизированный образ для продакшн
- `docker-compose.yml` - Базовая конфигурация
- `docker-compose.production.yml` - Продакшн конфигурация с полным стеком
- `nginx-docker.conf` - Конфигурация Nginx для Docker
- `.env.docker` - Шаблон переменных окружения
- `docker-run.sh` - Скрипт автоматического запуска

## Быстрый старт

### 1. Подготовка

```bash
# Клонирование проекта
git clone https://github.com/ваш-username/crystal-bay-travel.git
cd crystal-bay-travel

# Запуск автоматического развертывания
./docker-run.sh
```

### 2. Настройка переменных

Отредактируйте файл `.env`:

```env
# Основные настройки
FLASK_SECRET_KEY=ваш-секретный-ключ
SAMO_OAUTH_TOKEN=ваш-samo-токен

# База данных (используется внутренний PostgreSQL)
DATABASE_URL=postgresql://crystalbay:secure_password@db:5432/crystalbay_db

# Дополнительные API ключи (опционально)
OPENAI_API_KEY=ваш-openai-ключ
TELEGRAM_BOT_TOKEN=ваш-telegram-токен
WAZZUP_API_KEY=ваш-wazzup-ключ
```

## Режимы запуска

### Разработка

```bash
docker-compose up -d
```

Включает:
- Flask приложение
- PostgreSQL база данных
- Redis для кеширования

### Продакшн

```bash
docker-compose -f docker-compose.production.yml up -d
```

Включает:
- Flask приложение с Gunicorn
- PostgreSQL база данных
- Redis для кеширования
- Nginx как reverse proxy
- Health checks для всех сервисов

## Управление контейнерами

### Основные команды

```bash
# Запуск сервисов
docker-compose up -d

# Остановка сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f web

# Просмотр статуса
docker-compose ps

# Перезапуск сервиса
docker-compose restart web

# Пересборка образов
docker-compose build --no-cache
```

### Подключение к контейнерам

```bash
# Подключение к приложению
docker-compose exec web bash

# Подключение к базе данных
docker-compose exec db psql -U crystalbay -d crystalbay_db

# Подключение к Redis
docker-compose exec redis redis-cli
```

## Мониторинг и логи

### Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Последние 100 строк
docker-compose logs --tail=100 web
```

### Health checks

```bash
# Проверка состояния всех сервисов
docker-compose ps

# Проверка health endpoint
curl http://localhost/health

# Проверка SAMO API
curl http://localhost/api/samo/test
```

## Продакшн настройки

### SSL сертификаты

1. Поместите сертификаты в папку `ssl/`:
   ```
   ssl/
   ├── cert.pem
   └── key.pem
   ```

2. Раскомментируйте SSL блок в `nginx-docker.conf`

3. Перезапустите Nginx:
   ```bash
   docker-compose restart nginx
   ```

### Backup базы данных

```bash
# Создание backup
docker-compose exec db pg_dump -U crystalbay crystalbay_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из backup
docker-compose exec -T db psql -U crystalbay crystalbay_db < backup_file.sql
```

### Обновление приложения

```bash
# Получение обновлений
git pull origin main

# Пересборка и перезапуск
docker-compose build --no-cache
docker-compose up -d
```

## Масштабирование

### Увеличение количества воркеров

В `docker-compose.production.yml`:

```yaml
web:
  deploy:
    replicas: 3
  environment:
    - GUNICORN_WORKERS=4
```

### Внешняя база данных

Для использования внешней БД (например, Amazon RDS):

```yaml
# Удалите db сервис и измените DATABASE_URL
environment:
  - DATABASE_URL=postgresql://user:pass@external-db:5432/dbname
```

## Troubleshooting

### Проблемы с запуском

```bash
# Проверка образов
docker images

# Проверка сетей
docker network ls

# Проверка volumes
docker volume ls

# Очистка системы
docker system prune -a
```

### Проблемы с базой данных

```bash
# Пересоздание базы данных
docker-compose down -v
docker-compose up -d db
docker-compose up -d web
```

### Проблемы с разрешениями

```bash
# Исправление прав на volume
docker-compose exec web chown -R crystalbay:crystalbay /app
```

## Безопасность

### Рекомендации

1. **Смените пароли по умолчанию**:
   - PostgreSQL пароль в docker-compose.yml
   - Flask SECRET_KEY в .env

2. **Ограничьте сетевой доступ**:
   - Используйте firewall для ограничения портов
   - Настройте SSL/TLS

3. **Регулярно обновляйте образы**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Мониторинг логов**:
   - Настройте централизованное логирование
   - Мониторинг аномальной активности

## Производительность

### Оптимизация

1. **Настройка PostgreSQL**:
   ```yaml
   db:
     command: postgres -c 'shared_buffers=256MB' -c 'max_connections=200'
   ```

2. **Настройка Gunicorn**:
   ```yaml
   web:
     command: gunicorn --workers 4 --worker-class gevent --worker-connections 1000
   ```

3. **Мониторинг ресурсов**:
   ```bash
   docker stats
   ```

## Дополнительные возможности

### Интеграция с CI/CD

Пример для GitHub Actions:

```yaml
- name: Deploy with Docker
  run: |
    docker-compose -f docker-compose.production.yml down
    docker-compose -f docker-compose.production.yml pull
    docker-compose -f docker-compose.production.yml up -d
```

### Мониторинг с Prometheus

Добавьте в docker-compose.yml:

```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

---

**Важно**: Всегда тестируйте изменения в development среде перед применением в production!