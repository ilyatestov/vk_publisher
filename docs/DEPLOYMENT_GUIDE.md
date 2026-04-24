# 📦 Полное руководство по развёртыванию VK Publisher

## Содержание

1. [Быстрый старт (5 минут)](#-быстрый-старт-5-минут)
2. [Локальная разработка](#-локальная-разработка)
3. [Docker (Production)](#-docker-production)
4. [Windows (.exe)](#-windows-exe)
5. [Настройка окружения](#-настройка-окружения)
6. [Чек-лист перед деплоем](#-чек-лист-перед-деплоем)

---

## 🚀 Быстрый старт (5 минут)

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Клонирование репозитория
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher

# Копирование конфигурации
cp .env.example .env

# Редактирование .env (обязательные переменные)
# VK_ACCESS_TOKEN=ваш_токен
# TELEGRAM_BOT_TOKEN=ваш_токен

# Запуск всех сервисов
docker-compose up -d

# Проверка логов
docker-compose logs -f app
```

**Доступ к сервисам:**
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Вариант 2: Python venv

```bash
# Установка зависимостей
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env

# Запуск
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 💻 Локальная разработка

### Требования

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| Python | 3.11+ | Обязательно |
| PostgreSQL | 15+ | Или SQLite для разработки |
| Redis | 7+ | Для очередей TaskIQ |
| Ollama | latest | Опционально, для AI |

### Установка на Ubuntu/Debian

```bash
# Системные зависимости
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server git curl

# Установка Ollama (для AI-функций)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:8b-instruct-q4_K_M

# Проект
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # для разработки
```

### Конфигурация .env для разработки

```dotenv
# VK API
VK_ACCESS_TOKEN=vk1...your_token_here
VK_GROUP_ID=123456789

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_MODERATOR_CHAT_ID=987654321

# Database (SQLite для разработки)
DATABASE_URL=sqlite+aiosqlite:///./data/vk_publisher.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3:8b-instruct-q4_K_M

# Security (смените на случайную строку 32+ символов!)
ENCRYPTION_KEY=change_this_to_random_32_chars_or_more
```

### Запуск с проверкой конфигурации

```bash
# Проверка окружения
python scripts/test_setup.py

# База данных
python scripts/test_database.py

# Запуск приложения
uvicorn src.main:app --reload --log-level debug

# В отдельном терминале - TaskIQ worker
taskiq worker src.application.tasks.broker:broker
```

---

## 🐳 Docker (Production)

### docker-compose.yml для production

Создайте файл `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE__URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/vk_publisher
      - REDIS_HOST=redis
      - VK_ACCESS_TOKEN=${VK_ACCESS_TOKEN}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - vk_net

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: vk_publisher
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - vk_net

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - vk_net

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: taskiq worker src.application.tasks.broker:broker
    environment:
      - DATABASE__URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/vk_publisher
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - vk_net

volumes:
  postgres_data:
  redis_data:

networks:
  vk_net:
    driver: bridge
```

### Запуск production окружения

```bash
# Создание .env файла
cat > .env << EOF
DB_PASSWORD=secure_password_here_32chars
REDIS_PASSWORD=secure_redis_password_here
VK_ACCESS_TOKEN=vk1...your_token
TELEGRAM_BOT_TOKEN=bot_token_here
ENCRYPTION_KEY=random_32_char_secret_key
