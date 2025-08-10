# Crystal Bay Travel - Installation Guide

## 🚀 Quick Installation

### Option 1: Automated Setup

1. **Clone and run the automated installer:**
```bash
git clone https://github.com/your-username/crystal-bay-travel.git
cd crystal-bay-travel
chmod +x start.sh
./start.sh
```

2. **Edit configuration when prompted:**
   - Add your SAMO OAuth token
   - Add your OpenAI API key
   - Add your Telegram bot token
   - Configure other optional services

3. **Access the application:**
   - Web Dashboard: http://localhost:5000
   - Database: PostgreSQL on localhost:5432

### Option 2: Manual Setup

1. **Prerequisites:**
   - Docker & Docker Compose installed
   - Git installed

2. **Clone repository:**
```bash
git clone https://github.com/your-username/crystal-bay-travel.git
cd crystal-bay-travel
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Edit with your configuration
```

4. **Start services:**
```bash
docker-compose up -d
```

## 🔧 Configuration

### Required Environment Variables

```env
# Database
DATABASE_URL=postgresql://crystalbay:password@db:5432/crystalbay_travel

# SAMO Travel API
SAMO_OAUTH_TOKEN=your_samo_oauth_token_here

# OpenAI for AI features
OPENAI_API_KEY=sk-your_openai_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABC-your_bot_token_here

# Flask Security
FLASK_SECRET_KEY=your-secret-key-here
```

### Optional Integrations

```env
# WhatsApp/Viber Integration
WAZZUP_API_KEY=your_wazzup_key_here

# Alternative Database (instead of PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key_here

# Email Service
SENDGRID_API_KEY=your_sendgrid_key_here
```

## 🧪 Testing Installation

1. **Access web dashboard:**
   - Go to http://localhost:5000
   - You should see the Crystal Bay Travel dashboard

2. **Test SAMO API integration:**
   - Navigate to "SAMO API & Тестирование"
   - Click "Полный тест" to test all API endpoints
   - Check curl functionality and diagnostics

3. **Verify database:**
   - Database should be accessible on localhost:5432
   - Tables will be created automatically on first run

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Stop existing services
docker-compose down
# Or change ports in docker-compose.yml
```

**Database connection issues:**
```bash
# Check database logs
docker-compose logs db
# Restart database
docker-compose restart db
```

**SAMO API 403 errors:**
- Contact SAMO support to whitelist your server IP
- Use the "IP Whitelist Test" in the dashboard
- Check your OAuth token configuration

### Getting Help

1. **Check logs:**
```bash
docker-compose logs -f web
docker-compose logs -f db
```

2. **Restart services:**
```bash
docker-compose restart
```

3. **Clean installation:**
```bash
docker-compose down -v
docker-compose up -d
```

## 🛠 Development Setup

For local development without Docker:

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r pyproject.toml
```

3. **Set up local database:**
```bash
# Using Docker for database only
docker run -d --name crystalbay-db \
  -e POSTGRES_DB=crystalbay_travel \
  -e POSTGRES_USER=crystalbay \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 postgres:13
```

4. **Run application:**
```bash
python main.py
```

## 📊 Production Deployment

For production deployment, use:

```bash
docker-compose -f docker-compose.production.yml up -d
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed production setup.