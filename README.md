# Crystal Bay Travel - Multi-Channel Travel Booking System

![Crystal Bay Travel](https://img.shields.io/badge/Crystal%20Bay-Travel%20System-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Latest-red)

## 🌟 Обзор

Crystal Bay Travel - это комплексная многоканальная система бронирования туров и управления клиентами. Система объединяет в себе автоматизированную обработку лидов, AI-powered взаимодействие с клиентами, и интегрированное управление бронированиями.

### ✨ Ключевые возможности

- **🤖 Telegram Bot Interface** - Клиентский интерфейс для бронирования
- **💼 Web Admin Dashboard** - Панель управления с Apple-дизайном
- **🔄 Multi-API Integration** - SAMO Travel, Wazzup24, Bitrix24, OpenAI
- **📊 Lead Management** - Kanban-доска для управления лидами
- **🤖 AI Chat Automation** - Автоматические ответы с GPT-4o
- **📈 Analytics Dashboard** - Аналитика и отчеты
- **🏨 Tour Management** - Управление турами и бронированиями

## 🚀 Быстрый запуск с Docker

### Предварительные требования

- Docker и Docker Compose
- Git

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd crystal-bay-travel
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корневой директории:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# Database
DATABASE_URL=postgresql://crystal_bay:crystal_bay_password@db:5432/crystal_bay_db

# API Keys (обязательные)
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional API Keys
WAZZUP_API_KEY=your_wazzup_api_key
SAMO_OAUTH_TOKEN=your_samo_oauth_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Security
SESSION_SECRET=your-secure-session-secret-key
```

### 3. Запуск системы

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f web

# Проверка статуса
docker-compose ps
```

### 4. Доступ к системе

- **Web Interface**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/dashboard
- **API Documentation**: http://localhost:5000/api
- **Database**: localhost:5432 (для внешнего подключения)

## 🏗️ Архитектура системы

### Основные компоненты

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Telegram Bot   │    │   API Gateway   │
│   (Flask/HTML)  │    │  (python-tg)    │    │   (REST API)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Main Application      │
                    │      (Flask Core)         │
                    └─────────────┬─────────────┘
                                  │
          ┌─────────┬─────────────┼─────────────┬─────────┐
          │         │             │             │         │
    ┌─────▼───┐ ┌───▼───┐ ┌──────▼──────┐ ┌───▼───┐ ┌───▼───┐
    │PostgreSQL│ │ Redis │ │  AI Engine  │ │ SAMO  │ │Wazzup │
    │Database  │ │ Cache │ │ (OpenAI)    │ │  API  │ │  API  │
    └─────────┘ └───────┘ └─────────────┘ └───────┘ └───────┘
```

### Внешние интеграции

- **SAMO Travel API** - Бронирование туров и управление инвентарем
- **OpenAI GPT-4o** - Обработка естественного языка и AI-чат
- **Wazzup24.ru** - Многоканальные коммуникации
- **Bitrix24** - CRM интеграция
- **Telegram Bot API** - Клиентский интерфейс
- **SendGrid** - Email рассылки

## 📁 Структура проекта

```
crystal-bay-travel/
├── 🐳 docker-compose.yml       # Docker композиция
├── 🐳 Dockerfile              # Docker образ
├── ⚙️ pyproject.toml          # Python зависимости
├── 🌐 main.py                 # Главное приложение Flask
├── 📊 models.py               # Database модели
├── 🔌 app_api.py              # API endpoints
├── 🎯 samo_api_routes.py      # SAMO API интеграция
├── 🤖 telegram_bot.py         # Telegram bot
├── 🔄 wazzup_integration.py   # Wazzup24 интеграция
├── 📁 templates/              # HTML шаблоны
│   ├── 🏠 dashboard.html      # Главная панель
│   ├── 📋 leads.html          # Управление лидами
│   ├── 🏨 tours.html          # Каталог туров
│   └── ⚙️ settings.html       # Настройки системы
├── 📁 static/                 # Статические файлы
│   ├── 🎨 css/               # Стили
│   ├── 📜 js/                # JavaScript
│   └── 🖼️ images/           # Изображения
└── 📁 nginx.conf             # Nginx конфигурация
```

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Обязательная | Описание |
|------------|--------------|----------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `OPENAI_API_KEY` | ✅ | OpenAI API ключ для AI функций |
| `TELEGRAM_BOT_TOKEN` | ✅ | Token Telegram бота |
| `WAZZUP_API_KEY` | ❌ | Wazzup24 API ключ |
| `SAMO_OAUTH_TOKEN` | ❌ | SAMO Travel OAuth токен |
| `SUPABASE_URL` | ❌ | Supabase project URL |
| `SUPABASE_KEY` | ❌ | Supabase API ключ |
| `SESSION_SECRET` | ✅ | Секретный ключ для сессий |

### Настройка API

1. **OpenAI API**:
   - Получите ключ на [platform.openai.com](https://platform.openai.com)
   - Добавьте в `.env` файл

2. **Telegram Bot**:
   - Создайте бота через [@BotFather](https://t.me/botfather)
   - Получите токен и добавьте в `.env`

3. **SAMO Travel API**:
   - Свяжитесь с Crystal Bay Travel для получения токена
   - IP-адрес сервера должен быть в белом списке

4. **Wazzup24**:
   - Зарегистрируйтесь на [wazzup24.ru](https://wazzup24.ru)
   - Получите API ключ в настройках

## 🔧 Разработка

### Локальная разработка

```bash
# Клонирование репозитория
git clone <repository-url>
cd crystal-bay-travel

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск в dev режиме
python main.py
```

### Структура базы данных

```sql
-- Основные таблицы
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    tour_name VARCHAR(255),
    departure_date DATE,
    price DECIMAL(10,2),
    status VARCHAR(50)
);
```

## 📦 Развертывание в production

### 1. Подготовка сервера

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
sudo apt-get install docker-compose-plugin
```

### 2. Настройка Nginx (опционально)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Настройка SSL

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com
```

### 4. Мониторинг

```bash
# Логи приложения
docker-compose logs -f web

# Статистика использования
docker stats

# Health check
curl http://localhost:5000/health
```

## 🔒 Безопасность

- Используйте сильные пароли для базы данных
- Регулярно обновляйте API ключи
- Настройте файрвол для ограничения доступа
- Используйте HTTPS в production
- Регулярно создавайте резервные копии

## 🤝 Поддержка

### Troubleshooting

**Проблема**: Контейнер не запускается
```bash
# Проверка логов
docker-compose logs web
```

**Проблема**: API недоступен
```bash
# Проверка состояния сервисов
docker-compose ps
```

**Проблема**: Ошибки базы данных
```bash
# Пересоздание базы данных
docker-compose down -v
docker-compose up -d
```

## 📞 Контакты

- **Разработчик**: Crystal Bay Travel Development Team
- **Email**: tech@crystalbay.travel
- **Website**: https://crystalbay.travel

## 📄 Лицензия

Этот проект разработан для Crystal Bay Travel и защищен авторским правом.