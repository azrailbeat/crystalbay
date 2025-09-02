# Crystal Bay Travel - Comprehensive Travel Management System

## 🌟 Overview

Crystal Bay Travel is a sophisticated multi-channel travel booking and customer management system designed for modern travel agencies. The platform combines AI-powered customer service, comprehensive lead management, and seamless integration with travel booking APIs.

## ✨ Key Features

### 🎯 Core Functionality
- **Apple-inspired Dashboard** - Clean, intuitive interface with real-time metrics
- **Kanban Lead Management** - Visual lead tracking with drag-and-drop workflow
- **SAMO API Integration** - Complete tour search and booking capabilities
- **Multi-channel Support** - Website, Telegram, WhatsApp integration
- **AI-Powered Agents** - Automated customer service with GPT-4 integration

### 🔧 Technical Capabilities
- **Advanced Diagnostics** - Network, API, and system health monitoring
- **Real-time Testing** - Built-in curl execution and API testing tools
- **Flexible Deployment** - Docker-ready with scalable architecture
- **Comprehensive Logging** - Detailed error tracking and system monitoring

### 🌐 Integrations
- **SAMO Travel API** - Tour inventory and booking management
- **Wazzup24.ru** - WhatsApp business messaging
- **Supabase** - Cloud database with real-time capabilities
- **OpenAI** - Advanced AI for customer service automation

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for development)
- Environment variables configured

### Installation with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crystal-bay-travel.git
   cd crystal-bay-travel
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Start with Docker**
   ```bash
   # Development
   docker-compose up -d
   
   # Production
   docker-compose -f docker-compose.production.yml up -d
   ```

4. **Access the application**
   - Web Interface: http://localhost:5000
   - Health Check: http://localhost:5000/health

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_KEY="your_supabase_key"
   export SAMO_OAUTH_TOKEN="your_samo_token"
   export OPENAI_API_KEY="your_openai_key"
   ```

3. **Start the application**
   ```bash
   # Using start script
   ./start.sh
   
   # Or manually
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## 📋 Environment Variables

### Required Variables
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SAMO_OAUTH_TOKEN=your_samo_api_token
```

### Optional Variables
```env
OPENAI_API_KEY=your_openai_api_key
WAZZUP_API_KEY=your_wazzup_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
PORT=5000
FLASK_ENV=production
```

## 🏗️ Architecture

### Core Components
- **Flask Application** (`main.py`) - Web interface and routing
- **API Layer** (`app_api.py`) - RESTful endpoints and diagnostics
- **Data Models** (`models.py`) - Database abstractions and services
- **SAMO Integration** (`crystal_bay_samo_api.py`) - Travel API client
- **Proxy Client** (`proxy_client.py`) - Network routing utilities

### Frontend Structure
```
templates/
├── layout.html          # Base template with navigation
├── dashboard.html       # Main dashboard with metrics
├── leads.html          # Lead management interface
├── tours.html          # Tour search and booking
├── samo_testing.html   # API testing and diagnostics
└── unified_settings.html # Configuration management
```

### Static Assets
```
static/
├── css/                # Bootstrap-based styling
├── js/                 # Frontend JavaScript
└── images/             # Application assets
```

## 🔧 API Endpoints

### Health & Diagnostics
- `GET /health` - Application health check
- `GET /api/diagnostics/server` - Server information
- `GET /api/diagnostics/samo` - SAMO API status
- `GET /api/diagnostics/environment` - Environment variables check

### Lead Management
- `GET /api/leads` - Retrieve leads
- `POST /api/leads` - Create new lead
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead

### SAMO API Integration
- `POST /api/samo/search-tours` - Search tour inventory
- `POST /api/samo/execute-curl` - Execute API commands
- `GET /api/samo/currencies` - Get supported currencies
- `GET /api/samo/countries` - Get destination countries

## 🧪 Testing & Diagnostics

### Built-in Testing
The application includes comprehensive diagnostic tools:

- **Network Diagnostics** - DNS resolution, connectivity tests
- **API Testing** - Real-time SAMO API validation
- **Curl Execution** - Built-in command generation and execution
- **SSL Verification** - Certificate validation and security checks

### Development Testing
```bash
# Run basic health check
curl http://localhost:5000/health

# Test SAMO API connection
curl http://localhost:5000/api/diagnostics/samo

# Check server status
curl http://localhost:5000/api/diagnostics/server
```

## 🐳 Docker Deployment

### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    volumes:
      - .:/app
```

### Production Environment
```yaml
# docker-compose.production.yml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

## 📊 Monitoring & Logging

### Application Logs
- Structured logging with timestamps
- Error tracking and debugging information
- API request/response logging
- System health monitoring

### Metrics Dashboard
- Real-time lead statistics
- SAMO API connection status
- System performance indicators
- User activity tracking

## 🔒 Security Features

- Environment-based configuration
- API key management
- Request validation and sanitization
- Error handling without data exposure
- Secure proxy routing capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**SAMO API Connection Issues**
- Verify your OAuth token is correct
- Check IP whitelist status with SAMO support
- Use built-in diagnostics: `/samo-testing`

**Database Connection Problems**
- Verify Supabase credentials
- Check network connectivity
- Review environment variable configuration

**Docker Deployment Issues**
- Ensure all environment variables are set
- Check port availability (5000)
- Review Docker logs for detailed error messages

### Getting Help

- Check the built-in diagnostics at `/samo-testing`
- Review application logs
- Verify all environment variables are configured
- Contact support with specific error messages

## 🌟 Features in Detail

### Lead Management System
- Kanban-style visual workflow
- Automated lead scoring
- Multi-source lead import
- Real-time status updates

### SAMO API Integration
- Complete tour inventory access
- Real-time booking capabilities
- Currency and country management
- Advanced search and filtering

### AI-Powered Customer Service
- OpenAI GPT-4 integration
- Automated response generation
- Multi-language support
- Conversation history tracking

### Comprehensive Diagnostics
- Network connectivity testing
- API endpoint validation
- SSL certificate verification
- Real-time system monitoring

---

*Crystal Bay Travel - Transforming travel management with modern technology*