#!/usr/bin/env python3
"""
Crystal Bay Travel - Multi-Channel Travel Booking System
Main Flask application entry point

Author: Crystal Bay Travel Development Team
Version: 1.0.0
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/crystal_bay.log', mode='a') if os.path.exists('logs') else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Database model base
class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///crystal_bay.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
    'pool_size': 10,
    'max_overflow': 20
}

# Initialize extensions
db = SQLAlchemy(model_class=Base)
db.init_app(app)
CORS(app, origins=['*'])

# Create required directories
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Import models after db initialization
with app.app_context():
    try:
        import models
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")

# Register API routes
try:
    from app_api import register_api_routes
    register_api_routes(app)
    logger.info("API routes registered successfully")
except Exception as e:
    logger.error(f"Failed to register API routes: {e}")

# Register SAMO API routes
try:
    from samo_api_routes import register_samo_api_routes
    register_samo_api_routes(app)
    logger.info("SAMO API routes registered successfully")
except (ImportError, AttributeError):
    logger.warning("SAMO API routes not available")
except Exception as e:
    logger.error(f"Failed to register SAMO API routes: {e}")

# ===== MAIN APPLICATION ROUTES =====

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    return render_template('dashboard.html')

@app.route('/leads')
def leads():
    """Lead management page"""
    return render_template('leads.html')

@app.route('/tours')
def tours():
    """Tours catalog page"""
    return render_template('tours.html')

@app.route('/bookings')
def bookings():
    """Bookings management page"""
    return render_template('bookings.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/agents')
def agents():
    """AI agents management"""
    return render_template('agents.html')

@app.route('/integrations')
def integrations():
    """Integrations management"""
    return render_template('integrations.html')

@app.route('/wazzup-integration')
def wazzup_integration():
    """Wazzup24 integration page"""
    return render_template('wazzup_integration.html')

@app.route('/unified-settings')
def unified_settings():
    """Unified settings management"""
    return render_template('unified_settings.html')

# ===== HEALTH CHECK & MONITORING =====

@app.route('/health')
def health_check():
    """Health check endpoint for Docker/monitoring"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check API keys
    api_status = {
        'openai': bool(os.environ.get('OPENAI_API_KEY')),
        'telegram': bool(os.environ.get('TELEGRAM_BOT_TOKEN')),
        'wazzup': bool(os.environ.get('WAZZUP_API_KEY')),
        'samo': bool(os.environ.get('SAMO_OAUTH_TOKEN'))
    }
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': db_status,
        'api_keys': api_status,
        'uptime': True
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/api/status')
def api_status():
    """Extended API status information"""
    try:
        # Environment information
        env_info = {
            'flask_env': os.environ.get('FLASK_ENV', 'development'),
            'debug_mode': app.debug,
            'database_url_configured': bool(os.environ.get('DATABASE_URL'))
        }
        
        # Feature flags
        features = {
            'samo_api': bool(os.environ.get('SAMO_OAUTH_TOKEN')),
            'wazzup_integration': bool(os.environ.get('WAZZUP_API_KEY')),
            'openai_integration': bool(os.environ.get('OPENAI_API_KEY')),
            'telegram_bot': bool(os.environ.get('TELEGRAM_BOT_TOKEN')),
            'supabase_integration': bool(os.environ.get('SUPABASE_URL'))
        }
        
        return jsonify({
            'application': 'Crystal Bay Travel',
            'version': '1.0.0',
            'status': 'running',
            'environment': env_info,
            'features': features,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Внутренняя ошибка сервера"), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('error.html', 
                         error_code=403, 
                         error_message="Доступ запрещен"), 403

# ===== CONTEXT PROCESSORS =====

@app.context_processor
def inject_global_variables():
    """Inject global variables into all templates"""
    return {
        'app_name': 'Crystal Bay Travel',
        'app_version': '1.0.0',
        'current_year': datetime.utcnow().year,
        'api_available': {
            'samo': bool(os.environ.get('SAMO_OAUTH_TOKEN')),
            'wazzup': bool(os.environ.get('WAZZUP_API_KEY')),
            'openai': bool(os.environ.get('OPENAI_API_KEY'))
        }
    }

# ===== APPLICATION STARTUP =====

def create_app():
    """Application factory pattern"""
    return app

if __name__ == '__main__':
    # Development server settings
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Crystal Bay Travel System...")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY', 'TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.warning("Some features may not work properly")
    
    # Start the application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise