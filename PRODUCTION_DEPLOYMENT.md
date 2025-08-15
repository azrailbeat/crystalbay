# Production Deployment Guide - Crystal Bay Travel

## Развертывание на сервере (46.250.234.89)

### Подготовка к развертыванию

Система готова к развертыванию на продакшн сервере. Все демо-данные удалены.

### Быстрое развертывание

```bash
# 1. Клонировать репозиторий
git clone https://github.com/your-repo/crystal-bay-travel.git
cd crystal-bay-travel

# 2. Запустить автоматическую установку
chmod +x start.sh
./start.sh
```

### Docker развертывание

```bash
# Продакшн развертывание
docker-compose -f docker-compose.production.yml up -d
```

### Настройка SAMO API

После развертывания:

1. **IP Whitelist**: Добавить IP сервера (46.250.234.89) в whitelist SAMO API
2. **OAuth Token**: Проверить актуальность токена в настройках
3. **Тестирование**: Использовать `/samo-testing` для проверки подключения

### Статус интеграции

✅ **SAMO API**: Полная интеграция готова, все endpoints работают  
✅ **Tours Search**: Интерфейс поиска туров реализован  
✅ **Production Ready**: Демо-данные удалены  
✅ **Docker**: Готов к контейнерному развертыванию  

### Порты и сервисы

- **Web App**: 5000 (HTTP)
- **Database**: PostgreSQL
- **SAMO API**: https://booking.crystalbay.com/export/default.php

### Мониторинг

После развертывания система доступна:
- Dashboard: http://46.250.234.89:5000/
- Tours Search: http://46.250.234.89:5000/tours-search
- SAMO Testing: http://46.250.234.89:5000/samo-testing

### Безопасность

- Все API keys настроены через environment variables
- PostgreSQL database с защищенными подключениями
- CORS настроен для production использования