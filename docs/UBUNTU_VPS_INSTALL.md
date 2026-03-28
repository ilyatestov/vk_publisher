# 🐧 УСТАНОВКА VK PUBLISHER НА UBUNTU / VPS

Эта инструкция поможет вам установить и настроить VK Publisher на сервере под управлением Ubuntu (включая VPS).

---

## 📋 ТРЕБОВАНИЯ

- Ubuntu 20.04/22.04 LTS
- Python 3.10 или выше
- 2 ГБ RAM минимум
- 10 ГБ свободного места на диске
- Доступ в интернет
- Root права или sudo

---

## 🚀 ШАГ 1: ПОДГОТОВКА СЕРВЕРА

### 1.1 Обновите пакеты
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Установите необходимые утилиты
```bash
sudo apt install -y git curl wget build-essential software-properties-common
```

---

## 🚀 ШАГ 2: УСТАНОВКА PYTHON

### Для Ubuntu 20.04 и новее:

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev
```

### Проверьте версию Python:
```bash
python3 --version
```

Если версия ниже 3.10, установите свежую:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

---

## 🚀 ШАГ 3: КЛОНИРОВАНИЕ РЕПОЗИТОРИЯ

### 3.1 Создайте директорию для приложения
```bash
mkdir -p ~/vk_publisher
cd ~/vk_publisher
```

### 3.2 Клонируйте репозиторий
```bash
git clone https://github.com/ilyatestov/vk_publisher.git .
```

Или если скачиваете архивом:
```bash
wget https://github.com/ilyatestov/vk_publisher/archive/refs/heads/main.zip
unzip main.zip
cp -r vk_publisher-main/* .
rm -rf vk_publisher-main main.zip
```

---

## 🚀 ШАГ 4: СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ

### 4.1 Создайте виртуальное окружение
```bash
python3 -m venv .venv
```

### 4.2 Активируйте его
```bash
source .venv/bin/activate
```

После активации слева появится `(.venv)`.

### 4.3 Обновите pip
```bash
pip install --upgrade pip
```

---

## 🚀 ШАГ 5: УСТАНОВКА ЗАВИСИМОСТЕЙ

```bash
pip install -r requirements.txt
```

Для production также рекомендуется установить:
```bash
pip install gunicorn
```

---

## 🚀 ШАГ 6: НАСТРОЙКА КОНФИГУРАЦИИ

### 6.1 Скопируйте файл конфигурации
```bash
cp .env.example .env
```

### 6.2 Получите API токены
Следуйте инструкции: **[VK_API_SETUP.md](docs/VK_API_SETUP.md)**

### 6.3 Отредактируйте .env
```bash
nano .env
```

Заполните обязательные поля:
```bash
VK__ACCESS_TOKEN=ваш_токен_vk
VK__GROUP_ID=id_вашей_группы
TELEGRAM__TOKEN=токен_telegram_бота
TELEGRAM__MODERATOR_CHAT_ID=ваш_id_telegram
DATABASE__URL=sqlite+aiosqlite:///./data/vk_publisher.db
```

Сохраните (Ctrl+O, Enter, Ctrl+X).

---

## 🚀 ШАГ 7: ЗАПУСК ПРИЛОЖЕНИЯ

### 7.1 Простой запуск (для тестирования)
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 7.2 Запуск в фоне через nohup
```bash
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

Проверьте что работает:
```bash
curl http://localhost:8000/health
```

---

## 🚀 ШАГ 8: НАСТРОЙКА SYSTEMD (АВТОЗАПУСК)

### 8.1 Создайте файл сервиса
```bash
sudo nano /etc/systemd/system/vk-publisher.service
```

### 8.2 Вставьте содержимое:
```ini
[Unit]
Description=VK Publisher Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/vk_publisher
Environment="PATH=/home/ubuntu/vk_publisher/.venv/bin"
ExecStart=/home/ubuntu/vk_publisher/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

> ⚠️ **ВАЖНО:** Замените `ubuntu` на ваше имя пользователя!

### 8.3 Перезагрузите systemd
```bash
sudo systemctl daemon-reload
```

### 8.4 Включите автозапуск
```bash
sudo systemctl enable vk-publisher
```

### 8.5 Запустите сервис
```bash
sudo systemctl start vk-publisher
```

### 8.6 Проверьте статус
```bash
sudo systemctl status vk-publisher
```

### 8.7 Просмотр логов
```bash
sudo journalctl -u vk-publisher -f
```

### Полезные команды systemctl:
```bash
# Остановить
sudo systemctl stop vk-publisher

# Перезапустить
sudo systemctl restart vk-publisher

# Отключить автозапуск
sudo systemctl disable vk-publisher
```

---

## 🐳 АЛЬТЕРНАТИВА: ЗАПУСК ЧЕРЕZ DOCKER

### 8.1 Установите Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 8.2 Установите Docker Compose
```bash
sudo apt install -y docker-compose
```

### 8.3 Настройте .env файл
Заполните `.env` как описано выше.

### 8.4 Запустите все сервисы
```bash
docker-compose up -d
```

### 8.5 Проверьте статус
```bash
docker-compose ps
```

### 8.6 Просмотр логов
```bash
docker-compose logs -f app
```

### 8.7 Остановка
```bash
docker-compose down
```

---

## 🔒 ШАГ 9: НАСТРОЙКА FIREWALL (UFW)

### 9.1 Разрешите SSH (если еще не разрешен)
```bash
sudo ufw allow ssh
```

### 9.2 Разрешите порт приложения
```bash
sudo ufw allow 8000/tcp
```

### 9.3 Если используете Grafana/Prometheus
```bash
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus
```

### 9.4 Включите firewall
```bash
sudo ufw enable
```

### 9.5 Проверьте статус
```bash
sudo ufw status
```

---

## 🌐 ШАГ 10: НАСТРОЙКА NGINX (ОПЦИОНАЛЬНО)

Если хотите использовать доменное имя:

### 10.1 Установите Nginx
```bash
sudo apt install -y nginx
```

### 10.2 Создайте конфиг
```bash
sudo nano /etc/nginx/sites-available/vk-publisher
```

### 10.3 Вставьте:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 10.4 Активируйте сайт
```bash
sudo ln -s /etc/nginx/sites-available/vk-publisher /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 ШАГ 11: НАСТРОЙКА SSL (LET'S ENCRYPT)

### 11.1 Установите Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 11.2 Получите сертификат
```bash
sudo certbot --nginx -d your-domain.com
```

### 11.3 Автоматическое обновление
Certbot автоматически настроит cron для обновления сертификатов.

---

## 📊 ДОСТУП К ИНТЕРФЕЙСАМ

| Интерфейс | Адрес | Описание |
|-----------|-------|----------|
| Swagger UI | http://your-server-ip:8000/docs | Документация API |
| Health Check | http://your-server-ip:8000/health | Проверка здоровья |
| Metrics | http://your-server-ip:8000/metrics | Метрики Prometheus |
| Grafana | http://your-server-ip:3000 | Дашборды (логин: admin, пароль: admin) |
| Prometheus | http://your-server-ip:9090 | Метрики |

---

## 🔧 ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема: "command not found: python3"
**Решение:**
```bash
sudo apt install -y python3
```

### Проблема: "Permission denied" при создании venv
**Решение:**
```bash
sudo chown -R $USER:$USER ~/vk_publisher
```

### Проблема: Сервис не запускается
**Решение:**
```bash
# Проверьте логи
sudo journalctl -u vk-publisher -n 50

# Проверьте путь в файле сервиса
sudo cat /etc/systemd/system/vk-publisher.service
```

### Проблема: Порт 8000 уже занят
**Решение:**
```bash
# Найдите процесс
sudo lsof -i :8000

# Или измените порт в systemd файле
```

### Проблема: Docker не запускается
**Решение:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 💡 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Активация виртуального окружения
source .venv/bin/activate

# Деактивация
deactivate

# Просмотр процессов
ps aux | grep uvicorn

# Просмотр открытых портов
sudo netstat -tulpn | grep :8000

# Логи приложения
tail -f ~/vk_publisher/app.log

# Перезапуск сервиса
sudo systemctl restart vk-publisher
```

---

## 🎯 БЕЗОПАСНОСТЬ

### Рекомендации:
1. **Не используйте root** для запуска приложения
2. **Настройте firewall** (UFW)
3. **Используйте SSH ключи** вместо паролей
4. **Регулярно обновляйте** систему
5. **Сделайте бэкап** файла `.env`

### Обновление системы:
```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📈 МОНИТОРИНГ

### Установите htop для мониторинга ресурсов:
```bash
sudo apt install -y htop
htop
```

### Проверка использования памяти:
```bash
free -h
```

### Проверка места на диске:
```bash
df -h
```

---

Если возникли проблемы - создайте issue в репозитории проекта с описанием ошибки и логами.
