# Установка VK Publisher на Ubuntu VPS

Подходит для Ubuntu 22.04/24.04 (для 20.04 тоже применимо, но лучше LTS 22.04+).

## 1) Требования

- CPU: 2 vCPU+
- RAM: 2 GB минимум (4 GB комфортно, особенно с Ollama)
- Диск: 10 GB+
- Ubuntu с sudo-доступом
- Открытые исходящие подключения к VK API и Telegram API

## 2) Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential python3 python3-pip python3-venv
```

Проверка:
```bash
python3 --version
pip3 --version
```

## 3) Получение проекта

```bash
cd ~
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
```

## 4) Python окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Настройка `.env`

```bash
cp .env.example .env
nano .env
```

Минимально обязательные переменные:

```dotenv
VK_ACCESS_TOKEN=...
VK_GROUP_ID=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_MODERATOR_CHAT_ID=...
```

Дополнительно (опционально):
- `OLLAMA_BASE_URL`
- `LLM_MODEL`
- `DATABASE_PATH`
- `LOG_LEVEL`

## 6) Быстрая проверка конфигурации

```bash
python scripts/test_setup.py
```

## 7) Ручной запуск приложения

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Проверки:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/
```

## 8) Запуск как systemd service

Создайте unit-файл:

```bash
sudo nano /etc/systemd/system/vk-publisher.service
```

Содержимое:

```ini
[Unit]
Description=VK Publisher FastAPI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/vk_publisher
Environment="PATH=/home/ubuntu/vk_publisher/.venv/bin"
ExecStart=/home/ubuntu/vk_publisher/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Замените `ubuntu` и путь при необходимости.

Применение:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vk-publisher
sudo systemctl start vk-publisher
sudo systemctl status vk-publisher
```

Логи:

```bash
sudo journalctl -u vk-publisher -f
```

## 9) Reverse proxy через Nginx (рекомендуется)

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/vk-publisher
```

Пример:

```nginx
server {
    listen 80;
    server_name your-domain.example;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/vk-publisher /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 10) Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## 11) Docker-вариант (альтернативно)

```bash
docker compose up -d
docker compose ps
```

Остановка:
```bash
docker compose down
```

## 12) Эксплуатационные рекомендации

1. Не храните токены в Git.
2. Для production используйте PostgreSQL вместо SQLite.
3. Включите мониторинг (`/metrics`, Prometheus, Grafana).
4. Держите отдельные `.env` для staging/prod.
5. Регулярно проверяйте логи и quota VK API.
