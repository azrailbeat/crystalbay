import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import threading
import logging
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
bot_process = None

# Import and register API routes
from app_api import register_api_routes
register_api_routes(app)

# Import and register test API routes
from app_api_test import register_test_routes
register_test_routes(app)

# Import and register lead import routes
from lead_import_api import lead_import_bp
app.register_blueprint(lead_import_bp)

def start_bot_process():
    """Start the Telegram bot in a separate process"""
    global bot_process
    if bot_process is None or bot_process.poll() is not None:
        try:
            logger.info("Starting bot process...")
            bot_process = subprocess.Popen(["python", "launch_bot.py"], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE)
            logger.info("Bot process started")
            
            # Monitor the process output in a separate thread
            def monitor_output():
                for line in bot_process.stdout:
                    logger.info(f"Bot: {line.decode().strip()}")
                for line in bot_process.stderr:
                    logger.error(f"Bot error: {line.decode().strip()}")
            
            threading.Thread(target=monitor_output, daemon=True).start()
            return True
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            return False
    else:
        logger.info("Bot process already running")
        return True

# Auto-start bot function - will be called during app initialization
def auto_start_bot():
    """Automatically start the bot when the application starts"""
    # Check if all required environment variables are present
    required_vars = ["TELEGRAM_BOT_TOKEN", "SAMO_OAUTH_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if not missing_vars:
        start_bot_process()

@app.route('/')
def home():
    """Render the home page"""
    # First, try to start the bot automatically
    auto_start_bot()
    
    # Check if required environment variables are set
    required_vars = ["TELEGRAM_BOT_TOKEN", "SAMO_OAUTH_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    bot_status = "running" if bot_process is not None and bot_process.poll() is None else "ready" if not missing_vars else "missing_env"
    
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/public')
def public_home():
    """Render the public-facing home page"""
    return render_template('home.html', active_page='home')

@app.route('/start_bot', methods=['POST'])
def start_bot():
    """Start the Telegram bot"""
    success = start_bot_process()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    # Check if required environment variables are set
    required_vars = ["TELEGRAM_BOT_TOKEN", "SAMO_OAUTH_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    bot_status = "running" if bot_process is not None and bot_process.poll() is None else "ready" if not missing_vars else "missing_env"
    
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/agents-ai')
def agents_ai():
    """Render the AI agents settings page"""
    return render_template('agents.html', active_page='agents-ai')

@app.route('/tours')
def tours():
    """Render the tours page"""
    return render_template('tours.html', active_page='tours')

@app.route('/leads')
def leads():
    """Render the leads page"""
    return render_template('new_leads.html', active_page='leads')

@app.route('/leads/new')
def leads_new():
    """Render the new leads page with enhanced functionality"""
    return render_template('leads_new.html', active_page='leads')

@app.route('/bookings')
def bookings():
    """Render the bookings page"""
    return render_template('bookings.html', active_page='bookings')

@app.route('/messages')
def messages():
    """Render the messages page"""
    return render_template('messages.html', active_page='messages')

@app.route('/agents')
def agents():
    """Render the managers page"""
    return render_template('managers.html', active_page='agents')

@app.route('/analytics')
def analytics():
    """Render the analytics page"""
    return render_template('analytics.html', active_page='analytics')

@app.route('/history')
def history():
    """Render the history page"""
    return render_template('history.html', active_page='history')

@app.route('/integrations')
def integrations():
    """Render the integrations page"""
    return render_template('integrations.html', active_page='integrations')

@app.route('/widget-demo')
def widget_demo():
    """Render the widget demo and API documentation page"""
    return render_template('widget_demo.html')

@app.route('/settings')
def settings():
    """Render the settings page"""
    return render_template('settings.html', active_page='settings')

@app.route('/bot_logs')
def bot_logs():
    """Show bot logs (this would need to be implemented with proper log file handling)"""
    # This is a placeholder. In a real implementation, you'd read from a log file
    logs = ""
    try:
        # Check if log file exists and read it
        log_path = "bot_logs.log"
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = f.read()
        else:
            logs = "No log file found. The log will appear after the bot has been started."
    except Exception as e:
        logs = f"Error reading log file: {str(e)}"
        
    return render_template('logs.html', logs=logs)

# API Endpoints for the Web Interface
@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Get the current bot status for the API"""
    required_vars = ["TELEGRAM_BOT_TOKEN", "SAMO_OAUTH_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    bot_status = "running" if bot_process is not None and bot_process.poll() is None else "ready" if not missing_vars else "missing_env"
    
    return jsonify({
        "status": bot_status,
        "missing_vars": missing_vars,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/bot/start', methods=['POST'])
def api_start_bot():
    """API endpoint to start the bot"""
    success = start_bot_process()
    return jsonify({
        "success": success,
        "message": "Bot started successfully" if success else "Failed to start bot",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings from Supabase"""
    try:
        from models import BookingService
        bookings = BookingService.get_bookings()
        return jsonify({
            "success": True,
            "bookings": bookings,
            "count": len(bookings),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get a specific booking by ID"""
    try:
        from models import BookingService
        booking = BookingService.get_booking(booking_id)
        if booking:
            return jsonify({
                "success": True,
                "booking": booking,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Booking not found",
                "timestamp": datetime.now().isoformat()
            }), 404
    except Exception as e:
        logger.error(f"Error fetching booking: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/bookings/<booking_id>/status', methods=['PUT'])
def update_booking_status(booking_id):
    """Update the status of a booking"""
    try:
        from models import BookingService
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({
                "success": False,
                "error": "Status is required",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        updated_booking = BookingService.update_booking_status(booking_id, status)
        if updated_booking:
            return jsonify({
                "success": True,
                "booking": updated_booking,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Booking not found or update failed",
                "timestamp": datetime.now().isoformat()
            }), 404
    except Exception as e:
        logger.error(f"Error updating booking status: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get available departure cities from SAMO API"""
    try:
        from helpers import fetch_cities
        samo_token = os.getenv("SAMO_OAUTH_TOKEN")
        if not samo_token:
            return jsonify({
                "success": False,
                "error": "SAMO_OAUTH_TOKEN is required",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        cities = fetch_cities(samo_token)
        return jsonify({
            "success": True,
            "cities": cities,
            "count": len(cities),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get available countries based on departure city from SAMO API"""
    try:
        from helpers import fetch_countries
        samo_token = os.getenv("SAMO_OAUTH_TOKEN")
        city_id = request.args.get('city_id')
        
        if not samo_token:
            return jsonify({
                "success": False,
                "error": "SAMO_OAUTH_TOKEN is required",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        if not city_id:
            return jsonify({
                "success": False,
                "error": "city_id is required",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        countries = fetch_countries(samo_token, city_id)
        return jsonify({
            "success": True,
            "countries": countries,
            "count": len(countries),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/tours', methods=['GET'])
def get_tours():
    """Get available tours based on selected criteria from SAMO API"""
    try:
        from helpers import fetch_tours
        samo_token = os.getenv("SAMO_OAUTH_TOKEN")
        city_id = request.args.get('city_id')
        country_id = request.args.get('country_id')
        checkin_date = request.args.get('checkin_date')
        
        if not samo_token:
            return jsonify({
                "success": False,
                "error": "SAMO_OAUTH_TOKEN is required",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        if not city_id or not country_id or not checkin_date:
            return jsonify({
                "success": False,
                "error": "city_id, country_id, and checkin_date are required",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        tours = fetch_tours(samo_token, city_id, country_id, checkin_date)
        return jsonify({
            "success": True,
            "tours": tours,
            "count": len(tours),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching tours: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/booking', methods=['POST'])
def create_booking():
    """Create a new booking with SAMO API and store in Supabase"""
    try:
        from models import BookingService
        data = request.json
        
        required_fields = ['customer_name', 'customer_phone', 'customer_email', 
                          'tour_id', 'departure_city', 'destination_country',
                          'checkin_date', 'nights', 'adults', 'price', 'currency']
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        # Optional fields
        if 'children' not in data:
            data['children'] = 0
        if 'status' not in data:
            data['status'] = 'pending'
            
        booking = BookingService.create_booking(data)
        return jsonify({
            "success": True,
            "booking": booking,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Email Integration API Endpoints
@app.route('/api/email/status', methods=['GET'])
def get_email_status():
    """Get the status of email integration"""
    try:
        from email_integration import EmailIntegration
        email = EmailIntegration()
        
        is_configured = email.is_configured()
        status = "configured" if is_configured else "not_configured"
        missing_vars = []
        
        if not os.getenv('SENDGRID_API_KEY'):
            missing_vars.append('SENDGRID_API_KEY')
        if not os.getenv('SENDGRID_FROM_EMAIL'):
            missing_vars.append('SENDGRID_FROM_EMAIL')
            
        return jsonify({
            "success": True,
            "status": status,
            "missing_vars": missing_vars,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error checking email status: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/email/send', methods=['POST'])
def send_email():
    """Send an email using SendGrid"""
    try:
        from email_integration import EmailIntegration
        data = request.json
        
        required_fields = ['to_email', 'subject']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        to_email = data.get('to_email')
        subject = data.get('subject')
        text_content = data.get('text_content')
        html_content = data.get('html_content')
        
        if not text_content and not html_content:
            return jsonify({
                "success": False,
                "error": "Either text_content or html_content must be provided",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        email = EmailIntegration()
        if not email.is_configured():
            return jsonify({
                "success": False,
                "error": "Email integration is not configured. Set SENDGRID_API_KEY and SENDGRID_FROM_EMAIL environment variables.",
                "timestamp": datetime.now().isoformat()
            }), 500
            
        success = email.send_email(to_email, subject, text_content, html_content)
        
        return jsonify({
            "success": success,
            "message": "Email sent successfully" if success else "Failed to send email",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/email/process', methods=['POST'])
def process_inbound_email():
    """Process inbound email webhook from SendGrid"""
    try:
        from email_integration import EmailIntegration
        data = request.json
        
        email = EmailIntegration()
        lead = email.receive_webhook(data)
        
        if lead:
            return jsonify({
                "success": True,
                "lead": lead,
                "message": "Email processed and lead created",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to process email or create lead",
                "timestamp": datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error processing inbound email: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/email/messages', methods=['GET'])
def get_email_messages():
    """Get recent email messages"""
    try:
        # This is a placeholder. In a real implementation, you would fetch emails from your database
        # where you've stored processed inbound emails
        messages = [
            {
                "id": "1",
                "sender_name": "Иван Иванов",
                "sender_email": "ivan@example.com",
                "subject": "Запрос о туре в Турцию",
                "preview": "Здравствуйте! Интересуют туры в Турцию на июнь 2025 года для семьи из 2 взрослых и 1 ребенка...",
                "received_date": "2025-05-04T15:42:00",
                "is_read": False,
                "lead_id": "abc123"
            },
            {
                "id": "2",
                "sender_name": "Елена Петрова",
                "sender_email": "elena@example.com",
                "subject": "Вопрос по визе",
                "preview": "Добрый день! Подскажите, пожалуйста, какие документы необходимы для получения визы в Таиланд...",
                "received_date": "2025-05-03T14:15:00",
                "is_read": True,
                "lead_id": "def456"
            }
        ]
        
        return jsonify({
            "success": True,
            "messages": messages,
            "count": len(messages),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching email messages: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Initialize the app
if __name__ == '__main__':
    # Start the bot immediately before the app starts
    auto_start_bot()
    app.run(host='0.0.0.0', port=5000, debug=True)