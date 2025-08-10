#!/bin/bash

# Crystal Bay Travel - Deployment Script for Whitelisted Server
# Скрипт развертывания на белом списке серверов

set -e

echo "🚀 Crystal Bay Travel - Deployment on Whitelisted Server"
echo "======================================================="

# Check if we're running on whitelisted server
if [ -z "$WHITELIST_SERVER" ]; then
    echo "⚠️  Warning: WHITELIST_SERVER environment variable not set"
    echo "   This script is designed for whitelisted production servers"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify required environment variables
required_vars=("DATABASE_URL" "OPENAI_API_KEY" "TELEGRAM_BOT_TOKEN" "WAZZUP_API_KEY" "SAMO_OAUTH_TOKEN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '   %s\n' "${missing_vars[@]}"
    echo "Please set these variables before deployment"
    exit 1
fi

echo "✅ All required environment variables are set"

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
APP_DIR="/opt/crystal-bay-travel"
echo "📁 Setting up application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Stop existing containers if running
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Create production environment file
echo "📝 Creating production environment file..."
cat > .env << EOF
# Crystal Bay Travel - Production Configuration
FLASK_ENV=production
SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}

# Database
DATABASE_URL=$DATABASE_URL

# Core APIs
OPENAI_API_KEY=$OPENAI_API_KEY
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
WAZZUP_API_KEY=$WAZZUP_API_KEY
SAMO_OAUTH_TOKEN=$SAMO_OAUTH_TOKEN

# Optional services
SUPABASE_URL=${SUPABASE_URL:-}
SUPABASE_KEY=${SUPABASE_KEY:-}
SENDGRID_API_KEY=${SENDGRID_API_KEY:-}
BITRIX_WEBHOOK_URL=${BITRIX_WEBHOOK_URL:-}
BITRIX_USER_ID=${BITRIX_USER_ID:-1}
NOTION_INTEGRATION_SECRET=${NOTION_INTEGRATION_SECRET:-}
NOTION_DATABASE_ID=${NOTION_DATABASE_ID:-}

# Server configuration
WHITELIST_SERVER=true
EOF

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Test application health
echo "🔍 Testing application health..."
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost/health &>/dev/null; then
        echo "✅ Application is healthy!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - waiting for application..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Application health check failed"
    echo "📋 Application logs:"
    docker-compose logs --tail=50 web
    exit 1
fi

# Display deployment information
echo ""
echo "🎉 Crystal Bay Travel Successfully Deployed!"
echo "=========================================="
echo "🌐 Application URL: http://$(curl -s ifconfig.me)"
echo "🏥 Health Check: http://$(curl -s ifconfig.me)/health"
echo "📊 Dashboard: http://$(curl -s ifconfig.me)/dashboard"
echo "💬 Wazzup24: http://$(curl -s ifconfig.me)/wazzup"
echo ""
echo "📋 Management Commands:"
echo "  docker-compose logs -f web    # View application logs"
echo "  docker-compose restart web    # Restart application"
echo "  docker-compose down           # Stop all services"
echo "  docker-compose ps             # Check service status"
echo ""
echo "🔧 Configuration:"
echo "  Environment: $FLASK_ENV"
echo "  Database: $(echo $DATABASE_URL | sed 's/:.*/.../')"
echo "  OpenAI: $(echo $OPENAI_API_KEY | sed 's/sk-.*/sk-.../')"
echo "  Telegram: $(echo $TELEGRAM_BOT_TOKEN | sed 's/.*:.*/.../')"
echo ""
echo "✅ Production deployment completed successfully!"