#!/bin/bash
# Crystal Bay Travel - Production Deployment Script

echo "🚀 Starting Crystal Bay Travel Production Deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo ./production_deploy.sh"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create .env file with your configuration."
    echo "📝 Example .env content needed:"
    echo "DATABASE_URL=postgresql://user:pass@db:5432/crystalbay_db"
    echo "SAMO_OAUTH_TOKEN=your_samo_token"
    echo "OPENAI_API_KEY=your_openai_key"
    echo "TELEGRAM_BOT_TOKEN=your_telegram_token"
    echo "FLASK_SECRET_KEY=your_secret_key"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.production.yml pull

# Build application
echo "🏗️ Building application..."
docker-compose -f docker-compose.production.yml build

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
    echo "✅ Production deployment successful!"
    echo ""
    echo "📊 Services Status:"
    docker-compose -f docker-compose.production.yml ps
    echo ""
    echo "🌐 Access your application:"
    echo "   - Web Dashboard: http://$(curl -s ifconfig.me)"
    echo "   - With SSL: https://$(curl -s ifconfig.me)"
    echo ""
    echo "📋 Useful commands:"
    echo "   - View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "   - Stop services: docker-compose -f docker-compose.production.yml down"
    echo "   - Restart: docker-compose -f docker-compose.production.yml restart"
    echo ""
    echo "🔧 Test SAMO API:"
    echo "   Navigate to: http://$(curl -s ifconfig.me)/samo_testing"
else
    echo "❌ Deployment failed. Check logs:"
    docker-compose -f docker-compose.production.yml logs
    exit 1
fi