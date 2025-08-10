# Crystal Bay Travel - Multi-Channel Travel Booking System

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-red)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue)](https://postgresql.org)

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system designed to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management.

## ✨ Key Features

- **🎯 Multi-Channel Lead Management** - Automated lead import from various sources
- **🚀 SAMO API Integration** - Complete tour booking system integration
- **🤖 AI-Powered Assistants** - Smart chatbots using OpenAI GPT-4o
- **📱 Telegram Bot** - Full-featured customer service bot
- **💬 Messenger Integration** - Wazzup24.ru integration for WhatsApp/Viber
- **📊 Kanban Lead Board** - Visual lead management dashboard
- **📈 Analytics Dashboard** - Sales and conversion analytics
- **⚙️ Unified Settings** - Centralized integration management
- **🧪 Advanced Testing** - SAMO API testing with curl, diagnostics, and monitoring

## 🛠 Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Database**: PostgreSQL or Supabase
- **AI**: OpenAI GPT-4o
- **Deployment**: Docker, Docker Compose
- **APIs**: SAMO Travel API, Telegram Bot API, Wazzup24

## 🚀 Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/crystal-bay-travel.git
cd crystal-bay-travel
```

2. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
DATABASE_URL=postgresql://crystalbay:password@db:5432/crystalbay_travel
SAMO_OAUTH_TOKEN=your_samo_oauth_token
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
FLASK_SECRET_KEY=your_secret_key
```

3. **Start the application**
```bash
docker-compose up -d
```

4. **Access the application**
- Web Dashboard: http://localhost:5000
- Database: PostgreSQL on localhost:5432

## 📋 Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SAMO_OAUTH_TOKEN` | SAMO API OAuth token | `your_samo_token_here` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `123456:ABC-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WAZZUP_API_KEY` | Wazzup24 messenger integration | - |
| `SUPABASE_URL` | Alternative to PostgreSQL | - |
| `SUPABASE_KEY` | Supabase API key | - |
| `APP_PORT` | Application port | `5000` |
| `DEBUG` | Debug mode | `False` |

## 🏗 Development Setup

### Local Development

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

2. **Install dependencies**
```bash
pip install -r pyproject.toml
```

3. **Set up database**
```bash
# Using Docker for development database
docker run -d \
  --name crystalbay-db \
  -e POSTGRES_DB=crystalbay_travel \
  -e POSTGRES_USER=crystalbay \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:13
```

4. **Run the application**
```bash
python main.py
```

## 📁 Project Structure

```
crystal-bay-travel/
├── main.py                 # Main Flask application
├── app_api.py             # API routes and endpoints  
├── models.py              # Database models
├── crystal_bay_samo_api.py # SAMO API integration
├── samo_api_routes.py     # SAMO API routes
├── proxy_client.py        # Proxy client for API requests
├── templates/             # HTML templates
│   ├── layout.html        # Base layout
│   ├── dashboard.html     # Main dashboard
│   ├── samo_testing.html  # SAMO API testing interface
│   └── ...
├── static/               # Static assets
├── docker-compose.yml    # Docker composition
├── Dockerfile           # Docker configuration
└── README.md           # This file
```

## 🧪 SAMO API Testing

The system includes comprehensive SAMO API testing capabilities:

- **Quick Tests**: Basic API method testing
- **Curl Tests**: Command generation and execution
- **Advanced Diagnostics**: Network, DNS, SSL checks
- **Real-time Logs**: Automated monitoring and logging

Access via: Dashboard → SAMO API & Тестирование

## 🐳 Docker Deployment

### Production Deployment

1. **Use production compose file**
```bash
docker-compose -f docker-compose.production.yml up -d
```

2. **Or build custom image**
```bash
docker build -t crystal-bay-travel .
docker run -d -p 5000:5000 --env-file .env crystal-bay-travel
```

### Environment-specific Deployment

- **Development**: `docker-compose.yml`
- **Production**: `docker-compose.production.yml`

## 🔧 Configuration

### SAMO API Setup

1. Obtain OAuth token from SAMO
2. Add server IP to SAMO whitelist
3. Configure in environment variables
4. Test connection via dashboard

### Telegram Bot Setup

1. Create bot via @BotFather
2. Get bot token
3. Configure webhook or polling
4. Add token to environment

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Detailed deployment instructions
- [Docker Guide](DOCKER_GUIDE.md) - Docker-specific configuration
- [Quick Start](QUICK_START.md) - Getting started guide

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review environment configuration in `.env.example`

---

Made with ❤️ for the travel industry