# Crystal Bay Travel - Полное руководство по Docker

## Обзор

Docker контейнеризация обеспечивает простое и надежное развертывание системы Crystal Bay Travel на любом сервере. Все зависимости, база данных и веб-сервер упакованы в контейнеры для максимальной портабильности.

## Преимущества Docker развертывания

- ✅ Изолированная среда выполнения
- ✅ Автоматическое управление зависимостями
- ✅ Простое масштабирование
- ✅ Встроенные health checks
- ✅ Автоматические backup и восстановление
- ✅ Reverse proxy с SSL поддержкой

## Файлы конфигурации

- `Dockerfile.optimized` - Оптимизированный образ для продакшн
- `docker-compose.yml` - Базовая конфигурация
- `docker-compose.production.yml` - Продакшн конфигурация с полным стеком
- `nginx-docker.conf` - Конфигурация Nginx для Docker
- `.env.docker` - Шаблон переменных окружения
- `docker-run.sh` - Скрипт автоматического запуска

## Системные требования

- **Docker**: версия 20.10+
- **Docker Compose**: версия 2.0+
- **Память**: минимум 4GB RAM
- **Диск**: минимум 10GB свободного места
- **Сеть**: открытые порты 80, 443 (для продакшн)

## Быстрый старт

### 1. Установка Docker (если не установлен)

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL:**
```bash
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. Подготовка проекта

```bash
# Клонирование проекта
git clone https://github.com/ваш-username/crystal-bay-travel.git
cd crystal-bay-travel

# Проверка файлов
ls -la docker*
# Должны быть: Dockerfile.optimized, docker-compose.yml, docker-run.sh

# Запуск автоматического развертывания
chmod +x docker-run.sh
./docker-run.sh
```

### 3. Настройка переменных окружения

Скрипт автоматически создаст файл `.env` из шаблона. Отредактируйте его:

```bash
nano .env
```

**Обязательные настройки:**
```env
# Безопасность - ОБЯЗАТЕЛЬНО ИЗМЕНИТЕ
FLASK_SECRET_KEY=ваш-уникальный-секретный-ключ-32-символа

# SAMO API - основной функционал
SAMO_OAUTH_TOKEN=ваш-samo-oauth-токен

# База данных (оставьте как есть для Docker)
DATABASE_URL=postgresql://crystalbay:secure_password@db:5432/crystalbay_db
```

**Дополнительные API (опционально):**
```env
# OpenAI для AI функций
OPENAI_API_KEY=sk-ваш-openai-ключ

# Telegram бот
TELEGRAM_BOT_TOKEN=ваш-telegram-токен

# Wazzup24 мессенджер
WAZZUP_API_KEY=ваш-wazzup-ключ

# SendGrid для email
SENDGRID_API_KEY=ваш-sendgrid-ключ

# Notion интеграция
NOTION_INTEGRATION_SECRET=ваш-notion-секрет
NOTION_DATABASE_ID=ваш-notion-database-id
```

**Генерация секретного ключа:**
```bash
# Python способ
python3 -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL способ
openssl rand -hex 32
```

## Режимы запуска

### Режим разработки

```bash
# Простой запуск для тестирования
docker-compose up -d

# Просмотр логов в реальном времени
docker-compose logs -f
```

**Включает:**
- Flask приложение (порт 5000)
- PostgreSQL база данных
- Redis для кеширования
- Автоматическая перезагрузка при изменениях

**Доступ:** http://localhost:5000

### Режим продакшн (рекомендуется)

```bash
# Полный продакшн стек
docker-compose -f docker-compose.production.yml up -d

