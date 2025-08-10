# Crystal Bay Travel - Multi-Channel Travel Booking System

[![Production Status](https://img.shields.io/badge/status-production%20ready-green.svg)](https://github.com/azrailbeat/crystalbay)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system designed for modern travel agencies. The system streamlines operations through automated lead processing, AI-powered customer interactions, and integrated booking management with a clean Apple-inspired web dashboard.

### Key Features

- **🎨 Apple-Inspired Web Dashboard** - Clean, intuitive interface with modern design
- **🏨 SAMO API Integration** - Complete tour booking system with real-time inventory
- **📊 Kanban Lead Management** - Visual lead tracking and management system
- **🤖 AI-Powered Automation** - OpenAI GPT-4o integration for intelligent responses
- **💬 Multi-Channel Messaging** - Telegram Bot and Wazzup24.ru integration
- **🔧 Advanced Diagnostics** - Network testing, SSL checks, API monitoring
- **📱 Responsive Design** - Bootstrap-based UI optimized for all devices
- **🐳 Docker Deployment** - Production-ready containerization

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (for containerized deployment)
- **PostgreSQL Database** (Neon DB or local instance)
- **Git**

### Option 1: Quick Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/azrailbeat/crystalbay.git
cd crystalbay

# Make start script executable and run
chmod +x start.sh
./start.sh
```

The start script will automatically:
- Install Python dependencies
- Setup environment variables
- Start the Flask application
- Open the web interface

### Option 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/azrailbeat/crystalbay.git
cd crystalbay

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your configuration (see Configuration section)

# 5. Start application
python main.py
```

### Option 3: Docker Deployment

#### Development Mode
```bash
docker-compose up -d
```

#### Production Mode
```bash
docker-compose -f docker-compose.production.yml up -d
```

## ⚙️ Configuration

### Environment Variables Setup

Copy `.env.example` to `.env` and configure the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
PGHOST=your-db-host
PGPORT=5432
PGUSER=your-db-user
PGPASSWORD=your-db-password
PGDATABASE=your-db-name

# SAMO Travel API (Required for booking functionality)
SAMO_OAUTH_TOKEN=your-samo-oauth-token

# OpenAI Integration (Required for AI features)
OPENAI_API_KEY=sk-proj-your-openai-key

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Wazzup24 Messaging (Optional)
WAZZUP_API_KEY=your-wazzup-api-key

# Supabase (Optional - alternative database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DEBUG=False
```

### API Keys Setup Guide

#### 1. SAMO Travel API Token
1. Contact SAMO support to request API access
2. Provide your server IP address for whitelisting
3. Receive OAuth token and add to `SAMO_OAUTH_TOKEN`

#### 2. OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create account and navigate to API Keys
3. Generate new secret key
4. Add to `OPENAI_API_KEY`

#### 3. Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command to create bot
3. Copy token to `TELEGRAM_BOT_TOKEN`

#### 4. Database Setup (Neon DB - Recommended)
1. Visit [Neon](https://neon.tech/) and create account
2. Create new project and database
3. Copy connection string to `DATABASE_URL`

## 📁 Project Structure

```
crystal-bay-travel/
├── main.py                 # Main Flask application
├── app_api.py             # API routes and endpoints
├── models.py              # Database models and services
├── crystal_bay_samo_api.py # SAMO API integration
├── samo_api_routes.py     # SAMO API route definitions
├── proxy_client.py        # Proxy client for API requests
├── templates/             # HTML templates
│   ├── layout.html        # Base layout with sidebar
│   ├── dashboard.html     # Main dashboard
│   ├── leads.html         # Lead management
│   ├── tours.html         # Tour search and booking
│   ├── bookings.html      # Booking management
│   ├── agents.html        # Agent management
│   ├── analytics.html     # Analytics dashboard
│   ├── history.html       # Activity history
│   ├── ai_agents.html     # AI agent management
│   ├── messages.html      # Message center
│   ├── samo_testing.html  # SAMO API testing interface
│   └── unified_settings.html # Settings panel
├── static/               # Static assets (CSS, JS, images)
├── docker-compose.yml    # Development Docker setup
├── docker-compose.production.yml # Production setup
├── Dockerfile.production # Production Docker configuration
├── requirements.txt      # Python dependencies
├── start.sh             # Quick start script
├── install.md           # Detailed installation guide
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT License
└── README.md            # This file
```

## 🌐 Web Interface

After installation, access the application at:

- **Local Development**: http://localhost:5000
- **Production**: http://your-server-ip:5000

### Main Sections

1. **📊 Dashboard** (`/`) - Overview of leads, bookings, and system status
2. **👥 Lead Management** (`/leads`) - Kanban-style lead tracking
3. **🏨 Tour Search** (`/tours`) - SAMO API tour booking interface
4. **📅 Bookings** (`/bookings`) - Booking management and tracking
5. **🤖 AI Agents** (`/ai-agents`) - AI automation configuration
6. **💬 Messages** (`/messages`) - Multi-channel message center
7. **🔧 SAMO Testing** (`/samo-testing`) - API diagnostics and testing
8. **⚙️ Settings** (`/unified-settings`) - System configuration

## 🔧 API Endpoints

### Health Check
```bash
GET /health
# Returns: {"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

### SAMO API Integration
```bash
# Get available tours
GET /api/samo/tours

# Search tour prices
POST /api/samo/search/prices
# Body: {"destination": "Turkey", "date_from": "2025-08-15", ...}

# Get currencies
GET /api/samo/currencies

# Test connectivity
GET /api/samo/connectivity-test
```

### System Diagnostics
```bash
# DNS resolution test
GET /api/samo/dns-check

# SSL certificate check
GET /api/samo/ssl-check

# IP whitelist test
GET /api/samo/whitelist-test

# Network diagnostics
GET /api/samo/network-diagnostics
```

## 🐳 Docker Deployment

### Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment
```bash
# Start production services
docker-compose -f docker-compose.production.yml up -d

# Scale web service
docker-compose -f docker-compose.production.yml up -d --scale web=3

# Update and restart
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

### Production Server Setup

For automated production deployment on servers:

```bash
# Make deployment script executable
chmod +x production_deploy.sh

# Run production deployment (requires root)
sudo ./production_deploy.sh
```

## 🛠️ Development

### Local Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
FLASK_ENV=development python main.py

# Enable debug logging
export DEBUG=True
```

### Code Quality
- All Python files pass compilation tests
- LSP diagnostics resolved
- Type safety implemented
- Production-ready error handling

### Testing SAMO API
1. Navigate to `/samo-testing` in web interface
2. Use built-in connectivity tests
3. Check IP whitelist status
4. Verify SSL certificates
5. Test API endpoints with curl integration

## 🔍 Troubleshooting

### Common Issues

#### SAMO API 403 Forbidden Error
**Problem**: API returns 403 Forbidden
**Solution**: 
1. Contact SAMO support
2. Provide your server IP for whitelisting
3. Verify OAuth token is correct

#### Database Connection Issues
**Problem**: Cannot connect to PostgreSQL
**Solution**:
1. Verify `DATABASE_URL` is correct
2. Check database server is running
3. Ensure firewall allows connections

#### Docker Build Failures
**Problem**: Docker build fails
**Solution**:
1. Ensure `requirements.txt` exists
2. Check `Dockerfile.production` references
3. Verify all environment variables are set

### Health Check Commands
```bash
# Check application health
curl http://localhost:5000/health

# Test SAMO API connectivity
curl http://localhost:5000/api/samo/currencies

# Verify database connection
python -c "import models; print('Database OK')"
```

## 📋 System Requirements

### Minimum Requirements
- **CPU**: 1 vCPU
- **Memory**: 512 MB RAM
- **Storage**: 1 GB SSD
- **Network**: 100 Mbps

### Recommended (Production)
- **CPU**: 2+ vCPUs
- **Memory**: 2+ GB RAM
- **Storage**: 10+ GB SSD
- **Network**: 1 Gbps
- **SSL Certificate** for HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check `install.md` for detailed installation steps
- **Issues**: Report bugs via GitHub Issues
- **Production Issues**: See `SERVER_SETUP_COMMANDS.md`

## 🎯 Roadmap

- [ ] Complete Wazzup24 integration
- [ ] Enhanced AI conversation flows  
- [ ] Advanced analytics dashboard
- [ ] Mobile app companion
- [ ] Multi-language support
- [ ] Advanced booking automation

---

**Ready for Production Deployment** 🚀

This system is production-tested with zero code errors and comprehensive Docker deployment capabilities.