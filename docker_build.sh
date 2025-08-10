#!/bin/bash

# Crystal Bay Travel - Production Docker Build Script

set -e

echo "🐳 Building Crystal Bay Travel for Production"
echo "============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build the application image
echo "🔨 Building application image..."
docker-compose build --no-cache web

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data logs ssl

# Set proper permissions
chmod 755 data logs

# Initialize environment if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.production ]; then
        echo "📋 Copying production environment template..."
        cp .env.production .env
        echo "⚠️  IMPORTANT: Edit .env with your actual credentials before starting!"
    else
        echo "❌ No environment file found. Please create .env with required variables."
        exit 1
    fi
fi

# Validate environment variables
echo "✅ Validating environment configuration..."
if ! grep -q "DATABASE_URL=" .env || ! grep -q "OPENAI_API_KEY=" .env; then
    echo "❌ Missing required environment variables in .env file"
    echo "Required: DATABASE_URL, OPENAI_API_KEY, SESSION_SECRET"
    exit 1
fi

# Start the services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🔍 Checking application health..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost/health &>/dev/null; then
        echo "✅ Application is healthy!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - waiting for application..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Application failed to start properly"
    echo "📋 Checking logs..."
    docker-compose logs web
    exit 1
fi

# Display status
echo ""
echo "🎉 Crystal Bay Travel is now running!"
echo "=================================="
echo "🌐 Application: http://localhost"
echo "🏥 Health Check: http://localhost/health"
echo "📊 Dashboard: http://localhost/dashboard"
echo "💬 Wazzup24: http://localhost/wazzup"
echo ""
echo "📋 Useful commands:"
echo "  docker-compose logs web     # View application logs"
echo "  docker-compose logs db      # View database logs"
echo "  docker-compose down         # Stop all services"
echo "  docker-compose restart web  # Restart application"
echo ""
echo "🔧 To update configuration:"
echo "  1. Edit .env file"
echo "  2. Run: docker-compose restart web"