# Проверка статуса всех сервисов
docker-compose -f docker-compose.production.yml ps
```

**Включает:**
- Flask приложение с Gunicorn (3 воркера)
- PostgreSQL база данных с оптимизацией
- Redis для кеширования и сессий
- Nginx reverse proxy (порты 80, 443)
- Health checks для всех сервисов
- Автоматические restart политики

**Доступ:** http://localhost (или ваш домен)

### Быстрый продакшн запуск

```bash
# Все в одной команде
./docker-run.sh
# Выберите: 2) Продакшн режим
```

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

### Health checks и мониторинг

```bash
# Проверка состояния всех сервисов
docker-compose -f docker-compose.production.yml ps

# Детальная информация о здоровье
docker-compose -f docker-compose.production.yml exec web curl -f http://localhost:5000/health

# Проверка через веб-браузер
curl -s http://localhost/health | jq .

# Проверка SAMO API подключения
curl -s http://localhost/api/samo/test

# Мониторинг ресурсов
docker stats

# Проверка логов на ошибки
docker-compose logs web | grep ERROR
```

**Пример успешного ответа health check:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-10T09:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "samo_api": "configured"
  }
}
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

### Backup и восстановление

**Создание backup:**
```bash
# Автоматический backup с датой
BACKUP_FILE="backup_crystalbay_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T db pg_dump -U crystalbay crystalbay_db > $BACKUP_FILE
echo "Backup создан: $BACKUP_FILE"

# Backup с сжатием
docker-compose exec -T db pg_dump -U crystalbay crystalbay_db | gzip > backup_crystalbay_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Восстановление из backup:**
```bash
# Остановка приложения
docker-compose down

# Запуск только базы данных
docker-compose up -d db
sleep 10

# Восстановление
docker-compose exec -T db psql -U crystalbay crystalbay_db < backup_file.sql

# Или из сжатого backup
gunzip < backup_file.sql.gz | docker-compose exec -T db psql -U crystalbay crystalbay_db

# Запуск всех сервисов
docker-compose up -d
```

**Автоматический backup (cron):**
```bash
# Добавить в crontab (crontab -e)
0 2 * * * cd /path/to/crystal-bay-travel && docker-compose exec -T db pg_dump -U crystalbay crystalbay_db | gzip > backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### Обновление приложения

**Простое обновление (без изменения Docker конфигурации):**
```bash
# Получение обновлений
git pull origin main

# Пересборка только приложения
docker-compose build --no-cache web

# Перезапуск приложения (база данных останется работать)
docker-compose up -d
```

**Полное обновление (с изменениями Docker конфигурации):**
```bash
# Создание backup перед обновлением
BACKUP_FILE="backup_before_update_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T db pg_dump -U crystalbay crystalbay_db > $BACKUP_FILE

# Получение обновлений
git pull origin main

# Остановка всех сервисов
docker-compose down

# Удаление старых образов (опционально)
docker image prune -f

# Пересборка всех образов
docker-compose build --no-cache

# Запуск обновленной системы
docker-compose -f docker-compose.production.yml up -d

# Проверка успешного запуска
sleep 30
docker-compose ps
curl -s http://localhost/health
```

**Zero-downtime обновление (для продакшн):**
```bash
# Запуск новой версии на другом порту
sed 's/80:80/8080:80/' docker-compose.production.yml > docker-compose.update.yml
docker-compose -f docker-compose.update.yml up -d

# Проверка новой версии
curl -s http://localhost:8080/health

# Переключение трафика (через nginx или load balancer)
# Остановка старой версии
docker-compose down

# Переименование конфигураций
mv docker-compose.update.yml docker-compose.production.yml
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

## Решение проблем (Troubleshooting)

### Проблемы с запуском

**Диагностика:**
```bash
# Проверка статуса Docker
systemctl status docker

# Проверка доступных ресурсов
docker system df
free -h
df -h

# Проверка сетей и volumes
docker network ls
docker volume ls
docker images

# Проверка запущенных контейнеров
docker ps -a
```

**Решение:**
```bash
# Полная очистка и перезапуск
docker-compose down -v  # Удалит данные!
docker system prune -a -f
docker volume prune -f

# Пересборка с нуля
./docker-run.sh
```

