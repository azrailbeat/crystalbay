# Crystal Bay Travel - Complete Deployment Guide

## 🚀 Quick Start Options

### Option 1: One-Command Installation (Recommended)
```bash
git clone https://github.com/azrailbeat/crystalbay.git && cd crystalbay && chmod +x start.sh && ./start.sh
```

### Option 2: Step-by-Step Installation
```bash
# 1. Clone repository
git clone https://github.com/azrailbeat/crystalbay.git
cd crystalbay

# 2. Setup environment
cp .env.example .env
# Edit .env with your settings (see Environment Setup below)

# 3. Install and run
chmod +x start.sh
./start.sh
```

## ⚙️ Environment Setup (.env Configuration)

Copy `.env.example` to `.env` and configure with your actual values:

```env
# Database Configuration (Required)
DATABASE_URL=postgresql://neondb_owner:npg_Y4g4VaRYSjnv@ep-weathered-glade-a25ajc8n.eu-central-1.aws.neon.tech/neondb?sslmode=require
PGHOST=ep-weathered-glade-a25ajc8n.eu-central-1.aws.neon.tech
PGPORT=5432
PGUSER=neondb_owner
PGPASSWORD=npg_Y4g4VaRYSjnv
PGDATABASE=neondb

# SAMO Travel API (Required for booking features)
SAMO_OAUTH_TOKEN=27bd59a7ac67422189789f0188167379

# OpenAI Integration (Required for AI features)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Wazzup24 Integration (Optional)
WAZZUP_API_KEY=your-wazzup-api-key

# Supabase (Alternative database option)
SUPABASE_URL=https://cfaxdmgpoxclmhzpbvqo.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmYXhkbWdwb3hjbG1oenBidnFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjE3MzY3NzQsImV4cCI6MjAzNzMxMjc3NH0.0

# Flask Configuration
FLASK_SECRET_KEY=crystal-bay-travel-production-secret-2025
FLASK_ENV=development
DEBUG=True
```

## 🎯 API Keys Setup Guide

### 1. Database Setup (Neon DB)
1. Visit [neon.tech](https://neon.tech) and create account
2. Create new project
3. Copy connection string to `DATABASE_URL`

### 2. SAMO Travel API
1. Contact SAMO support for API access
2. Request IP whitelisting for your server
3. Obtain OAuth token and set `SAMO_OAUTH_TOKEN`

### 3. OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Go to API Keys section
3. Create new secret key
4. Set `OPENAI_API_KEY`

### 4. Telegram Bot (Optional)
1. Message [@BotFather](https://t.me/botfather)
2. Use `/newbot` to create bot
3. Copy token to `TELEGRAM_BOT_TOKEN`

## 🐳 Docker Deployment

### Development Mode
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Production Mode
```bash
# Production deployment
docker-compose -f docker-compose.production.yml up -d

# Monitor production logs
docker-compose -f docker-compose.production.yml logs -f

# Scale for high traffic
docker-compose -f docker-compose.production.yml up -d --scale web=3
```

## 🌐 Server Deployment (Production)

### Automated Production Deployment
```bash
# For Ubuntu/CentOS servers
chmod +x production_deploy.sh
sudo ./production_deploy.sh
```

### Manual Production Setup
```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Clone and deploy
git clone https://github.com/azrailbeat/crystalbay.git
cd crystalbay
cp .env.example .env
# Edit .env with production values
docker-compose -f docker-compose.production.yml up -d
```

## 🔧 Testing and Verification

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# SAMO API connectivity
curl http://localhost:5000/api/samo/currencies

# Database connection
curl http://localhost:5000/api/health/database
```

### Web Interface Access
- **Dashboard**: http://localhost:5000
- **Lead Management**: http://localhost:5000/leads  
- **Tour Search**: http://localhost:5000/tours
- **SAMO Testing**: http://localhost:5000/samo-testing
- **Settings**: http://localhost:5000/unified-settings

## 🛠️ Development Setup

### Local Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
export FLASK_ENV=development
export DEBUG=True
python main.py
```

### Code Quality Checks
```bash
# Python compilation test
python -m py_compile main.py
python -m py_compile samo_api_routes.py
python -m py_compile crystal_bay_samo_api.py

# Import tests
python -c "import main; print('Main module OK')"
python -c "import models; print('Models module OK')"
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. SAMO API 403 Error
**Issue**: API returns "403 Forbidden"
**Solution**: 
- Contact SAMO support for IP whitelisting
- Verify `SAMO_OAUTH_TOKEN` is correct
- Check server IP with: `curl ifconfig.me`

#### 2. Database Connection Failed
**Issue**: Cannot connect to PostgreSQL
**Solution**:
- Verify `DATABASE_URL` format
- Check database server status
- Test connection: `psql $DATABASE_URL`

#### 3. Port 5000 Already in Use
**Issue**: "Address already in use"
**Solution**:
```bash
# Find and kill process
sudo lsof -i :5000
sudo kill -9 <PID>

# Or use different port
export PORT=5001
python main.py
```

#### 4. Virtual Environment Issues
**Issue**: "No module named 'flask'"
**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Docker Build Failures
**Issue**: Docker build fails
**Solution**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check requirements.txt exists
ls -la requirements.txt
```

### Debug Commands
```bash
# Check Python version
python3 --version

# Verify dependencies
pip list | grep -E "(flask|requests|openai)"

# Test environment variables
python -c "import os; print('DB:', bool(os.getenv('DATABASE_URL')))"

# Check disk space
df -h

# Memory usage
free -h
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, CentOS 7+, macOS 10.15+
- **Python**: 3.11+
- **Memory**: 512 MB RAM
- **Storage**: 1 GB available space
- **Network**: Internet connection

### Recommended (Production)
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **Memory**: 2+ GB RAM
- **Storage**: 10+ GB SSD
- **Network**: 1 Gbps connection
- **SSL**: Valid certificate for HTTPS

## 🚀 Performance Optimization

### Production Optimizations
```bash
# Enable production mode
export FLASK_ENV=production
export DEBUG=False

# Use production WSGI server
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app

# Database connection pooling
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=30
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install psutil

# Monitor resources
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"

# Log monitoring
tail -f /var/log/crystalbay/app.log
```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
docker-compose restart
```

### Backup Procedures
```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Full project backup
tar -czf crystalbay_backup_$(date +%Y%m%d).tar.gz .
```

---

## ✅ Success Indicators

Your installation is successful when:

1. **Health endpoint returns 200**: `curl http://localhost:5000/health`
2. **Dashboard loads**: Open http://localhost:5000 in browser
3. **No Python errors**: All modules import successfully
4. **SAMO API responds**: Even 403 is OK (means connection works)
5. **Database connected**: No connection errors in logs

## 🆘 Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `install.md` for detailed steps
- **Server Issues**: See `SERVER_SETUP_COMMANDS.md` for production fixes

**Ready for deployment!** 🎉