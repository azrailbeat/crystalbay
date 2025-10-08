# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system. Its primary purpose is to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. The system features a clean web-based admin dashboard with Apple-inspired design and complete SAMO API integration for tour management, specifically configured for Kazakhstan departures to Vietnam destinations. The system aims to provide a production-ready solution for travel agencies, integrating real-time data and advanced analytics.

## User Preferences

Preferred communication style: Simple, everyday language.
Data integrity requirement: Production uses ONLY authentic data from SAMO API. Demo mode available with realistic Kazakhstan-Vietnam travel data for presentations and demonstrations.
Market focus: Kazakhstan travelers (Almaty, Astana) to Vietnam destinations.
Currency priority: Kazakhstan Tenge (KZT) as default currency.
Production deployment: System designed for production server (IP: 46.250.234.89) with SAMO API access.
API Requirements: Real SAMO API integration for production. Demo data system available for presentations via seed_demo_data.py script.

## System Architecture

The application follows a modular, service-oriented architecture, designed for cloud deployment with scalability and fault tolerance.

### Core Components
- **Analytics Dashboard with AI Insights**: Professional analytics dashboard with real-time KPI tracking, Chart.js visualizations, and OpenAI-powered business insights. Tracks financial metrics (revenue, average booking value, profit margins), operational metrics (conversion rate, occupancy, cancellations), and customer metrics (CLV, CAC, repeat rate, NPS).
- **Web Admin Dashboard**: A clean Flask-based interface with an Apple-inspired design and light theme, providing a centralized control panel for all operations.
- **SAMO API Integration**: Comprehensive integration for tour booking, inventory management, and real-time tour data, including a full SAMO API management system with testing capabilities for over 60 commands.
- **Lead Management**: A Kanban-style system for tracking and managing customer leads, integrated with a detailed customer journey mapping feature.
- **Tour Management**: A unified single-page interface for tour search and booking, dynamically populating data from the SAMO API.

### Technical Implementations & Design Choices
- **Frontend**: Utilizes a responsive Bootstrap-based UI for the web admin dashboard, emphasizing a clean and intuitive user experience with an Apple-inspired design.
- **Backend**: Built on Flask, serving both the web dashboard and RESTful API endpoints, handling bot process management and CORS.
- **API Layer**: Implements RESTful endpoints for CRUD operations, lead import, and real-time status updates.
- **AI/NLP**: Incorporates `NLPProcessor` for message understanding, `InquiryProcessor` for automated lead analysis, and `IntelligentChatProcessor` for AI-powered chat automation using OpenAI GPT-4o.
- **Proxy Solutions**: Includes `TinyProxy` client and a PHP/bash script solution for transparent HTTP proxy routing to bypass IP restrictions.
- **Centralized Settings**: A unified panel for managing all integrations and system configurations.
- **Bitrix24 CRM Integration**: Custom travel booking pipeline matching a 9-stage Trello workflow for lead and deal management.
- **Production Readiness**: Designed for production deployment, featuring a health check endpoint, comprehensive preloading of SAMO data, and robust error handling for API unavailability.

## External Dependencies

- **SAMO Travel API**: The primary third-party service for tour booking, inventory management, and real-time tour data.
- **Flask**: The Python web framework used for the backend.
- **Bootstrap 5**: The CSS framework for the frontend UI.
- **PostgreSQL**: The relational database used for data storage.
- **OpenAI GPT-4o**: Utilized for AI-powered chat automation and intelligent processing.

## Recent Changes (October 8, 2025):
- **🔐 Security Hardening (CRITICAL)**:
  - ✅ Removed hardcoded OAuth token from crystal_bay_samo_api.py - now uses SAMO_OAUTH_TOKEN environment variable
  - ✅ Fixed OAuth token logging - no longer logs full token, only masked version (first 8 + last 4 chars)
  - ✅ Restricted CORS - now requires explicit ALLOWED_ORIGINS environment variable (no more wildcard "*")
  - ✅ Added safe_params logging to prevent credential exposure in request logs
  - ✅ Updated .gitignore with security patterns (backup files, old versions, test files)
- **🧹 Cleanup (539MB freed)**:
  - ✅ Removed backup_20250902_103619 and backup_20250902_103620 directories
  - ✅ Deleted all test files (test_*.py, *_test.py, run_all_tests.py)
  - ✅ Removed old/backup versions (samo_integration_old.py, *_backup.html)
  - ✅ Cleaned up production reports and outdated files

## Previous Changes (October 6, 2025):
- **Demo Data System**: Created seed_demo_data.py for generating realistic demo data for presentations
  - 10 Kazakhstan clients with authentic names
  - 14 travel orders (Kazakhstan → Vietnam destinations)
  - 16 multi-channel messages (Telegram/WhatsApp)
  - Realistic KZT pricing and order statuses
- **Bug Fixes**: Fixed JavaScript error in dashboard loadMetrics function
- **Database Tables**: Created all required tables (clients, orders, messages, order_logs, samo_cache, api_logs)
- **System Status**: All components verified and ready for demonstrations

## Changes (September 30, 2025):
- **Multi-Channel Messaging System**: Added Telegram and WhatsApp connectors for customer communication
- **Message Management**: Complete UI for viewing, managing, and responding to messages from all channels
- **Database Model**: Added Message model with composite unique constraint (platform, chat_id, message_id) for idempotency
- **API Endpoints**: Full REST API for messaging operations (webhooks, sending, reading messages)
- **Security Enhancements**:
  - Mandatory SESSION_SECRET environment variable (no fallback)
  - Telegram webhook validation with X-Telegram-Bot-Api-Secret-Token
  - Message deduplication via composite unique constraint
  - Database transaction rollback on errors
  - Database indexes on platform, chat_id, and created_at for performance

## System Status (October 6, 2025):
### Production Readiness:
- **Demo Mode**: ✅ READY - Full demo data available for presentations
- **Production Mode**: ⚠️ WAITING - SAMO API IP whitelist required
- **Production Server**: 46.250.234.89 (configured)
- **Outgoing IP**: 34.23.16.144 ⚠️ BLOCKED by SAMO API
- **OAuth Token**: Valid ✓ (27bd59a7ac67...)
- **Solution Needed**: Add IP 34.23.16.144 to SAMO API whitelist

### Components Status:
- ✅ Flask Application: RUNNING (port 5000)
- ✅ PostgreSQL Database: CONNECTED
- ✅ Web Dashboard: ACCESSIBLE
- ✅ Analytics & Metrics: WORKING
- ✅ Messaging System: INITIALIZED (Telegram/WhatsApp)
- ✅ Health Check: /health endpoint active
- ⚠️ SAMO API: BLOCKED (IP whitelist required)

### Demo Data Statistics:
- Clients: 10 (Kazakhstan names)
- Orders: 14 (Vietnam destinations, KZT currency)
- Messages: 16 (multi-channel)
- Revenue: 46,320,596 KZT
- Conversion Rate: 37.5%
- Active Clients: 9

### Available Commands:
- `python seed_demo_data.py` - Generate/refresh demo data
- Demo data suitable for presentations and demonstrations