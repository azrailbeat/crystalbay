# Настройка сервера для Crystal Bay Travel

## Текущий статус сервера

**IP:** 46.250.234.89  
**OS:** Ubuntu 20.04.6 LTS  
**Проект:** `/root/cbay/crystalbay/`

## 1. Обновление проекта до последней версии

На сервере выполните:

```bash
cd /root/cbay/crystalbay/
git pull origin main
```

**Примечание:** В текущем проекте отсутствуют новые Docker файлы. Создадим их:

```bash
# Создание оптимизированного Dockerfile
cat > Dockerfile.optimized << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_production.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_production.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -s /bin/bash crystalbay && \
    chown -R crystalbay:crystalbay /app && \
    chmod +x /app/deploy.sh || true
USER crystalbay

# Create necessary directories
RUN mkdir -p /app/static/uploads /app/logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--preload", "main:app"]
EOF

# Создание production requirements
cat > requirements_production.txt << 'EOF'
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
email-validator==2.1.0
notion-client==2.2.1
openai==1.3.7
python-http-client==3.3.7
sendgrid==6.10.0
supabase==2.0.2
python-telegram-bot==20.7
telegram==0.0.1
trafilatura==1.6.4
EOF
```

## 2. Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt update
sudo apt install docker-compose -y

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Запуск Docker
sudo systemctl start docker
sudo systemctl enable docker
```

## 3. Создание файла переменных окружения

```bash
cd /root/cbay/crystalbay/

# Создание .env файла
cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=ИЗМЕНИТЕ_НА_БЕЗОПАСНЫЙ_КЛЮЧ_32_СИМВОЛА

# Database Configuration
DATABASE_URL=postgresql://crystalbay:secure_password@db:5432/crystalbay_db

# SAMO API Configuration - ОБЯЗАТЕЛЬНО НАСТРОЙТЕ
SAMO_OAUTH_TOKEN=ВАШ_SAMO_OAUTH_TOKEN

# OpenAI Configuration (optional)
OPENAI_API_KEY=ВАШ_OPENAI_API_KEY

# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN=ВАШ_TELEGRAM_BOT_TOKEN

# Wazzup24 API Configuration (optional)
WAZZUP_API_KEY=ВАШ_WAZZUP_API_KEY

# Supabase Configuration (optional)
SUPABASE_URL=ВАШ_SUPABASE_URL
SUPABASE_KEY=ВАШ_SUPABASE_KEY
EOF

echo "Файл .env создан. ОБЯЗАТЕЛЬНО отредактируйте его с вашими ключами!"
```

## 4. Создание production docker-compose

```bash
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile.optimized
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://crystalbay:secure_password@db:5432/crystalbay_db
      - FLASK_ENV=production
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - SAMO_OAUTH_TOKEN=${SAMO_OAUTH_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - WAZZUP_API_KEY=${WAZZUP_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - static_files:/app/static
      - app_logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: crystalbay_db
      POSTGRES_USER: crystalbay
      POSTGRES_PASSWORD: secure_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U crystalbay -d crystalbay_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-docker.conf:/etc/nginx/conf.d/default.conf
      - static_files:/app/static:ro
    depends_on:
      web:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  static_files:
  app_logs:
  redis_data:
EOF
```

## 5. Создание Nginx конфигурации

```bash
cat > nginx-docker.conf << 'EOF'
upstream app {
    server web:5000;
}

server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # File upload limit
    client_max_body_size 100M;
    
    # Main application
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias /app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://app/health;
        access_log off;
    }
    
    # Logging
    access_log /var/log/nginx/crystalbay_access.log;
    error_log /var/log/nginx/crystalbay_error.log;
}
EOF
```

## 6. Создание скрипта запуска

```bash
cat > docker-run.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 Запуск Crystal Bay Travel в Docker..."

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден! Создайте его с вашими настройками."
    exit 1
fi

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose -f docker-compose.production.yml down || true

