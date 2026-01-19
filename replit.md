# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system. Its primary purpose is to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. The system features a clean web-based admin dashboard with Apple-inspired design and complete SAMO API integration for tour management.

## Recent Changes (January 2026)

- **AI Chat System (Jan 2026)**: Complete AI-powered chat with 3 modes: Manual, Assisted, Auto
- **Telegram Integration (Jan 2026)**: Real-time webhook integration with @crystal_agent_bot
- **Auto-Responses (Jan 2026)**: Automatic AI responses for all incoming Telegram/WhatsApp messages
- **Project Cleanup (Jan 2026)**: Removed all unnecessary files, Node.js artifacts, test files - clean GitHub-ready state
- **Free WhatsApp Integration (Jan 2026)**: Support for Evolution API, whatsapp-web.js, and GREEN-API as subscription-free alternatives

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
├── main.py                    # Main Flask application
├── app_api.py                 # REST API endpoints
├── models.py                  # Database models
├── ai_chat_service.py         # AI chat (OpenAI GPT-4o)
├── messaging_service.py       # Telegram/WhatsApp hub
├── crystal_bay_samo_api.py    # SAMO API
├── proxy_client.py            # Proxy client
├── whatsapp_web_connector.py  # Free WhatsApp connector
├── Dockerfile                 # Docker config
│
├── config/                    # Configuration
│   ├── docker-compose.yml
│   └── docker-compose.production.yml
│
├── docs/                      # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   ├── QUICK_START.md
│   └── install.md
│
├── templates/                 # HTML templates
│   ├── layout.html
│   ├── dashboard.html
│   ├── leads.html
│   ├── tours_search.html
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