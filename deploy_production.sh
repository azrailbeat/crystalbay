#!/bin/bash

# Crystal Bay Travel - Production Deployment Script
# For server 46.250.234.89

echo "🚀 Crystal Bay Travel - Production Deployment"
echo "=============================================="

# Stop any existing containers
echo "Stopping existing services..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Pull latest updates (if using git)
if [ -d ".git" ]; then
    echo "Updating from git repository..."
    git pull origin main
fi

# Build production image
echo "Building production Docker image..."
docker-compose -f docker-compose.production.yml build

# Start services in production mode
echo "Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "Waiting for services to initialize..."
sleep 10

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.production.yml ps

# Test application health
echo "Testing application health..."
curl -f http://localhost:5000/ >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Access your application:"
    echo "   Dashboard: http://46.250.234.89:5000/"
    echo "   Tours Search: http://46.250.234.89:5000/tours-search"
    echo "   SAMO Testing: http://46.250.234.89:5000/samo-testing"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Add server IP (46.250.234.89) to SAMO API whitelist"
    echo "   2. Test SAMO API integration via /samo-testing"
    echo "   3. Configure any additional environment variables"
else
    echo "❌ Application health check failed. Check logs:"
    docker-compose -f docker-compose.production.yml logs
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"