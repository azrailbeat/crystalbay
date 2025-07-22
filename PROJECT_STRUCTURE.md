# Crystal Bay Travel - Clean Project Structure

## 📁 Core Application Architecture (After Cleanup - July 22, 2025)

```
crystal-bay-travel/
├── 📱 Core Application
│   ├── main.py                    # Flask application entry point
│   ├── models.py                  # Data models and database access
│   └── app_api.py                 # REST API endpoints
│
├── 🔗 Integration Layer
│   ├── api_integration.py         # SAMO API base integration
│   ├── crystal_bay_samo_api.py    # Crystal Bay specific SAMO API
│   ├── bitrix_integration.py      # Bitrix24 CRM integration
│   ├── wazzup_api_v3.py          # Wazzup24 messaging API
│   ├── email_integration.py       # Email processing
│   └── web_scraper.py            # Web content extraction
│
├── 🤖 AI & Bot Components
│   ├── bot.py                     # Core Telegram bot
│   ├── crystal_bay_bot.py         # Crystal Bay specific bot logic
│   ├── nlp_processor.py           # AI natural language processing
│   ├── inquiry_processor.py       # Inquiry analysis and routing
│   ├── intelligent_chat_processor.py # AI chat automation
│   └── message_processor.py       # Message handling and routing
│
├── ⚙️ Service Layer
│   ├── lead_import_api.py         # Lead import services
│   ├── lead_connector.py          # Lead management
│   ├── email_processor.py         # Email processing services
│   ├── samo_leads_integration.py   # SAMO leads synchronization
│   ├── samo_api_routes.py         # SAMO API routing
│   └── samo_settings_integration.py # SAMO settings management
│
├── 🎛️ Configuration & Settings
│   ├── unified_settings_manager.py # Centralized settings
│   ├── settings_manager.py        # Legacy settings support
│   └── .env.example               # Environment variables template
│
├── 🌐 Web Interface
│   ├── templates/                 # HTML templates
│   │   ├── layout.html           # Base template
│   │   ├── dashboard.html        # Main dashboard
│   │   ├── leads.html            # Lead management
│   │   ├── settings.html         # Settings panel
│   │   ├── analytics.html        # Analytics view
│   │   └── bookings.html         # Booking management
│   │
│   ├── static/                   # Static assets
│   │   └── js/                   # JavaScript files
│   │
│   └── attached_assets/          # Development assets
│
├── 💾 Data Storage
│   └── data/                     # JSON data persistence
│       ├── memory_leads.json    # Lead data
│       ├── chat_history.json    # Chat history
│       └── messages.json        # Message logs
│
├── 🧪 Testing (Preserved)
│   └── tests/                    # Test suite
│       ├── test_api_integration.py
│       ├── test_models.py
│       └── run_tests.py
│
├── 📚 Documentation
│   ├── replit.md                 # Main project documentation
│   ├── comprehensive_system_analysis_report.md
│   ├── priority_fixes_plan.md
│   ├── CRYSTAL_BAY_IP_WHITELIST_REQUEST.md
│   ├── IP_WHITELIST_STATUS.md
│   └── PROJECT_STRUCTURE.md      # This file
│
├── 📦 Configuration Files
│   ├── pyproject.toml            # Python dependencies
│   ├── uv.lock                   # Lock file
│   ├── replit.nix                # Replit environment
│   └── .replit                   # Replit configuration
│
└── 🗄️ Backup (Moved)
    └── backup/                   # Old/unused files
        ├── README.md             # Backup documentation
        ├── *.py                  # 17 Python files moved
        ├── *.html                # Old templates
        ├── *.md                  # Old documentation
        └── *.log                 # Application logs
```

## 🏗️ Architecture Layers

### 1. **Presentation Layer** (Templates + Static)
- Web dashboard with Apple-inspired design
- Responsive Bootstrap-based UI
- Real-time updates via JavaScript

### 2. **API Layer** (main.py + app_api.py)
- RESTful endpoints for all operations
- CORS-enabled for cross-origin requests
- JSON-based communication

### 3. **Service Layer** (Service files)
- Business logic separation
- External API orchestration
- Data transformation and validation

### 4. **Integration Layer** (Integration files)
- SAMO API for tour booking
- Telegram Bot for customer interaction
- Bitrix24 for CRM management
- Wazzup24 for messaging
- Email processing for lead capture

### 5. **Data Layer** (models.py + data/)
- Supabase database (primary)
- JSON file persistence (fallback)
- In-memory caching

## 🔧 Key Features

### ✅ **Production Ready**
- Clean codebase with backup of old files
- Environment-based configuration
- Comprehensive error handling
- Logging throughout application

### ✅ **Integrations Active**
- SAMO API integration (awaiting IP whitelist)
- Telegram bot operational
- OpenAI AI processing
- Email import system
- CRM synchronization

### ✅ **Management Interface**
- Kanban-style lead management
- Real-time analytics dashboard
- Settings and configuration panel
- Integration testing tools

## 🚀 Next Steps

1. **Complete LSP Error Fixes** - Address remaining type safety issues
2. **Security Implementation** - Add authentication and rate limiting  
3. **Crystal Bay IP Approval** - Activate SAMO API integration
4. **Performance Optimization** - Add caching and async operations
5. **Testing Expansion** - Comprehensive test coverage

---
*Clean project structure implemented: July 22, 2025*