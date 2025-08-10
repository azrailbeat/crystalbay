# Быстрый запуск на сервере

## 1. Подготовка системы

```bash
# Обновление и установка зависимостей
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx postgresql

# Создание пользователя
sudo useradd -m -s /bin/bash crystalbay
sudo usermod -aG sudo crystalbay
```

## 2. Загрузка проекта

```bash
# Переключение на пользователя
sudo su - crystalbay

# Клонирование проекта
git clone https://github.com/ваш-username/crystal-bay-travel.git
cd crystal-bay-travel
```

## 3. Автоматическое развертывание

```bash
# Запуск скрипта развертывания
./deploy.sh
```

## 4. Настройка переменных

```bash
# Редактирование конфигурации
nano .env
```

Основные переменные:
```env
DATABASE_URL=postgresql://user:password@localhost/crystalbay_db
SAMO_OAUTH_TOKEN=ваш_samo_токен
FLASK_SECRET_KEY=случайная_строка_для_сессий
```

## 5. Запуск приложения

### Простой запуск для тестирования:
```bash
source venv/bin/activate
python main.py
```

### Продакшн запуск:
```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 --workers 3 main:app
```

### Установка как системный сервис:
```bash
# Копирование файла сервиса
sudo cp crystalbay.service /etc/systemd/system/

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable crystalbay
sudo systemctl start crystalbay
```

## 6. Настройка Nginx (опционально)

```bash
# Копирование конфигурации
sudo cp nginx.conf /etc/nginx/sites-available/crystalbay

# Активация
sudo ln -s /etc/nginx/sites-available/crystalbay /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Проверка работы

```bash
# Проверка статуса
curl http://localhost:5000/health

# Проверка SAMO API
curl http://localhost:5000/api/samo/test
```

## Управление

```bash
# Просмотр логов
sudo journalctl -u crystalbay -f

# Перезапуск
sudo systemctl restart crystalbay

# Остановка
sudo systemctl stop crystalbay
```

---

**Важно**: Обязательно настройте правильные значения в файле `.env` перед запуском!