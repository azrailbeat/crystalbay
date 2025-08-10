#!/bin/bash

# =======================================================
# Crystal Bay Travel - Quick Start Script
# =======================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project info
PROJECT_NAME="Crystal Bay Travel"
VERSION="1.0.0"

# Function to print colored messages
print_message() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    echo "======================================================"
    print_message "$BLUE" "  $PROJECT_NAME - Multi-Channel Travel System"
    print_message "$BLUE" "  Version: $VERSION"
    echo "======================================================"
    echo
}

print_step() {
    print_message "$YELLOW" "► $1"
}

print_success() {
    print_message "$GREEN" "✓ $1"
}

print_error() {
    print_message "$RED" "✗ $1"
}

print_info() {
    print_message "$BLUE" "ℹ $1"
}

# Check if Docker is installed
check_docker() {
    print_step "Проверка Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен!"
        echo "Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose не установлен!"
        echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker найден: $(docker --version)"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon не запущен!"
        echo "Запустите Docker daemon и попробуйте снова."
        exit 1
    fi
}

# Check environment file
check_env_file() {
    print_step "Проверка файла переменных окружения..."
    
    if [ ! -f ".env" ]; then
        print_info "Файл .env не найден, создаю из шаблона..."
        cp .env.example .env
        print_info "Файл .env создан. ОБЯЗАТЕЛЬНО отредактируйте его перед запуском!"
        echo
        print_message "$YELLOW" "ВНИМАНИЕ: Заполните следующие обязательные поля в .env:"
        print_message "$YELLOW" "  - OPENAI_API_KEY"
        print_message "$YELLOW" "  - TELEGRAM_BOT_TOKEN"
        print_message "$YELLOW" "  - SESSION_SECRET"
        echo
        
        read -p "Нажмите Enter после редактирования .env файла..." dummy
    else
        print_success "Файл .env найден"
    fi
    
    # Check for required variables
    missing_vars=()
    
    if ! grep -q "OPENAI_API_KEY=.*[^[:space:]]" .env; then
        missing_vars+=("OPENAI_API_KEY")
    fi
    
    if ! grep -q "TELEGRAM_BOT_TOKEN=.*[^[:space:]]" .env; then
        missing_vars+=("TELEGRAM_BOT_TOKEN")
    fi
    
    if ! grep -q "SESSION_SECRET=.*[^[:space:]]" .env; then
        missing_vars+=("SESSION_SECRET")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Отсутствуют обязательные переменные: ${missing_vars[*]}"
        print_info "Отредактируйте файл .env и заполните эти поля"
        exit 1
    fi
    
    print_success "Все обязательные переменные настроены"
}

# Build and start services
start_services() {
    print_step "Остановка существующих контейнеров..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    print_step "Сборка Docker образов..."
    docker-compose build --no-cache
    
    print_step "Запуск сервисов..."
    docker-compose up -d
    
    print_success "Все сервисы запущены!"
}

# Wait for services to be healthy
wait_for_services() {
    print_step "Ожидание готовности сервисов..."
    
    # Wait for database
    echo -n "  Ждем базу данных"
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U crystal_bay -q 2>/dev/null; then
            break
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "База данных не запустилась за отведенное время"
        exit 1
    fi
    
    echo
    print_success "База данных готова"
    
    # Wait for web application
    echo -n "  Ждем веб-приложение"
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 3
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Веб-приложение не запустилось за отведенное время"
        print_info "Проверьте логи: docker-compose logs web"
        exit 1
    fi
    
    echo
    print_success "Веб-приложение готово"
}

# Show service status
show_status() {
    print_step "Статус сервисов..."
    docker-compose ps
    echo
    
    print_step "Health check..."
    if curl -s http://localhost:5000/health | grep -q '"status":"healthy"'; then
        print_success "Система работает корректно!"
    else
        print_error "Система работает, но есть проблемы"
        print_info "Проверьте: http://localhost:5000/health"
    fi
}

# Show access information
show_access_info() {
    echo
    print_message "$GREEN" "🎉 Crystal Bay Travel успешно запущен!"
    echo
    print_info "Доступные адреса:"
    print_info "  🌐 Главная страница:      http://localhost:5000"
    print_info "  💼 Административная панель: http://localhost:5000/dashboard"  
    print_info "  🏨 Каталог туров:         http://localhost:5000/tours"
    print_info "  📊 Управление лидами:     http://localhost:5000/leads"
    print_info "  📈 Аналитика:             http://localhost:5000/analytics"
    print_info "  ⚙️  Настройки:            http://localhost:5000/settings"
    echo
    print_info "🔍 API эндпоинты:"
    print_info "  Health check:             http://localhost:5000/health"
    print_info "  API статус:               http://localhost:5000/api/status"
    print_info "  SAMO API тест:            http://localhost:5000/api/samo/test"
    echo
    print_info "📊 Полезные команды:"
    print_info "  Логи:          docker-compose logs -f"
    print_info "  Статус:        docker-compose ps"
    print_info "  Остановка:     docker-compose down"
    print_info "  Перезапуск:    docker-compose restart"
    echo
}

# Main execution
main() {
    print_header
    
    # Check system requirements
    check_docker
    check_env_file
    
    # Start services
    start_services
    wait_for_services
    
    # Show results
    show_status
    show_access_info
    
    print_message "$GREEN" "Запуск завершен успешно! 🚀"
    echo
}

# Run main function
main "$@"