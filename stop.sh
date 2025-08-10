#!/bin/bash

# =======================================================
# Crystal Bay Travel - Stop Script
# =======================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_message() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    echo "======================================================"
    print_message "$BLUE" "  Crystal Bay Travel - Остановка системы"
    echo "======================================================"
    echo
}

print_step() {
    print_message "$YELLOW" "► $1"
}

print_success() {
    print_message "$GREEN" "✓ $1"
}

print_info() {
    print_message "$BLUE" "ℹ $1"
}

main() {
    print_header
    
    print_step "Остановка всех сервисов..."
    docker-compose down
    
    print_success "Все сервисы остановлены!"
    echo
    
    # Ask about data cleanup
    read -p "Удалить все данные (базы данных, логи)? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Удаление всех данных..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Все данные удалены!"
    else
        print_info "Данные сохранены. Для полной очистки используйте:"
        print_info "  docker-compose down -v --remove-orphans"
    fi
    
    echo
    print_message "$GREEN" "Crystal Bay Travel остановлен! 👋"
    echo
}

main "$@"