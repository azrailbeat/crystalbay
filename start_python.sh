#!/bin/bash
# Crystal Bay Travel - Python Quick Start Script

echo "🚀 Starting Crystal Bay Travel System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    echo "📋 Installation commands:"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   macOS: brew install python3"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo "✅ Python $PYTHON_VERSION detected"
else
    echo "⚠️  Python $PYTHON_VERSION detected, but 3.11+ recommended"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "💡 Try: sudo apt install python3-venv (on Ubuntu/Debian)"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --quiet --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --quiet -r requirements.txt
    echo "✅ Dependencies installed from requirements.txt"
else
    echo "⚠️  requirements.txt not found, installing core dependencies..."
    pip install --quiet flask flask-sqlalchemy flask-cors gunicorn psycopg2-binary requests python-dotenv openai
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️ Creating .env configuration file..."
    cp .env.example .env
    echo ""
    echo "📝 IMPORTANT: Edit .env file with your configuration:"
    echo "   - DATABASE_URL (PostgreSQL connection string)"
    echo "   - SAMO_OAUTH_TOKEN (from SAMO Travel API)"
    echo "   - OPENAI_API_KEY (from OpenAI Platform)"
    echo "   - TELEGRAM_BOT_TOKEN (optional, from @BotFather)"
    echo ""
    echo "💡 For quick testing, you can use the example values in .env"
    echo "⚠️  Some features require real API keys to function properly"
    echo ""
    read -p "Press Enter to continue with current .env settings, or Ctrl+C to edit first..."
fi

# Check if port 5000 is available
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 5000 is already in use"
    echo "🔧 Trying to stop existing process..."
    pkill -f "python.*main.py" || true
    sleep 2
fi

echo ""
echo "✅ Setup complete!"
echo "🌐 Starting Crystal Bay Travel application..."
echo "📋 Access points:"
echo "   • Web Dashboard: http://localhost:5000"
echo "   • Health Check: http://localhost:5000/health"
echo "   • SAMO Testing: http://localhost:5000/samo-testing"
echo ""

# Start the application
export FLASK_ENV=development
export DEBUG=True
python main.py