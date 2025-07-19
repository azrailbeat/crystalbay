# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system designed to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. The system combines a Telegram bot interface, web-based admin dashboard, and multiple external API integrations to provide a complete travel agency solution.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### High-Level Architecture

The application follows a modular, service-oriented architecture with clear separation between interface layers, business logic, and data persistence. The system is designed for cloud deployment with scalability and fault tolerance in mind.

**Core Components:**
1. **Telegram Bot Service** - Customer-facing conversational interface
2. **Web Admin Dashboard** - Internal management interface built with Flask
3. **API Gateway** - RESTful endpoints for external integrations
4. **AI Processing Engine** - OpenAI-powered natural language processing
5. **Data Management Layer** - Supabase database with in-memory fallbacks
6. **External Integrations** - SAMO Travel API, SendGrid, Wazzup24.ru

### Data Flow Architecture

```
Telegram Bot ─┐
              ├─► Flask Web App ─► API Layer ─► Business Logic ─► Data Layer
Web Dashboard ─┘                      │                           │
                                      │                           ├─► Supabase DB
Email/Widget ─────► Lead Import API ───┘                           └─► In-Memory Store
```

## Key Components

### 1. Frontend Interfaces

**Telegram Bot (`bot.py`, `crystal_bay_bot.py`)**
- Built with python-telegram-bot library
- Supports conversation flows for tour search and booking
- Integrates with OpenAI for natural language understanding
- Manages user sessions and booking workflows

**Web Admin Dashboard (`templates/`)**
- Apple-inspired design with light theme
- Kanban board for lead management (`leads.html`)
- Analytics dashboard with metrics visualization
- Settings panel for system configuration
- Responsive Bootstrap-based UI

### 2. Backend Services

**Flask Application (`main.py`)**
- Central application server managing all HTTP requests
- Serves both web dashboard and API endpoints
- Handles bot process management
- CORS-enabled for cross-origin requests

**API Layer (`app_api.py`, `lead_import_api.py`)**
- RESTful endpoints for CRUD operations
- Lead import from multiple sources (email, widgets, external APIs)
- Real-time status updates and processing
- JSON-based communication with error handling

### 3. AI Processing Engine

**NLP Processor (`nlp_processor.py`)**
- OpenAI GPT integration for message understanding
- Context-aware conversation handling
- Multi-language support (primarily Russian)
- Prompt engineering for travel domain

**Inquiry Processor (`inquiry_processor.py`)**
- Automated lead analysis and categorization
- Status transition management
- AI-powered response suggestions
- Confidence scoring for automated decisions

### 4. External Integrations

