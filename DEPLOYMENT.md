# Crystal Bay Travel - Production Deployment

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
