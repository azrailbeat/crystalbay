# Crystal Bay Travel - Руководство по развертыванию на сервере

## Системные требования

- Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- Python 3.11+
- PostgreSQL 12+ (или доступ к Supabase)
- Nginx (рекомендуется)
- 2GB RAM минимум
- 10GB свободного места

## Пошаговое развертывание

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx postgresql postgresql-contrib

# Создание пользователя для приложения
sudo useradd -m -s /bin/bash crystalbay
sudo usermod -aG sudo crystalbay
```

### 2. Клонирование проекта

```bash
# Переключение на пользователя crystalbay
sudo su - crystalbay

# Клонирование из GitHub
git clone https://github.com/ваш-username/crystal-bay-travel.git
cd crystal-bay-travel

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install gunicorn psycopg2-binary
pip install -r requirements.txt
```

### 3. Настройка базы данных

#### Вариант A: Локальная PostgreSQL

```bash
# Создание базы данных
sudo -u postgres createdb crystalbay_db
sudo -u postgres createuser crystalbay_user

# Настройка пароля
sudo -u postgres psql
ALTER USER crystalbay_user PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE crystalbay_db TO crystalbay_user;
\q
```

#### Вариант B: Использование Supabase (рекомендуется)

1. Создайте проект на [supabase.com](https://supabase.com)
2. Скопируйте URL подключения из настроек проекта

### 4. Настройка переменных окружения

```bash
# Создание файла конфигурации
cp .env.example .env
nano .env
```

Отредактируйте `.env`:

```env
# Database
DATABASE_URL=postgresql://crystalbay_user:secure_password@localhost/crystalbay_db
# Или для Supabase:
# DATABASE_URL=postgresql://postgres:your_password@db.project_id.supabase.co:5432/postgres

# SAMO API
SAMO_OAUTH_TOKEN=ваш_samo_токен

# OpenAI (если используется)
OPENAI_API_KEY=ваш_openai_ключ

# Другие ключи
TELEGRAM_BOT_TOKEN=ваш_telegram_токен
WAZZUP_API_KEY=ваш_wazzup_ключ
SUPABASE_URL=ваш_supabase_url
SUPABASE_KEY=ваш_supabase_ключ

# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=ваш_секретный_ключ_для_сессий
```

### 5. Запуск приложения

#### Тестовый запуск

```bash
# Активация окружения
source venv/bin/activate

# Тестовый запуск
python main.py
```

#### Запуск через Gunicorn

```bash
# Запуск с Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 3 --reload main:app
```

### 6. Настройка Nginx (рекомендуется)

```bash
# Создание конфигурации Nginx
sudo nano /etc/nginx/sites-available/crystalbay
```

Содержимое файла:

```nginx
server {
    listen 80;
    server_name ваш_домен.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/crystalbay/crystal-bay-travel/static;
        expires 30d;
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/crystalbay /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Создание системного сервиса

```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/crystalbay.service
```

Содержимое файла:

```ini
[Unit]
Description=Crystal Bay Travel Application
After=network.target

[Service]
Type=exec
User=crystalbay
Group=crystalbay
WorkingDirectory=/home/crystalbay/crystal-bay-travel
Environment=PATH=/home/crystalbay/crystal-bay-travel/venv/bin
ExecStart=/home/crystalbay/crystal-bay-travel/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск и включение сервиса
sudo systemctl daemon-reload
sudo systemctl enable crystalbay
sudo systemctl start crystalbay
sudo systemctl status crystalbay
```

### 8. Настройка SSL (опционально)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d ваш_домен.com
```

## Управление приложением

### Основные команды

```bash
# Запуск приложения
sudo systemctl start crystalbay

# Остановка приложения
sudo systemctl stop crystalbay

# Перезапуск приложения
sudo systemctl restart crystalbay

# Просмотр логов
sudo journalctl -u crystalbay -f

# Проверка статуса
sudo systemctl status crystalbay
```

### Обновление приложения

```bash
# Переход в директорию проекта
cd /home/crystalbay/crystal-bay-travel

# Получение обновлений
git pull origin main

# Перезапуск сервиса
sudo systemctl restart crystalbay
```

## Мониторинг и логи

### Логи приложения

```bash
# Логи systemd
sudo journalctl -u crystalbay -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Проверка работоспособности

```bash
# Проверка статуса приложения
curl http://localhost:5000/health

# Проверка SAMO API
curl http://localhost:5000/api/samo/test
```

## Решение проблем

### Проблема с базой данных

```bash
# Проверка подключения к БД
sudo -u crystalbay psql -d crystalbay_db

# Проверка логов PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Проблема с правами доступа

```bash
# Исправление прав на файлы
sudo chown -R crystalbay:crystalbay /home/crystalbay/crystal-bay-travel
sudo chmod -R 755 /home/crystalbay/crystal-bay-travel
```

### Проблема с SAMO API

1. Убедитесь, что IP сервера добавлен в whitelist SAMO
2. Проверьте правильность OAuth токена
3. Протестируйте подключение на странице `/samo-testing`

## Backup и безопасность

### Backup базы данных

```bash
# Создание backup
sudo -u postgres pg_dump crystalbay_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из backup
sudo -u postgres psql crystalbay_db < backup_file.sql
```

### Настройка firewall

```bash
# Основные правила UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## Поддержка

Для решения проблем:

1. Проверьте логи приложения и системы
2. Убедитесь в корректности переменных окружения
3. Проверьте доступность внешних API
4. Свяжитесь с технической поддержкой SAMO для whitelist IP

---

**Важно**: После развертывания обязательно смените все пароли и ключи на production-готовые значения!