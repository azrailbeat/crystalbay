# Crystal Bay Travel - Руководство по развертыванию

## 🚀 Быстрое развертывание с Docker

### Шаг 1: Подготовка сервера

```bash
# Обновление системы (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt-get install docker-compose-plugin

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Проверка установки
docker --version
docker compose version
```

### Шаг 2: Клонирование и настройка проекта

```bash
# Клонирование репозитория
git clone <repository-url>
cd crystal-bay-travel

# Копирование файла конфигурации
cp .env.example .env

# Редактирование переменных окружения
nano .env  # или любой другой редактор
```

### Шаг 3: Настройка переменных окружения

Обязательно заполните в файле `.env`:

```env
# ОБЯЗАТЕЛЬНЫЕ настройки
OPENAI_API_KEY=sk-your-openai-api-key-here
TELEGRAM_BOT_TOKEN=123456789:your-telegram-bot-token-here
SESSION_SECRET=your-very-secure-random-session-key

# DATABASE (автоматически настраивается через Docker)
DATABASE_URL=postgresql://crystal_bay:crystal_bay_password@db:5432/crystal_bay_db

# ОПЦИОНАЛЬНЫЕ (можно оставить пустыми)
WAZZUP_API_KEY=your_wazzup_api_key
SAMO_OAUTH_TOKEN=your_samo_oauth_token
```

### Шаг 4: Запуск системы

```bash
# Сборка и запуск всех контейнеров
docker compose up -d

# Проверка статуса контейнеров
docker compose ps

# Просмотр логов
docker compose logs -f web
```

### Шаг 5: Проверка работы

```bash
# Проверка health check
curl http://localhost:5000/health

# Проверка основной страницы
curl http://localhost:5000

# Проверка административной панели
curl http://localhost:5000/dashboard
```

## 🌐 Настройка доменного имени и SSL

### Вариант 1: С Nginx (рекомендуется)

```bash
# Установка Nginx
sudo apt install nginx

# Создание конфигурации для сайта
sudo nano /etc/nginx/sites-available/crystalbay

# Добавьте конфигурацию:
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Активация сайта
sudo ln -s /etc/nginx/sites-available/crystalbay /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Установка SSL с Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Вариант 2: Прямой доступ через Docker

Измените в `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "80:5000"  # HTTP доступ
      - "443:5000" # HTTPS доступ (если настроен SSL в приложении)
```

## 🔧 Настройка производительности

### Конфигурация Gunicorn

Отредактируйте Dockerfile для изменения настроек Gunicorn:

```dockerfile
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \            # Количество worker'ов (обычно CPU cores * 2 + 1)
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--max-requests", "1000", \
     "--preload", \
     "--log-level", "info", \
     "main:app"]
```

### Настройка PostgreSQL

```bash
# Подключение к базе данных
docker compose exec db psql -U crystal_bay -d crystal_bay_db

# Оптимизация настроек PostgreSQL (в docker-compose.yml)
db:
  image: postgres:15-alpine
  command: |
    postgres
    -c shared_preload_libraries=pg_stat_statements
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
```

## 📊 Мониторинг и логирование

### Просмотр логов

```bash
# Логи приложения
docker compose logs -f web

# Логи базы данных
docker compose logs -f db

# Логи всех сервисов
docker compose logs -f

# Сохранение логов в файл
docker compose logs web > logs/application.log
```

### Мониторинг ресурсов

```bash
# Статистика контейнеров
docker stats

# Использование дискового пространства
docker system df

# Очистка неиспользуемых образов
docker system prune -a
```

### Настройка автоматического перезапуска

Добавьте в `docker-compose.yml`:

```yaml
services:
  web:
    restart: unless-stopped
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

## 🔒 Безопасность

### Файрвол (UFW)

```bash
# Установка и настройка UFW
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешение необходимых портов
sudo ufw allow ssh
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Проверка статуса
sudo ufw status
```

### SSL/TLS настройки

```bash
# Генерация сильных DH параметров
sudo openssl dhparam -out /etc/nginx/dhparam.pem 2048

# Добавление в конфигурацию Nginx
ssl_dhparam /etc/nginx/dhparam.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
```

### Обновления безопасности

```bash
# Регулярное обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker compose pull
docker compose up -d

# Проверка уязвимостей
docker scout quickview
```

## 💾 Резервное копирование

### Автоматическое резервное копирование базы данных

Создайте скрипт `/home/user/backup-script.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="crystal-bay-travel_db_1"

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Создание резервной копии
docker exec $CONTAINER_NAME pg_dump -U crystal_bay crystal_bay_db > $BACKUP_DIR/backup_$DATE.sql

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

echo "Backup created: backup_$DATE.sql"
```

### Настройка CRON для автоматических бэкапов

```bash
# Редактирование crontab
crontab -e

# Добавление задачи (ежедневно в 2:00)
0 2 * * * /home/user/backup-script.sh
```

### Резервное копирование файлов

```bash
# Создание архива приложения
tar -czf crystal-bay-backup-$(date +%Y%m%d).tar.gz \
    /path/to/crystal-bay-travel \
    --exclude=node_modules \
    --exclude=__pycache__ \
    --exclude=.git
```

## 🔄 Обновление системы

### Процедура обновления

```bash
# 1. Создание бэкапа перед обновлением
./backup-script.sh

# 2. Остановка контейнеров
docker compose down

# 3. Получение новой версии кода
git pull origin main

# 4. Обновление образов
docker compose build --no-cache

# 5. Запуск обновленной системы
docker compose up -d

# 6. Проверка работоспособности
curl http://localhost:5000/health
```

### Откат к предыдущей версии

```bash
# Откат кода к предыдущему коммиту
git log --oneline -n 5
git reset --hard <commit-hash>

# Пересборка и запуск
docker compose build --no-cache
docker compose up -d
```

## 🐛 Устранение неполадок

### Частые проблемы

**Проблема**: Контейнер постоянно перезапускается

```bash
# Проверка логов
docker compose logs web

# Проверка health check
docker compose exec web curl localhost:5000/health

# Проверка ресурсов
docker stats
```

**Проблема**: Ошибки подключения к базе данных

```bash
# Проверка состояния БД
docker compose exec db pg_isready -U crystal_bay

# Подключение к БД для диагностики
docker compose exec db psql -U crystal_bay -d crystal_bay_db

# Пересоздание БД (ВНИМАНИЕ: удалит все данные)
docker compose down -v
docker compose up -d
```

**Проблема**: Медленная работа системы

```bash
# Анализ производительности
docker stats
top
htop

# Оптимизация настроек в docker-compose.yml
# Увеличение памяти и CPU для контейнеров
```

### Команды для диагностики

```bash
# Информация о системе
docker info
docker compose version

# Проверка сети
docker network ls
docker compose exec web ping db

# Просмотр переменных окружения
docker compose exec web env | grep -E "(DATABASE|API_KEY)"

# Тест API эндпоинтов
curl -X GET http://localhost:5000/api/health
curl -X GET http://localhost:5000/api/samo/test
```

## 📈 Масштабирование

### Горизонтальное масштабирование

Измените `docker-compose.yml` для запуска нескольких экземпляров:

```yaml
services:
  web:
    deploy:
      replicas: 3
    ports:
      - "5000-5002:5000"
  
  nginx:
    # Настройка load balancer
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

### Вертикальное масштабирование

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

Этот файл содержит полную инструкцию по развертыванию Crystal Bay Travel системы в production окружении.