### Проблемы с базой данных

**Симптомы:** Ошибки подключения к PostgreSQL

**Диагностика:**
```bash
# Проверка логов базы данных
docker-compose logs db

# Проверка состояния контейнера
docker-compose exec db pg_isready -U crystalbay

# Проверка подключения изнутри
docker-compose exec web python3 -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

**Решение:**
```bash
# Пересоздание базы данных
docker-compose down
docker volume rm crystalbay_postgres_data  # Удалит все данные!
docker-compose up -d db
sleep 15
docker-compose up -d
```

### Проблемы с SAMO API

**Симптомы:** 403 Forbidden ошибки

**Диагностика:**
```bash
# Проверка переменных окружения
docker-compose exec web env | grep SAMO

# Тестирование подключения
docker-compose exec web curl -H "Authorization: Bearer $SAMO_OAUTH_TOKEN" https://api.samo-tours.ru/v1/test

# Проверка IP адреса сервера
curl ifconfig.me
```

**Решение:**
1. Убедитесь, что IP сервера добавлен в whitelist SAMO
2. Проверьте корректность SAMO_OAUTH_TOKEN
3. Свяжитесь с поддержкой SAMO для добавления IP

### Проблемы с производительностью

**Диагностика:**
```bash
# Мониторинг ресурсов
docker stats --no-stream

# Проверка логов на медленные запросы
docker-compose logs web | grep -i "slow\|timeout\|error"

# Проверка использования диска
docker system df
```

**Решение:**
```bash
# Увеличение ресурсов для контейнеров
# В docker-compose.yml добавить:
# deploy:
#   resources:
#     limits:
#       memory: 2G
#       cpus: '1.0'

# Оптимизация PostgreSQL
docker-compose exec db psql -U crystalbay -d crystalbay_db -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public';
"
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

## Чек-лист для продакшн развертывания

**Перед запуском:**
- [ ] Сервер соответствует системным требованиям
- [ ] Docker и Docker Compose установлены
- [ ] Настроены все переменные в .env файле
- [ ] SAMO_OAUTH_TOKEN получен и IP добавлен в whitelist
- [ ] Firewall настроен (порты 80, 443 открыты)
- [ ] SSL сертификаты подготовлены (для HTTPS)

**После запуска:**
- [ ] Все сервисы запущены (docker-compose ps)
- [ ] Health check возвращает успешный ответ
- [ ] SAMO API тестирование проходит успешно
- [ ] Настроены автоматические backup
- [ ] Мониторинг настроен
- [ ] DNS записи указывают на сервер

**Безопасность:**
- [ ] Изменены все пароли по умолчанию
- [ ] Firewall настроен корректно
- [ ] SSL/TLS сертификаты установлены
- [ ] Логирование настроено
- [ ] Регулярные обновления запланированы

## Полезные ссылки

- **Админ панель:** http://your-domain/
- **Health check:** http://your-domain/health
- **SAMO тестирование:** http://your-domain/samo-testing
- **API документация:** http://your-domain/api/docs
- **Логи приложения:** `docker-compose logs -f web`
- **Логи базы данных:** `docker-compose logs -f db`

## Поддержка

**При возникновении проблем:**

1. **Проверьте логи:** `docker-compose logs -f`
2. **Проверьте health check:** `curl http://localhost/health`
3. **Проверьте переменные окружения:** `docker-compose exec web env`
4. **Создайте backup перед изменениями**
5. **Обратитесь к этой документации**

**Контакты поддержки:**
- SAMO API: техподдержка SAMO tours
- Docker вопросы: официальная документация Docker
- Вопросы по приложению: разработчики Crystal Bay Travel

---

**⚠️ Важно**: Всегда тестируйте изменения в development среде перед применением в production!

**📋 Помните**: Регулярно создавайте backup и обновляйте систему для безопасности.