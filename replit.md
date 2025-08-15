# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system. Its primary purpose is to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. The system features a clean web-based admin dashboard with Apple-inspired design and complete SAMO API integration for tour management.

## Recent Changes (August 2025)

- **System Refactoring**: Eliminated duplicate menu items and functions, consolidated SAMO Testing and SAMO API into single interface
- **Enhanced SAMO Testing**: Complete rebuild with curl functionality, advanced diagnostics, and real-time testing capabilities
- **Improved Navigation**: Streamlined sidebar menu with consolidated "SAMO API & Тестирование" and "Мессенджеры" sections
- **Advanced Diagnostics**: Network diagnostics, SSL checks, DNS resolution, and IP whitelist testing
- **Curl Integration**: Built-in curl command generation, execution, and result display with preset configurations
- **Real-time Monitoring**: Live connection status, service indicators, and automated log refresh
- **Project Cleanup**: Removed unused templates and eliminated redundant code paths
- **GitHub Ready**: Complete cleanup for GitHub release with streamlined Docker installation
- **Easy Installation**: Automated start.sh script and comprehensive install.md guide
- **Code Quality (Aug 10)**: Fixed all LSP errors, import issues, and type safety problems - production ready
- **Bug Fixes (Aug 10)**: Resolved wazzup_message_processor imports, SSL certificate parsing, Docker configuration
- **Production Ready (Aug 10)**: All Python files compile successfully, health endpoints working, Docker deployment fixed
- **VPS Deployment Success (Aug 10)**: System successfully deployed on VPS (46.250.234.89) with Docker
- **SAMO API URL Fix (Aug 10)**: Updated API URL from booking-kz.crystalbay.com to booking.crystalbay.com (working endpoint)
- **Documentation Package (Aug 10)**: Created comprehensive README.md, DEPLOYMENT_GUIDE.md, QUICK_START.md with multiple installation methods
- **Tours Search Interface (Aug 15)**: Complete SAMO API integration with tour search form, all endpoints working correctly
- **Production Deployment (Aug 15)**: Demo data removed, system ready for production server deployment

## User Preferences

Preferred communication style: Simple, everyday language.
Production deployment: Docker-containerized system ready for deployment on external server with comprehensive cleanup and error handling.

## System Architecture

The application follows a modular, service-oriented architecture, designed for cloud deployment with scalability and fault tolerance.

### Core Components
- **Web Admin Dashboard**: Clean Flask-based interface with Apple-inspired design and light theme
- **SAMO API Integration**: Complete tour booking system integration with proper error handling
- **Lead Management**: Kanban-style lead tracking and management system
- **Navigation System**: Fully functional sidebar navigation to all major sections
- **Settings Management**: Unified settings panel for all integrations and configurations
- **Tour Management**: Search and booking interface for SAMO tour inventory

### Technical Implementations & Design Choices
- **Frontend**: Telegram Bot using `python-telegram-bot` and a web admin dashboard with responsive Bootstrap-based UI.
- **Backend**: Flask application serving both web dashboard and API endpoints, handling bot process management and CORS.
- **API Layer**: RESTful endpoints for CRUD operations, lead import from various sources, and real-time status updates.
- **AI/NLP**: `NLPProcessor` for message understanding, `InquiryProcessor` for automated lead analysis, and `IntelligentChatProcessor` for AI-powered chat automation using OpenAI GPT-4o.
- **UI/UX**: Apple-inspired design for the web dashboard, focusing on a clean, intuitive user experience.
- **Proxy Solutions**: Implementation of TinyProxy client and a PHP/bash script solution for transparent HTTP proxy routing to bypass IP restrictions.
- **Centralized Settings**: A unified panel for managing integrations and system settings, consolidating previous separate sections.
- **Bitrix24 CRM Integration**: Custom travel booking pipeline matching a 9-stage Trello workflow for lead and deal management.

## File Structure (GitHub Ready)

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
│   ├── samo_testing.html  # SAMO API testing (unified interface)
│   ├── unified_settings.html   # Settings panel
│   ├── wazzup_integration.html # Wazzup integration
│   └── error.html         # Error page
├── static/               # Static assets (CSS, JS, images)
├── docker-compose.yml    # Development Docker setup
├── docker-compose.production.yml # Production setup
├── Dockerfile           # Docker configuration
├── start.sh            # Quick start script
├── install.md          # Installation guide
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
├── pyproject.toml      # Python dependencies
└── README.md           # Project documentation
```

## External Dependencies

- **SAMO Travel API**: Tour booking, inventory management, and real-time tour data
- **Flask**: Web framework and templating
- **Bootstrap 5**: Frontend CSS framework with custom Apple-inspired styling
- **PostgreSQL**: Database (via Replit or Supabase)
```