# Сборка образов
echo "🔨 Сборка Docker образов..."
docker-compose -f docker-compose.production.yml build --no-cache

# Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.production.yml up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 30

# Проверка состояния
echo "🔍 Проверка состояния сервисов..."
docker-compose -f docker-compose.production.yml ps

# Проверка приложения
echo "🧪 Проверка приложения..."
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Приложение успешно запущено!"
    echo "🌐 Доступно по адресу: http://46.250.234.89"
    echo "📊 Health check: http://46.250.234.89/health"
    echo "🔧 SAMO API тест: http://46.250.234.89/samo-testing"
else
    echo "❌ Приложение не отвечает на health check"
    docker-compose -f docker-compose.production.yml logs web
fi

echo ""
echo "📋 Полезные команды:"
echo "Просмотр логов: docker-compose -f docker-compose.production.yml logs -f"
echo "Остановка:      docker-compose -f docker-compose.production.yml down"
echo "Перезапуск:     docker-compose -f docker-compose.production.yml restart"
EOF

chmod +x docker-run.sh
```

## 7. Настройка переменных окружения

```bash
# Отредактируйте .env файл
nano .env
```

**Обязательно настройте:**

1. **FLASK_SECRET_KEY** - сгенерируйте безопасный ключ:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **SAMO_OAUTH_TOKEN** - ваш токен от SAMO API

3. **Другие API ключи** по необходимости

## 8. Запуск приложения

```bash
# Запуск Docker контейнеров
./docker-run.sh

# Проверка статуса
docker-compose -f docker-compose.production.yml ps

# Просмотр логов
docker-compose -f docker-compose.production.yml logs -f web
```

## 9. Настройка IP Whitelist для SAMO API

**Важно:** Добавьте IP `46.250.234.89` в whitelist SAMO API:

1. Свяжитесь с технической поддержкой SAMO
2. Предоставите IP адрес: `46.250.234.89`
3. Укажите, что это для Crystal Bay Travel integration

## 10. Автоматическое обновление из Git

Создайте скрипт для обновлений:

```bash
cat > update-app.sh << 'EOF'
#!/bin/bash

set -e

echo "🔄 Обновление Crystal Bay Travel..."

# Создание backup
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
echo "💾 Создание backup..."
docker-compose -f docker-compose.production.yml exec -T db pg_dump -U crystalbay crystalbay_db > $BACKUP_FILE
echo "Backup создан: $BACKUP_FILE"

# Получение обновлений
echo "📥 Получение обновлений из Git..."
git pull origin main

# Перезапуск приложения
echo "🔄 Перезапуск приложения..."
docker-compose -f docker-compose.production.yml build --no-cache web
docker-compose -f docker-compose.production.yml up -d

# Проверка
sleep 15
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Обновление завершено успешно!"
    echo "🌐 Приложение доступно: http://46.250.234.89"
else
    echo "❌ Ошибка после обновления, проверьте логи:"
    docker-compose -f docker-compose.production.yml logs web
fi
EOF

chmod +x update-app.sh
```

## 11. Firewall настройки

```bash
# Настройка UFW firewall
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## 12. Проверка работы

После запуска проверьте:

- **Приложение:** http://46.250.234.89
- **Health check:** http://46.250.234.89/health
- **SAMO API тест:** http://46.250.234.89/samo-testing

## Команды для управления

```bash
# Запуск
./docker-run.sh

# Обновление из Git
./update-app.sh

# Остановка
docker-compose -f docker-compose.production.yml down

# Просмотр логов
docker-compose -f docker-compose.production.yml logs -f

# Backup базы данных
docker-compose -f docker-compose.production.yml exec -T db pg_dump -U crystalbay crystalbay_db > backup.sql

# Статус сервисов
docker-compose -f docker-compose.production.yml ps
```

---

**Следующие шаги:**
1. Выполните команды по порядку на сервере
2. Настройте переменные в .env файле
3. Запустите приложение через ./docker-run.sh
4. Обратитесь в SAMO для добавления IP в whitelist