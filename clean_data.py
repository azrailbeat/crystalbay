#!/usr/bin/env python3
"""
Clean test data and prepare for production deployment
"""

import os
import json
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def clean_test_data():
    """Remove all test and development data"""
    
    # Directories to clean completely
    dirs_to_clean = [
        'attached_assets',
        'backup',
        '__pycache__',
        'tests',
        '.pytest_cache'
    ]
    
    # Files to remove
    files_to_remove = [
        'crystal_bay.log',
        '*.log',
        'comprehensive_system_analysis_report.md',
        'priority_fixes_plan.md',
        'tinyproxy_setup.md',
        'vps_script_solution.md',
        'vps_setup_guide.md'
    ]
    
    # Test data files to clean
    test_data_files = [
        'data/backup_leads_*.json',
        'data/test_*.json',
        'data/samo_connectivity_results.json'
    ]
    
    print("🧹 Cleaning test data and development files...")
    
    # Remove directories
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing directory: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # Remove files
    for pattern in files_to_remove:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file():
                print(f"Removing file: {file_path}")
                file_path.unlink()
    
    # Clean test data files
    for pattern in test_data_files:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file():
                print(f"Removing test data: {file_path}")
                file_path.unlink()
    
    # Clean Python cache files
    for cache_file in Path('.').rglob('*.pyc'):
        cache_file.unlink()
    
    for cache_file in Path('.').rglob('*.pyo'):
        cache_file.unlink()
    
    print("✅ Test data cleanup completed!")

def create_production_env():
    """Create production environment template"""
    
    env_template = """# Crystal Bay Travel - Production Environment Variables
# Copy this to .env and fill in your actual values

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/crystal_bay_db

# Flask Configuration
FLASK_ENV=production
SESSION_SECRET=your-very-secure-session-secret-change-this

# External API Keys (Required)
OPENAI_API_KEY=sk-your-openai-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
WAZZUP_API_KEY=your-wazzup24-api-key
SAMO_OAUTH_TOKEN=your-samo-api-token

# Supabase Configuration (Optional - falls back to PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Email Configuration (Optional)
SENDGRID_API_KEY=your-sendgrid-api-key

# Bitrix24 Integration (Optional)
BITRIX_WEBHOOK_URL=https://your-bitrix24-domain.bitrix24.ru/rest/webhook/url
BITRIX_USER_ID=1

# Notion Integration (Optional)
NOTION_INTEGRATION_SECRET=secret_your-notion-integration-secret
NOTION_DATABASE_ID=your-database-id-from-notion-url"""
    
    with open('.env.production', 'w') as f:
        f.write(env_template)
    
    print("📝 Created .env.production template")
    print("   Edit this file with your actual credentials before deployment")

def validate_production_files():
    """Validate that all required files exist for production"""
    
    required_files = [
        'main_production.py',
        'models.py',
        'app_api.py',
        'wazzup_api_v3.py',
        'wazzup_message_processor.py',
        'crystal_bay_samo_api.py',
        'Dockerfile',
        'docker-compose.yml',
        'init-db.sql',
        'nginx.conf',
        '.dockerignore'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required production files present")
        return True

def create_production_readme():
    """Create production deployment README"""
    
    readme_content = """# Crystal Bay Travel - Production Deployment

## Quick Start

1. **Prepare Environment**
   ```bash
   cp .env.production .env
   # Edit .env with your actual credentials
   ```

2. **Build and Run with Docker**
   ```bash
   docker-compose up -d
   ```

3. **Access Application**
   - Main Application: http://localhost
   - Health Check: http://localhost/health

## Environment Variables Required

### Core Services
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SESSION_SECRET`: Flask session secret key

### External Integrations
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `WAZZUP_API_KEY`: Wazzup24 API key
- `SAMO_OAUTH_TOKEN`: SAMO travel API token

### Optional Services
- `SUPABASE_URL` & `SUPABASE_KEY`: Supabase integration
- `SENDGRID_API_KEY`: Email service
- `BITRIX_WEBHOOK_URL`: CRM integration

## Docker Services

- **web**: Main Flask application
- **db**: PostgreSQL database
- **redis**: Redis cache
- **nginx**: Reverse proxy with SSL

## Monitoring

- Health check endpoint: `/health`
- Application logs: `docker-compose logs web`
- Database logs: `docker-compose logs db`

## Backup

Regular database backups are recommended:
```bash
docker-compose exec db pg_dump -U crystal_bay crystal_bay_db > backup.sql
```

## Security

- Change default passwords in docker-compose.yml
- Use strong SESSION_SECRET
- Configure SSL certificates in nginx.conf
- Restrict database access
"""
    
    with open('DEPLOYMENT.md', 'w') as f:
        f.write(readme_content)
    
    print("📚 Created DEPLOYMENT.md guide")

if __name__ == '__main__':
    print("🚀 Preparing Crystal Bay Travel for Production Deployment\n")
    
    # Step 1: Clean test data
    clean_test_data()
    print()
    
    # Step 2: Create production environment template
    create_production_env()
    print()
    
    # Step 3: Validate files
    if validate_production_files():
        print()
        
        # Step 4: Create deployment guide
        create_production_readme()
        print()
        
        print("🎉 Production deployment preparation completed!")
        print("\nNext steps:")
        print("1. Edit .env.production with your actual credentials")
        print("2. Copy to .env: cp .env.production .env")
        print("3. Deploy with: docker-compose up -d")
        print("4. Check health: curl http://localhost/health")
    else:
        print("\n❌ Production preparation failed - missing required files")