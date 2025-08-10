# Crystal Bay Travel - Production Server Setup Commands

## 🚀 Quick Production Deployment

### Команды для выполнения на сервере 46.250.234.89:

```bash
# 1. Остановить существующие контейнеры
docker-compose -f docker-compose.production.yml down

# 2. Исправить Dockerfile в production конфигурации
nano docker-compose.production.yml
# Изменить: dockerfile: Dockerfile.optimized
# На: dockerfile: Dockerfile.production

# 3. Создать файл requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
supabase==1.0.4
requests==2.31.0
python-telegram-bot==20.5
openai==0.28.0
notion-client==2.0.0
sendgrid==6.10.0
python-dotenv==1.0.0
trafilatura==1.6.2
email-validator==2.0.0
python-http-client==3.3.7
EOF

# 4. Обновить Dockerfile.production для использования requirements.txt
nano Dockerfile.production
# Убедиться что есть строка: COPY requirements.txt .
# И строка: RUN pip install --no-cache-dir -r requirements.txt

# 5. Собрать и запустить контейнеры
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# 6. Проверить статус
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs web
```

## 🔧 Alternative: Simple Docker Build

Если production compose сложный, можно использовать простую сборку:

```bash
# 1. Собрать образ напрямую
docker build -f Dockerfile.production -t crystal-bay-travel .

# 2. Запустить контейнер с базой данных
docker run -d --name crystalbay-db \
  -e POSTGRES_DB=crystalbay_travel \
  -e POSTGRES_USER=crystalbay \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5433:5432 \
  postgres:15-alpine

# 3. Запустить приложение
docker run -d --name crystalbay-web \
  --link crystalbay-db:db \
  -p 5000:5000 \
  --env-file .env \
  crystal-bay-travel

# 4. Проверить
curl http://localhost:5000
```

## 📋 Environment File for Production

Создать файл `.env` на сервере:

```env
# Database
DATABASE_URL=postgresql://neondb_owner:npg_Y4g4VaRYSjnv@ep-weathered-glade-a25ajc8n.eu-central-1.aws.neon.tech/neondb?sslmode=require
PGHOST=ep-weathered-glade-a25ajc8n.eu-central-1.aws.neon.tech
PGPORT=5432
PGUSER=neondb_owner
PGPASSWORD=npg_Y4g4VaRYSjnv
PGDATABASE=neondb

# API Keys
SAMO_OAUTH_TOKEN=27bd59a7ac67422189789f0188167379
OPENAI_API_KEY=sk-proj-xSEofqA4GyVGwNHDLiLFnFHmNjvXCfrOjvyF3b7GKUL5pqUFZ0Y2jG2iEKGT3BlbkFJPv7EHh8fPHBUhTKZYAILb6e6Rh8GNL2Nm9BHKv2c
TELEGRAM_BOT_TOKEN=7234567890:AAHl7T-K9xQ2rN3mA5bC8dE9fG0hI1jK2lM3nO4pQ5r
WAZZUP_API_KEY=your_wazzup_key

# Supabase
SUPABASE_URL=https://cfaxdmgpoxclmhzpbvqo.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmYXhkbWdwb3hjbG1oenBidnFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjE3MzY3NzQsImV4cCI6MjAzNzMxMjc3NH0.0

# Flask
FLASK_SECRET_KEY=crystal-bay-travel-production-secret-2025
FLASK_ENV=production
DEBUG=False
```

## 🧪 Testing After Deployment

```bash
# 1. Проверить статус сервисов
docker-compose -f docker-compose.production.yml ps

# 2. Проверить логи
docker-compose -f docker-compose.production.yml logs web
docker-compose -f docker-compose.production.yml logs db

# 3. Проверить приложение
curl http://46.250.234.89:5000
curl http://46.250.234.89:5000/health

# 4. Тест SAMO API
curl -X GET http://46.250.234.89:5000/api/samo/currencies
```

## 🔥 Quick Fix Commands

Если что-то пошло не так:

```bash
# Остановить все
docker-compose -f docker-compose.production.yml down

# Очистить контейнеры и образы
docker system prune -a

# Перезапустить
docker-compose -f docker-compose.production.yml up -d --build

# Посмотреть что происходит
docker-compose -f docker-compose.production.yml logs -f
```

## ✅ Success Indicators

Система работает правильно если:

- ✅ `docker-compose ps` показывает все сервисы "Up"
- ✅ `curl http://46.250.234.89:5000` возвращает HTML страницу
- ✅ Логи не показывают критических ошибок
- ✅ SAMO API тестирование работает в веб-интерфейсе