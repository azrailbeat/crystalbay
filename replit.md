# Crystal Bay Travel - Multi-Channel Travel Booking System

## Overview

Crystal Bay Travel is a comprehensive multi-channel travel booking and customer management system. Its primary purpose is to streamline travel operations through automated lead processing, AI-powered customer interactions, and integrated booking management. The system features a clean web-based admin dashboard with Apple-inspired design and complete SAMO API integration for tour management, specifically configured for Kazakhstan departures to Vietnam destinations. The system aims to provide a production-ready solution for travel agencies, integrating real-time data and advanced analytics.

## User Preferences

Preferred communication style: Simple, everyday language.
Data integrity requirement: ONLY authentic data from SAMO API - no mock, demo, placeholder, or fallback data. System shows errors when API unavailable.
Market focus: Kazakhstan travelers (Almaty, Astana) to Vietnam destinations.
Currency priority: Kazakhstan Tenge (KZT) as default currency.
Production deployment: System designed for production server (IP: 46.250.234.89) with SAMO API access.
API Requirements: Real SAMO API integration exclusively - system shows errors when API unavailable instead of demo data.

## System Architecture

The application follows a modular, service-oriented architecture, designed for cloud deployment with scalability and fault tolerance.

### Core Components
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