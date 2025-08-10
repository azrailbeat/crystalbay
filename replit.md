# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system. Its primary purpose is to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. Key capabilities include a Telegram bot interface, a web-based admin dashboard, and multiple external API integrations. The project aims to provide a complete travel agency solution, enhancing efficiency and customer engagement in the travel industry.

**Status**: ✅ Production Ready - Fully containerized with Docker, optimized for git clone deployment

## User Preferences

- **Communication Style**: Simple, everyday language (non-technical)
- **Production Deployment**: Docker-containerized system ready for deployment on external server
- **Language**: Russian for deployment preparation and documentation
- **Deployment Method**: Git clone + Docker Compose with comprehensive setup automation
- **Error Handling**: Comprehensive cleanup and graceful fallback systems implemented

## System Architecture

The application follows a modular, service-oriented architecture, designed for cloud deployment with scalability and fault tolerance.

### Core Components
- **Telegram Bot Service**: Customer-facing conversational interface.
- **Web Admin Dashboard**: Internal management interface, built with Flask, featuring an Apple-inspired design with a light theme, including a Kanban board for lead management and an analytics dashboard.
- **API Gateway**: RESTful endpoints for external integrations and core application functionalities.
- **AI Processing Engine**: Leverages OpenAI for natural language processing, context-aware conversations, and automated response generation.
- **Data Management Layer**: Primarily uses Supabase with in-memory fallbacks for data persistence.
- **Intelligent Chat Automation System**: An AI-powered customer service solution for seamless, automated customer support, integrating real-time message monitoring from Wazzup24.ru, intent analysis, and automated response generation.

### Technical Implementations & Design Choices
- **Frontend**: Telegram Bot using `python-telegram-bot` and a web admin dashboard with responsive Bootstrap-based UI.
- **Backend**: Flask application serving both web dashboard and API endpoints, handling bot process management and CORS.
- **API Layer**: RESTful endpoints for CRUD operations, lead import from various sources, and real-time status updates.
- **AI/NLP**: `NLPProcessor` for message understanding, `InquiryProcessor` for automated lead analysis, and `IntelligentChatProcessor` for AI-powered chat automation using OpenAI GPT-4o.
- **UI/UX**: Apple-inspired design for the web dashboard, focusing on a clean, intuitive user experience.
- **Proxy Solutions**: Implementation of TinyProxy client and a PHP/bash script solution for transparent HTTP proxy routing to bypass IP restrictions.
- **Centralized Settings**: A unified panel for managing integrations and system settings, consolidating previous separate sections.
- **Bitrix24 CRM Integration**: Custom travel booking pipeline matching a 9-stage Trello workflow for lead and deal management.

## External Dependencies

- **Supabase**: Primary database (PostgreSQL-based).
- **OpenAI API**: GPT models for natural language processing and AI-powered interactions.
- **SAMO Travel API**: For tour booking, inventory management, and real-time tour data.
- **SendGrid**: Email delivery service for automated lead extraction and communication.
- **Wazzup24.ru**: Chat platform integration for real-time updates and message monitoring.
- **Bitrix24**: CRM integration for lead and deal management.
- **Flask**: Web framework.
- **python-telegram-bot**: Telegram Bot API wrapper.
- **Bootstrap 5**: Frontend CSS framework.
- **JavaScript**: For client-side interactivity.
```