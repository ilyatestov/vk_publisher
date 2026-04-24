# Установка VK Publisher на Ubuntu VPS

**Последнее обновление:** 2026-04-24  
**Поддерживаемые версии:** Ubuntu 20.04, 22.04, 24.04 LTS

Эта подробная инструкция проведёт вас через все этапы установки VK Publisher на виртуальный сервер (VPS) под управлением Ubuntu.

---

## 📋 Оглавление

1. [Требования к серверу](#требования-к-серверу)
2. [Подготовка сервера](#подготовка-сервера)
3. [Установка зависимостей](#установка-зависимостей)
4. [Получение проекта](#получение-проекта)
5. [Настройка Python окружения](#настройка-python-окружения)
6. [Конфигурация приложения](#конфигурация-приложения)
7. [Проверка готовности](#проверка-готовности)
8. [Запуск приложения](#запуск-приложения)
9. [Настройка как systemd service](#настройка-как-systemd-service)
10. [Reverse proxy через Nginx](#reverse-proxy-через-nginx)
11. [Настройка HTTPS (Let's Encrypt)](#настройка-https-lets-encrypt)
12. [Firewall и безопасность](#firewall-и-безопасность)
13. [Docker альтернатива](#docker-альтернатива)
14. [Мониторинг и логи](#мониторинг-и-логи)
15. [Обслуживание и обновления](#обслуживание-и-обновления)

---

## Требования к серверу

### Минимальные требования

| Компонент | Требование | Примечание |
|-----------|------------|------------|
| **CPU** | 2 vCPU | Для базовой работы без AI |
| **RAM** | 2 GB | Минимум, комфортно 4 GB |
| **Диск** | 10 GB | SSD рекомендуется |
| **ОС** | Ubuntu 20.04+ | Лучше LTS версия |

### Рекомендуемые требования (с Ollama AI)

| Компонент | Требование | Примечание |
|-----------|------------|------------|
| **CPU** | 4 vCPU | Для AI рерайтинга |
| **RAM** | 8 GB | Ollama требует много памяти |
| **Диск** | 25 GB | Для моделей ИИ |
| **Swap** | 4 GB | Дополнительная память |

### Сетевые требования

- Открытые исходящие подключения к:
  - `api.vk.com` (VK API)
  - `api.telegram.org` (Telegram Bot API)
  - `localhost:11434` (Ollama, опционально)
- Входящие порты:
  - `80/tcp` (HTTP для Let's Encrypt)
  - `443/tcp` (HTTPS, рекомендуется)
  - `22/tcp` (SSH для управления)

---

## Подготовка сервера

### 1. Подключение по SSH

```bash
ssh username@your_server_ip
```

### 2. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Создание пользователя для приложения

**Рекомендуется** запускать приложение от отдельного пользователя:

```bash
# Создать пользователя
sudo adduser vkpublisher

# Добавить в группу sudo (опционально)
sudo usermod -aG sudo vkpublisher

# Переключиться на пользователя
sudo su - vkpublisher
```

### 4. Проверка доступной памяти

```bash
free -h
df -h
```

---

## Установка зависимостей

### Базовые пакеты

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    pkg-config
```

### Проверка версий

```bash
python3 --version   # Должно быть 3.10+
pip3 --version
git --version
```

**Если Python < 3.10**, установите новую версию:

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

---

## Получение проекта

### Вариант 1: Git clone (рекомендуется)

```bash
cd ~
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
```

### Вариант 2: Загрузка ZIP архива

```bash
cd ~
wget https://github.com/ilyatestov/vk_publisher/archive/refs/heads/main.zip
unzip main.zip
mv vk_publisher-main vk_publisher
cd vk_publisher
```

### Структура проекта

```bash
ls -la
# Вы должны увидеть:
# src/, docs/, config/, docker/, requirements.txt, .env.example
```

---

## Настройка Python окружения

### 1. Создание виртуального окружения

```bash
python3 -m venv .venv
```

### 2. Активация окружения

```bash
source .venv/bin/activate
```

После активации в начале строки появится `(.venv)`.

### 3. Обновление pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

**Время установки:** 2-5 минут в зависимости от скорости интернета.

### 5. Проверка установки

```bash
pip list | grep -E "fastapi|uvicorn|sqlalchemy"
```

---

## Конфигурация приложения

### 1. Создание файла окружения

```bash
cp .env.example .env
```

### 2. Редактирование конфигурации

```bash
nano .env
```

### 3. Обязательные переменные

Откройте `.env` и заполните минимум эти переменные:

```dotenv
# === VK API ===
VK_ACCESS_TOKEN=ваш_токен_vk_app
VK_GROUP_ID=123456789
VK_API_VERSION=5.199

# === Telegram ===
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_MODERATOR_CHAT_ID=987654321

# === База данных ===
DATABASE_PATH=./data/vk_publisher.db

# === Логирование ===
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 4. Как получить токены

👉 **Подробная инструкция:** [VK_API_SETUP.md](VK_API_SETUP.md)

**Кратко:**

**VK Access Token:**
1. Перейдите на https://dev.vk.com/my-apps
2. Создайте Standalone-приложение
3. Используйте URL (замените YOUR_APP_ID):
   ```
   https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,offline&response_type=token&v=5.199
   ```
4. Скопируйте токен из адресной строки

**Telegram Bot Token:**
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям

**Telegram Chat ID:**
1. Найдите @userinfobot
2. Отправьте любое сообщение

### 5. Создание директорий

```bash
mkdir -p data logs
chmod 755 data logs
```

---

## Проверка готовности

### 1. Тестовый скрипт

```bash
python scripts/test_setup.py
```

**Ожидаемый вывод:**
```
✅ Python version: 3.10.x
✅ Dependencies installed
✅ .env file exists
✅ Required directories exist
⚠️  VK token not validated (run test_vk_api.py)
⚠️  Telegram token not validated (run test_vk_api.py)
```

### 2. Проверка VK API

```bash
python scripts/test_vk_api.py
```

### 3. Проверка Telegram

```bash
python scripts/test_database.py
```

---

## Запуск приложения

### Режим 1: Ручной запуск (для тестирования)

```bash
# Убедитесь что venv активирован
source .venv/bin/activate

# Запуск API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Проверка:**
```bash
curl http://localhost:8000/health
# Должно вернуть: {"status": "ok"}
```

**Полезные URL:**
- http://localhost:8000/ — Главная страница
- http://localhost:8000/docs — Swagger API документация
- http://localhost:8000/health — Health check
- http://localhost:8000/metrics — Prometheus метрики

### Режим 2: Web UI (дополнительно)

В **отдельном терминале**:

```bash
source .venv/bin/activate
python src/web_ui.py
```

Откройте: http://localhost:7860

### Режим 3: Фоновый запуск (nohup)

```bash
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

# Проверка
ps aux | grep uvicorn

# Остановка
pkill -f "uvicorn src.main:app"
```

---

## Настройка как systemd service

### 1. Создание unit файла

```bash
sudo nano /etc/systemd/system/vk-publisher.service
```

### 2. Содержимое файла

```ini
[Unit]
Description=VK Publisher FastAPI Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=vkpublisher
Group=vkpublisher
WorkingDirectory=/home/vkpublisher/vk_publisher
Environment="PATH=/home/vkpublisher/vk_publisher/.venv/bin"
ExecStart=/home/vkpublisher/vk_publisher/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vk-publisher

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Важно:** Замените `vkpublisher` на ваше имя пользователя если отличается.

### 3. Активация сервиса

```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable vk-publisher

# Запустить сервис
sudo systemctl start vk-publisher

# Проверить статус
sudo systemctl status vk-publisher
```

### 4. Управление сервисом

```bash
# Статус
sudo systemctl status vk-publisher

# Просмотр логов
sudo journalctl -u vk-publisher -f

# Перезапуск
sudo systemctl restart vk-publisher

# Остановка
sudo systemctl stop vk-publisher

# Логи за последние 2 часа
sudo journalctl -u vk-publisher --since "2 hours ago"
```

---

## Reverse proxy через Nginx

### 1. Установка Nginx

```bash
sudo apt install -y nginx
```

### 2. Создание конфигурации сайта

```bash
sudo nano /etc/nginx/sites-available/vk-publisher
```

### 3. Конфигурация

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Размер клиентского тела (для загрузки файлов)
    client_max_body_size 20M;

    # Логирование
    access_log /var/log/nginx/vk-publisher-access.log;
    error_log /var/log/nginx/vk-publisher-error.log;

    # API proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering off;
    }

    # Rate limiting (опционально)
    # limit_req zone=one burst=10 nodelay;
}
```

### 4. Активация сайта

```bash
# Создать символическую ссылку
sudo ln -s /etc/nginx/sites-available/vk-publisher /etc/nginx/sites-enabled/

# Удалить дефолтный сайт (опционально)
sudo rm /etc/nginx/sites-enabled/default

# Проверить конфигурацию
sudo nginx -t

# Перезагрузить Nginx
sudo systemctl reload nginx
```

### 5. Проверка

```bash
curl http://your-domain.com/health
```

---

## Настройка HTTPS (Let's Encrypt)

### 1. Установка Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Получение сертификата

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Автоматическое продление

Certbot автоматически создаёт cron задачу для продления.

**Проверка:**
```bash
sudo certbot renew --dry-run
```

### 4. Настройка firewall для HTTPS

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

---

## Firewall и безопасность

### 1. Установка UFW

```bash
sudo apt install -y ufw
```

### 2. Настройка правил

```bash
# Сброс существующих правил (осторожно!)
sudo ufw --force reset

# Разрешить SSH
sudo ufw allow OpenSSH

# Разрешить HTTP/HTTPS
sudo ufw allow 'Nginx Full'

# Включить firewall
sudo ufw enable

# Проверка статуса
sudo ufw status verbose
```

### 3. Fail2Ban (защита от брутфорса)

```bash
# Установка
sudo apt install -y fail2ban

# Создание локальной конфигурации
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Редактирование
sudo nano /etc/fail2ban/jail.local
```

**Добавьте в конец:**
```ini
[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/*error.log

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/*error.log
```

### 4. Запуск Fail2Ban

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo systemctl status fail2ban
```

---

## Docker альтернатива

Если предпочитаете Docker вместо прямой установки:

### 1. Установка Docker

```bash
# Добавить репозиторий Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
```

**Перелогиньтесь** для применения группы docker.

### 2. Запуск через Docker Compose

```bash
cd ~/vk_publisher

# Базовый запуск
docker compose up -d

# С Ollama (AI рерайтинг)
docker compose --profile with-ollama up -d

# Проверка
docker compose ps

# Логи
docker compose logs -f app
```

### 3. Остановка

```bash
docker compose down
```

---

## Мониторинг и логи

### 1. Prometheus метрики

Приложение экспортирует метрики на `/metrics`:

```bash
curl http://localhost:8000/metrics
```

**Основные метрики:**
- `pipeline_posts_processed_total` — Всего обработано постов
- `pipeline_publish_success_total` — Успешные публикации
- `pipeline_processing_duration_seconds` — Время обработки

### 2. Grafana дашборды

Если используете Docker с Grafana:

1. Откройте http://your-domain:3000
2. Логин: `admin`, Пароль: `admin`
3. Добавьте Prometheus datasource: `http://prometheus:9090`
4. Импортируйте дашборды из `monitoring/grafana/`

### 3. Логи приложения

```bash
# Файл логов
tail -f ~/vk_publisher/logs/app.log

# Через systemd
sudo journalctl -u vk-publisher -f

# Логи за сегодня
sudo journalctl -u vk-publisher --since today

# Поиск ошибок
sudo journalctl -u vk-publisher | grep -i error
```

### 4. Health checks

```bash
# Основной health check
curl http://localhost:8000/health

# Статистика
curl http://localhost:8000/api/v1/stats

# Проверка БД
curl http://localhost:8000/api/v1/health/db
```

---

## Обслуживание и обновления

### 1. Резервное копирование

```bash
# Создать директорию для бэкапов
mkdir -p ~/backups

# Бэкап базы данных
cp ~/vk_publisher/data/vk_publisher.db ~/backups/vk_publisher_db_$(date +%Y%m%d).db

# Бэкап конфигурации
cp ~/vk_publisher/.env ~/backups/vk_publisher_env_$(date +%Y%m%d)

# Бэкап логов (опционально)
tar -czf ~/backups/vk_publisher_logs_$(date +%Y%m%d).tar.gz ~/vk_publisher/logs/
```

### 2. Автоматизация бэкапов

```bash
crontab -e
```

**Добавьте:**
```bash
# Ежедневный бэкап в 3 AM
0 3 * * * /home/vkpublisher/vk_publisher/scripts/backup.sh
```

### 3. Обновление приложения

```bash
cd ~/vk_publisher

# Остановить сервис
sudo systemctl stop vk-publisher

# Обновить код
git pull origin main

# Обновить зависимости
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Запустить сервис
sudo systemctl start vk-publisher

# Проверить статус
sudo systemctl status vk-publisher
```

### 4. Очистка старых логов

```bash
# Очистить логи старше 30 дней
find ~/vk_publisher/logs -name "*.log" -mtime +30 -delete

# Очистить systemd журналы старше 7 дней
sudo journalctl --vacuum-time=7d
```

### 5. Мониторинг дискового пространства

```bash
# Проверка места
df -h

# Найти большие файлы
du -ah ~/vk_publisher | sort -rh | head -20
```

---

## Чеклист после установки

- [ ] Приложение запущено и доступно
- [ ] Health check возвращает OK
- [ ] VK API подключён (test_vk_api.py прошёл)
- [ ] Telegram бот работает
- [ ] Systemd service настроен и включён
- [ ] Nginx reverse proxy настроен
- [ ] HTTPS сертификат установлен
- [ ] Firewall настроен
- [ ] Fail2Ban запущен
- [ ] Логи пишутся корректно
- [ ] Бэкапы настроены
- [ ] Мониторинг работает

---

## Частые проблемы

### Порт 8000 занят

```bash
# Найти процесс
sudo lsof -i :8000

# Освободить порт или изменить в конфиге
```

### Недостаточно памяти

```bash
# Добавить swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Ошибка доступа к базе данных

```bash
# Исправить права
chmod 755 ~/vk_publisher/data
chown -R vkpublisher:vkpublisher ~/vk_publisher/data
```

---

## Полезные команды

```bash
# Перезапуск приложения
sudo systemctl restart vk-publisher

# Просмотр логов в реальном времени
sudo journalctl -u vk-publisher -f

# Проверка использования ресурсов
htop

# Проверка открытых портов
sudo netstat -tulpn | grep :8000

# Тест конфигурации Nginx
sudo nginx -t

# Проверка SSL сертификата
sudo certbot certificates
```

---

## Дополнительные ресурсы

- [Официальная документация VK API](https://dev.vk.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Systemd Cheatsheet](https://danielmiessler.com/study/systemd/)
- [Nginx Configuration Guide](https://www.nginx.com/resources/wiki/start/)

---

*Инструкция последний раз обновлена: 2026-04-24*