**SAMO Travel API (`api_integration.py`)**
- Integration with Anex Tour Partner API (https://b2b.anextour.com/api/v1/partner)
- Booking verification and search functionality using SAMO endpoints
- Tour information retrieval with SearchTour/PRICES, GetTourDetails endpoints
- Flight and accommodation data via CreateBooking, GetBookingStatus
- Proper OAuth authentication and parameter formatting per Trello documentation
- Mock data fallbacks for development

**Email Integration (`email_integration.py`, `email_processor.py`)**
- SendGrid integration for email sending
- Automated lead extraction from incoming emails
- Email parsing and data extraction
- Lead creation from email content

**Wazzup24.ru Integration (`wazzup_integration.py`)**
- Chat platform integration
- Contact synchronization
- Deal management
- Webhook handling for real-time updates

**Bitrix24 CRM Integration (`bitrix_integration.py`)**
- Complete CRM integration for lead and deal management
- Custom travel booking pipeline matching Trello workflow (9 stages)
- Pipeline stages: Новый запрос → Консультация → Подбор тура → Коммерческое предложение → Добавление интеграций → Оплатили → Принято заказчиком → Подтверждено → Завершено
- Contact and activity management
- Webhook and OAuth authentication support

**Intelligent Chat Processor (`intelligent_chat_processor.py`)**
- AI-powered chat automation using OpenAI GPT-4o
- Real-time message processing from Wazzup24.ru
- SAMO API integration for tour search and booking assistance
- Automatic lead creation in both local system and Bitrix CRM
- Intent analysis and contextual responses
- Support escalation and activity tracking

### 5. Data Management

**Models Layer (`models.py`)**
- Supabase database integration with fallback support
- In-memory data stores for development/testing
- Service classes for business logic abstraction
- Data validation and transformation

**Lead Management System**
- Kanban-style workflow management
- Status tracking (new → in_progress → pending → confirmed → closed)
- Tag-based categorization
- Automated processing capabilities

## Data Flow

### Lead Processing Pipeline

1. **Lead Capture**: Leads enter through multiple channels (Telegram, email, widgets, APIs)
2. **Initial Processing**: Basic validation and data extraction
3. **AI Analysis**: OpenAI-powered content analysis and categorization
4. **Status Assignment**: Automated status determination based on content
5. **Manager Assignment**: Distribution to appropriate team members
6. **Follow-up Tracking**: Automated reminders and status updates

### Booking Workflow

1. **Search Initiation**: Customer starts search via Telegram bot
2. **Parameter Collection**: Interactive conversation to gather requirements
3. **External API Query**: Integration with SAMO Travel for availability
4. **Options Presentation**: Formatted tour options with pricing
5. **Booking Confirmation**: Customer details collection and confirmation
6. **Status Tracking**: Booking lifecycle management

## External Dependencies

### Required Services
- **Supabase**: Primary database (PostgreSQL-based)
- **OpenAI API**: GPT models for natural language processing
- **SAMO Travel API**: Tour booking and inventory system
- **SendGrid**: Email delivery service
- **Wazzup24.ru**: Chat and CRM integration

### Development Dependencies
- **Flask**: Web framework
- **python-telegram-bot**: Telegram Bot API wrapper
- **Bootstrap 5**: Frontend CSS framework
- **JavaScript**: Client-side interactivity

### Environment Variables Required
```
TELEGRAM_BOT_TOKEN
SAMO_OAUTH_TOKEN
OPENAI_API_KEY
SENDGRID_API_KEY
SENDGRID_FROM_EMAIL
SUPABASE_URL
SUPABASE_KEY
WAZZUP_API_KEY
WAZZUP_API_SECRET
BITRIX_WEBHOOK_URL (or BITRIX_DOMAIN + BITRIX_ACCESS_TOKEN)
```

## Intelligent Chat Automation System

### Overview
The intelligent chat automation system represents a comprehensive AI-powered customer service solution that combines multiple technologies to provide seamless, automated customer support for travel bookings.

### System Components

**1. Message Processing Pipeline**
- Real-time message monitoring from Wazzup24.ru
- OpenAI GPT-4o powered intent analysis
- Contextual conversation management
- Automated response generation

**2. Tour Search Integration**
- SAMO API integration for real-time tour data
- Intelligent parameter extraction from customer messages
- Formatted tour recommendations with pricing
- Booking assistance and guidance

**3. CRM Integration**
- Automatic lead creation in Bitrix24
- Contact synchronization between platforms
- Activity tracking for all customer interactions
- Deal progression through travel booking pipeline

**4. Escalation Management**
- Intelligent detection of support requests
- Priority assignment based on message analysis
- Human handover for complex inquiries
- Real-time notification system

### Workflow Process

1. **Message Ingestion**: New messages detected via Wazzup webhooks
2. **Intent Analysis**: AI determines customer intent (tour search, booking, support, etc.)
3. **Data Retrieval**: System queries SAMO API for relevant tour information
4. **Response Generation**: AI creates contextual, personalized responses
5. **CRM Updates**: Leads and activities automatically created in Bitrix
6. **Continuous Monitoring**: System processes messages every 30 seconds

### Key Features

- **Multi-language Support**: Primarily Russian with expandable language capabilities
- **Context Awareness**: Maintains conversation history for better responses
- **Automatic Lead Scoring**: AI determines lead quality and urgency
- **Real-time Processing**: Sub-minute response times for customer inquiries
- **Fallback Mechanisms**: Human escalation for complex or urgent requests

## Deployment Strategy

### Cloud-Ready Architecture
- Containerization support for microservices deployment
- Environment-based configuration management
- Graceful degradation with fallback data stores
- Health check endpoints for monitoring

### Scalability Considerations
- Stateless design for horizontal scaling
- Database connection pooling
- Async processing for long-running operations
- CDN integration for static assets

### Monitoring and Logging
- Structured logging throughout the application
- Error tracking and alerting
- Performance metrics collection
- User interaction analytics

### Development vs Production
- Mock data services for development
- Environment-specific configuration
- Test suite for automated validation
- Staged deployment pipeline support

The architecture prioritizes reliability, maintainability, and user experience while providing comprehensive travel booking and customer management capabilities.