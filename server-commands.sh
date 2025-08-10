#!/bin/bash

# Crystal Bay Travel Server Setup Commands
# Выполните эти команды на сервере: 46.250.234.89

echo "🚀 Настройка Crystal Bay Travel на сервере..."

# 1. Переход в директорию проекта
cd /root/cbay/crystalbay/

# 2. Создание оптимизированного Dockerfile
cat > Dockerfile.optimized << 'EOF'
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_production.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_production.txt

COPY . .

RUN useradd -m -s /bin/bash crystalbay && \
    chown -R crystalbay:crystalbay /app
USER crystalbay

RUN mkdir -p /app/static/uploads /app/logs

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "main:app"]
EOF

# 3. Создание requirements_production.txt
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

# 4. Создание production docker-compose
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile.optimized
    ports:
      - "80:80"
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
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U crystalbay -d crystalbay_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  static_files:
  app_logs:
  redis_data:
EOF

# 5. Создание .env файла
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

# 6. Создание скрипта запуска
cat > docker-run.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Запуск Crystal Bay Travel..."

if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    exit 1
fi

echo "🛑 Остановка существующих контейнеров..."
docker-compose -f docker-compose.production.yml down || true

echo "🔨 Сборка образов..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.production.yml up -d

echo "⏳ Ожидание запуска..."
sleep 30

echo "🔍 Проверка состояния..."
docker-compose -f docker-compose.production.yml ps

if curl -s http://localhost/health > /dev/null; then
    echo "✅ Приложение запущено!"
    echo "🌐 Доступно: http://46.250.234.89"
else
    echo "❌ Ошибка запуска"
    docker-compose -f docker-compose.production.yml logs web
fi
EOF

# 7. Создание скрипта обновления
cat > update-app.sh << 'EOF'
#!/bin/bash
set -e

echo "🔄 Обновление приложения..."

# Backup
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose -f docker-compose.production.yml exec -T db pg_dump -U crystalbay crystalbay_db > $BACKUP_FILE || true

# Git update
git pull origin main

# Restart
docker-compose -f docker-compose.production.yml build --no-cache web
docker-compose -f docker-compose.production.yml up -d

sleep 15
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Обновление завершено!"
else
    echo "❌ Ошибка обновления"
fi
EOF

# 8. Установка прав на выполнение
chmod +x docker-run.sh
chmod +x update-app.sh

echo ""
echo "📝 Файлы созданы. Следующие шаги:"
echo ""
echo "1. Установите Docker (если не установлен):"
echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
echo "   sudo sh get-docker.sh"
echo "   sudo apt install docker-compose -y"
echo ""
echo "2. Отредактируйте .env файл с вашими ключами:"
echo "   nano .env"
echo ""
echo "3. Сгенерируйте секретный ключ:"
echo "   python3 -c \"import secrets; print(secrets.token_hex(32))\""
echo ""
echo "4. Запустите приложение:"
echo "   ./docker-run.sh"
echo ""
echo "5. Для обновлений из Git:"
echo "   ./update-app.sh"
echo ""
echo "🌐 Приложение будет доступно на: http://46.250.234.89"
echo "⚠️  Не забудьте добавить IP 46.250.234.89 в SAMO whitelist!"