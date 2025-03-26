import os
from flask import Flask, render_template, request, redirect, url_for
import subprocess
import threading
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
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

@app.route('/')
def home():
    """Render the home page"""
    # Check if required environment variables are set
    required_vars = ["TELEGRAM_BOT_TOKEN", "SAMO_OAUTH_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    bot_status = "ready" if not missing_vars else "missing_env"
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)