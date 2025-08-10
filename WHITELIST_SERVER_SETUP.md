# Crystal Bay Travel - Whitelist Server Setup Guide

## Подготовка к развертыванию на белом списке серверов

### 1. Требования к серверу

- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Минимум 2GB (рекомендуется 4GB)
- **CPU**: 2+ ядра
- **Диск**: 20GB+ свободного места
- **IP**: Должен быть в белом списке для API SAMO Travel
- **Порты**: 80, 443, 22 открыты

### 2. Переменные окружения (обязательные)

```bash
# Основные API ключи
export DATABASE_URL="postgresql://user:pass@localhost:5432/crystal_bay"
export OPENAI_API_KEY="sk-your-openai-key"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
export WAZZUP_API_KEY="your-wazzup24-api-key"
export SAMO_OAUTH_TOKEN="your-samo-api-token"

# Дополнительные (опционально)
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-key"
export SENDGRID_API_KEY="SG.your-sendgrid-key"
export BITRIX_WEBHOOK_URL="https://your-domain.bitrix24.ru/rest/webhook/url"

# Безопасность
export SESSION_SECRET="your-very-secure-session-secret"
export WHITELIST_SERVER="true"
```

### 3. Быстрое развертывание

```bash
# Клонирование репозитория
git clone <your-github-repo>
cd crystal-bay-travel

# Установка переменных окружения
source ./set_env_vars.sh  # создайте файл с вашими переменными

# Автоматическое развертывание
./deploy_whitelist_server.sh
```

### 4. Ручное развертывание

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Настройка окружения
cp .env.production .env
# Отредактируйте .env с вашими значениями

# Запуск
docker-compose up -d
```

### 5. Проверка развертывания

```bash
# Проверка состояния контейнеров
docker-compose ps

# Проверка логов
docker-compose logs -f web

# Проверка здоровья приложения
curl http://localhost/health

# Тест API
curl http://localhost/api/leads
```

### 6. Мониторинг

```bash
# Просмотр ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f

# Перезапуск сервисов
docker-compose restart web

# Обновление приложения
git pull
docker-compose up -d --build
```

### 7. Резервное копирование

```bash
# Бэкап базы данных
docker-compose exec db pg_dump -U crystal_bay crystal_bay_db > backup_$(date +%Y%m%d).sql

# Бэкап конфигурации
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml nginx.conf
```

### 8. SSL/HTTPS (рекомендуется)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автообновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 9. Firewall настройки

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 10. Troubleshooting

#### Проблема: Контейнер не запускается
```bash
docker-compose logs web
docker-compose down && docker-compose up -d
```

#### Проблема: Нет доступа к базе данных
```bash
# Проверка переменных окружения
docker-compose exec web env | grep DATABASE_URL

# Тест подключения к БД
docker-compose exec db psql -U crystal_bay -d crystal_bay_db -c "SELECT 1;"
```

#### Проблема: API не отвечает
```bash
# Проверка API ключей
docker-compose exec web env | grep API_KEY

# Проверка сетевого подключения
docker-compose exec web curl -I https://api.openai.com
```

### 11. Контакты поддержки

При возникновении проблем с развертыванием:
1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь в корректности переменных окружения
3. Проверьте доступность внешних API
4. Убедитесь что IP сервера в белом списке SAMO API

---

**Важно**: Данная система предназначена для развертывания на серверах, IP которых внесены в белый список SAMO Travel API. Убедитесь в корректности настройки IP whitelist перед развертыванием.