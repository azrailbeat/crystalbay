# Crystal Bay Travel - Multi-Channel Booking System

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
