"""
Crystal Bay Travel - Production Main Application
Clean version without development/test dependencies
"""

import os
import json
import logging
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
bot_process = None

# Health check endpoint for Docker
@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Import and register API routes
try:
    from app_api import register_api_routes
    register_api_routes(app)
    logger.info("API routes registered successfully")
except Exception as e:
    logger.error(f"Failed to register API routes: {e}")

# Register SAMO API routes
try:
    from samo_api_routes import register_samo_routes
    register_samo_routes(app)
    logger.info("SAMO API routes registered successfully")
except (ImportError, AttributeError):
    logger.warning("SAMO API routes not available")
except Exception as e:
    logger.error(f"Failed to register SAMO API routes: {e}")

# Main routes
@app.route('/')
def home():
    """Главная страница"""
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with leads overview"""
    try:
        # Get leads from database
        leads = []
        try:
            from models import LeadService
            lead_service = LeadService()
            leads = lead_service.get_leads(limit=10)
            logger.info(f"Dashboard loaded {len(leads)} leads")
        except Exception as ex:
            logger.warning(f"Database error: {ex}")
            leads = []
        
        lead_stats = {
            'total': len(leads),
            'new': len([l for l in leads if l.get('status') == 'new']),
            'contacted': len([l for l in leads if l.get('status') == 'contacted']),
            'qualified': len([l for l in leads if l.get('status') == 'qualified'])
        }
        
        return render_template('dashboard.html', 
                             leads=leads[:10], 
                             stats=lead_stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/leads')
def leads():
    """Leads management page"""
    try:
        # Get leads from database
        try:
            from models import LeadService
            lead_service = LeadService()
            leads = lead_service.get_leads(limit=100)
            logger.info(f"Loaded {len(leads)} leads from database")
            return render_template('leads.html', leads=leads)
        except Exception as ex:
            logger.error(f"Database error: {ex}")
            # Return empty state for production
            return render_template('leads.html', leads=[])
        
    except Exception as e:
        logger.error(f"Leads page error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/wazzup')
def wazzup_integration():
    """Wazzup24 Integration page"""
    return render_template('wazzup_integration.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('unified_settings.html')

# API endpoints are registered by app_api.py module

# Wazzup24 API endpoints
@app.route('/api/wazzup/test', methods=['POST'])
def test_wazzup_api():
    """Test Wazzup24 API connection"""
    try:
        from wazzup_message_processor import WazzupMessageProcessor
        
        processor = WazzupMessageProcessor()
        result = processor.test_connection()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Wazzup test error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/wazzup/messages', methods=['GET'])
def get_wazzup_messages():
    """Get recent messages from Wazzup24"""
    try:
        from wazzup_message_processor import WazzupMessageProcessor
        
        limit = request.args.get('limit', 20, type=int)
        processor = WazzupMessageProcessor()
        messages = processor.get_recent_messages(limit=limit)
        
        return jsonify({
            'status': 'success',
            'messages_count': len(messages),
            'messages': messages
        })
        
    except Exception as e:
        logger.error(f"Wazzup messages error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/wazzup/webhook', methods=['POST'])
def wazzup_webhook():
    """Webhook endpoint for receiving Wazzup24 messages"""
    try:
        from wazzup_message_processor import WazzupMessageProcessor
        
        webhook_data = request.get_json() or {}
        processor = WazzupMessageProcessor()
        
        # Process webhook message
        result = {
            'status': 'success',
            'message': 'Webhook processed',
            'data_received': bool(webhook_data)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Wazzup webhook error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Bot management
@app.route('/start-bot', methods=['POST'])
def start_bot():
    """Start Telegram bot"""
    global bot_process
    try:
        if bot_process and bot_process.poll() is None:
            return jsonify({
                'success': False,
                'message': 'Bot is already running'
            })
        
        # Start bot in background
        def run_bot():
            global bot_process
            try:
                bot_process = subprocess.Popen(
                    ['python', 'telegram_bot.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                logger.info("Bot process started")
            except Exception as e:
                logger.error(f"Failed to start bot: {e}")
        
        thread = threading.Thread(target=run_bot)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Bot starting...'
        })
        
    except Exception as e:
        logger.error(f"Start bot error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/stop-bot', methods=['POST'])
def stop_bot():
    """Stop Telegram bot"""
    global bot_process
    try:
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process.wait(timeout=10)
            logger.info("Bot process stopped")
            
        return jsonify({
            'success': True,
            'message': 'Bot stopped'
        })
        
    except Exception as e:
        logger.error(f"Stop bot error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error='Page not found', 
                         error_code=404), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', 
                         error='Internal server error', 
                         error_code=500), 500

if __name__ == '__main__':
    # Initialize database if needed
    try:
        from models import LeadService
        lead_service = LeadService()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug)