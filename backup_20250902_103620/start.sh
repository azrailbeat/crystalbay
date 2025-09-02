#!/bin/bash
# Crystal Bay Travel - Quick Start Script

echo "🚀 Starting Crystal Bay Travel System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys and configuration."
    echo "   Required: SAMO_OAUTH_TOKEN, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "📊 Access your Crystal Bay Travel dashboard:"
    echo "   🌐 Web Dashboard: http://localhost:5000"
    echo "   🗄️  Database: PostgreSQL on localhost:5432"
    echo ""
    echo "🧪 Test SAMO API integration:"
    echo "   Navigate to: Dashboard → SAMO API & Тестирование"
    echo ""
    echo "📋 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi