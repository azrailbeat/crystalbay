#!/usr/bin/env python3
"""
Crystal Bay Travel - Production Cleanup Script
Полная очистка проекта от всех заглушек и тестовых данных
"""

import os
import shutil
import json
from pathlib import Path

def clean_test_files():
    """Удаление всех тестовых файлов и заглушек"""
    
    # Файлы для удаления
    files_to_remove = [
        'clean_data.py',
        'comprehensive_system_analysis_report.md',
        'priority_fixes_plan.md',
        'tinyproxy_setup.md',
        'vps_script_solution.md',
        'vps_setup_guide.md',
        'crystal_bay.log',
        'settings.json',
        'main_production.py'
    ]
    
    # Директории для очистки
    dirs_to_clean = [
        'data',
        'logs',
        'backup'
    ]
    
    print("🧹 Очистка тестовых файлов...")
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  ❌ Удален: {file_path}")
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            print(f"  ❌ Удалена директория: {dir_path}")
    
    # Очистка Python cache
    for cache_file in Path('.').rglob('*.pyc'):
        cache_file.unlink()
    
    for cache_dir in Path('.').rglob('__pycache__'):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)

def clean_database_configs():
    """Очистка всех заглушек базы данных"""
    
    print("🗄️ Очистка заглушек базы данных...")
    
    # Очистка app_api.py от тестовых данных
    app_api_content = """import logging
from flask import request, jsonify
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def register_api_routes(app):
    \"\"\"Register all API routes for the application\"\"\"
    
    @app.route('/api/leads', methods=['GET'])
    def api_get_leads():
        \"\"\"Get all leads from database\"\"\"
        try:
            from models import LeadService
            lead_service = LeadService()
            leads = lead_service.get_leads(limit=request.args.get('limit', 50, type=int))
            
            return jsonify({
                'success': True,
                'leads': leads,
                'count': len(leads)
            })
        except Exception as e:
            logger.error(f"API get leads error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/leads', methods=['POST'])
    def api_create_lead():
        \"\"\"Create new lead\"\"\"
        try:
            data = request.get_json() or {}
            
            if not data.get('name') or not data.get('phone'):
                return jsonify({
                    'success': False,
                    'error': 'Name and phone are required'
                }), 400
            
            from models import LeadService
            lead_service = LeadService()
            
            lead_data = {
                'name': data['name'],
                'phone': data['phone'],
                'email': data.get('email'),
                'source': data.get('source', 'api'),
                'notes': data.get('notes'),
                'tour_interest': data.get('tour_interest'),
                'budget_range': data.get('budget_range')
            }
            lead_id = lead_service.create_lead(lead_data)
            
            return jsonify({
                'success': True,
                'lead_id': lead_id,
                'message': 'Lead created successfully'
            })
            
        except Exception as e:
            logger.error(f"API create lead error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    logger.info("API routes registered successfully")
"""
    
    with open('app_api.py', 'w', encoding='utf-8') as f:
        f.write(app_api_content)
    
    print("  ✅ app_api.py очищен от заглушек")

def create_production_env():
    """Создание чистого .env.production"""
    
    env_content = """# Crystal Bay Travel - Production Environment
# ================================================
# Заполните реальными значениями перед развертыванием

# Database (Required)
DATABASE_URL=postgresql://username:password@localhost:5432/crystal_bay_travel

# Flask Configuration (Required)
FLASK_ENV=production
SESSION_SECRET=your-super-secure-session-secret-change-this-to-random-string

# Core API Keys (Required)
OPENAI_API_KEY=sk-your-openai-api-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
WAZZUP_API_KEY=your-wazzup24-api-key

# SAMO Travel API (Required for tour bookings)
SAMO_OAUTH_TOKEN=your-samo-api-oauth-token

# Optional Integrations
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SENDGRID_API_KEY=SG.your-sendgrid-api-key
BITRIX_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/webhook/url
BITRIX_USER_ID=1

# Notion Integration (Optional)
NOTION_INTEGRATION_SECRET=secret_your-notion-secret
NOTION_DATABASE_ID=your-notion-database-id
"""
    
    with open('.env.production', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("📝 Создан чистый .env.production")

def create_github_files():
    """Создание файлов для GitHub"""
    
    # README.md
    readme_content = """# Crystal Bay Travel - Multi-Channel Booking System

Professional travel booking and customer management system with AI-powered features.

## Features

- 🎯 **Kanban Lead Management** - Visual drag & drop interface
- 🤖 **AI Customer Service** - OpenAI-powered automated responses  
- 📱 **Multi-Channel Integration** - Telegram, Wazzup24, Email
- 🏖️ **SAMO Travel API** - Real-time tour booking and inventory
- 📊 **Analytics Dashboard** - Lead tracking and performance metrics
- 🔗 **CRM Integration** - Bitrix24 and Notion support

## Tech Stack

- **Backend**: Python Flask, PostgreSQL, Redis
- **Frontend**: Bootstrap 5, Vanilla JS
- **AI**: OpenAI GPT-4o
- **APIs**: SAMO Travel, Wazzup24, Telegram Bot API
- **Deployment**: Docker, Nginx

## Quick Start

1. **Clone and Configure**
   ```bash
   git clone <repository>
   cd crystal-bay-travel
   cp .env.production .env
   # Edit .env with your API keys
   ```

2. **Run with Docker**
   ```bash
   chmod +x docker_build.sh
   ./docker_build.sh
   ```

3. **Access Application**
   - Main App: http://localhost
   - Health Check: http://localhost/health

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection
- `OPENAI_API_KEY` - AI features
- `TELEGRAM_BOT_TOKEN` - Bot integration
- `WAZZUP_API_KEY` - Chat platform
- `SAMO_OAUTH_TOKEN` - Tour bookings

### Optional
- `SUPABASE_URL/KEY` - Alternative database
- `SENDGRID_API_KEY` - Email service
- `BITRIX_WEBHOOK_URL` - CRM integration

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
```

## Production Deployment

See `DEPLOYMENT.md` for complete production setup instructions.

## License

Proprietary - Crystal Bay Travel
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # .gitignore
    gitignore_content = """.env
.env.local
*.log
logs/
data/
backup/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
.DS_Store
.vscode/
.idea/
*.swp
*.swo
.tmp/
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("📚 Созданы файлы для GitHub (README.md, .gitignore)")

def create_production_deployment():
    """Создание финального производственного образа"""
    
    # Dockerfile для production
    dockerfile_content = """FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "main:app"]
"""
    
    with open('Dockerfile.production', 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    print("🐳 Создан production Dockerfile")

if __name__ == '__main__':
    print("🚀 Crystal Bay Travel - Подготовка к публикации")
    print("=" * 50)
    
    # Шаг 1: Очистка тестовых файлов
    clean_test_files()
    
    # Шаг 2: Очистка заглушек базы данных
    clean_database_configs()
    
    # Шаг 3: Создание production environment
    create_production_env()
    
    # Шаг 4: Создание файлов для GitHub
    create_github_files()
    
    # Шаг 5: Создание production deployment
    create_production_deployment()
    
    print("=" * 50)
    print("✅ Проект готов к публикации на GitHub!")
    print()
    print("📋 Следующие шаги:")
    print("1. git init && git add . && git commit -m 'Initial commit'")
    print("2. git remote add origin <your-github-repo>")
    print("3. git push -u origin main")
    print("4. На сервере: git clone <repo> && ./docker_build.sh")
    print()
    print("⚠️  Не забудьте:")
    print("- Настроить реальные API ключи в .env")
    print("- Проверить whitelist IP адресов")
    print("- Настроить SSL сертификаты")