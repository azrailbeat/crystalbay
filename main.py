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
    
    return render_template('index.html', 
                          bot_status=bot_status, 
                          missing_vars=missing_vars)

@app.route('/start_bot', methods=['POST'])
def start_bot():
    """Start the Telegram bot"""
    success = start_bot_process()
    return redirect(url_for('home'))

@app.route('/bot_logs')
def bot_logs():
    """Show bot logs (this would need to be implemented with proper log file handling)"""
    # This is a placeholder. In a real implementation, you'd read from a log file
    return render_template('logs.html', logs="Bot logs will appear here")

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

# Initialize the app
if __name__ == '__main__':
    # Start the bot immediately before the app starts
    auto_start_bot()
    app.run(host='0.0.0.0', port=5000, debug=True)