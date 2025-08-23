# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system. Its primary purpose is to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. The system features a clean web-based admin dashboard with Apple-inspired design and complete SAMO API integration for tour management.

## Recent Changes (August 2025)

- **Final JavaScript Fixes (Aug 23)**: Fixed all JavaScript API endpoint errors, eliminated JSON parsing issues
- **Complete API Cleanup (Aug 23)**: All diagnostic endpoints return proper JSON, no more HTML errors
- **GitHub Release Preparation (Aug 23)**: Complete project cleanup, removed all test files, attached assets, and development artifacts
- **Production Code Quality (Aug 23)**: Fixed all LSP errors, eliminated type checking issues, clean compilation
- **Simplified Architecture (Aug 23)**: Streamlined models.py, removed duplicate code, optimized for deployment
- **Documentation Complete (Aug 23)**: Comprehensive README.md, proper .gitignore, production-ready structure
- **Docker Optimization (Aug 23)**: Clean Docker files, optimized build process, removed development dependencies
- **Environment Cleanup (Aug 23)**: Proper environment variable handling, removed hardcoded values, secure configuration
- **PRODUCTION READY (Aug 23)**: All components tested, no errors, perfect code quality, ready for GitHub and Docker deployment

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