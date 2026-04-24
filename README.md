# VK Publisher — Автоматизация публикаций ВКонтакте

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**VK Publisher** — это мощное приложение для автоматизации публикаций контента во ВКонтакте с поддержкой AI-рерайта, модерации через Telegram, планирования постов и мультипостинга в другие соцсети.

---

## 📋 Оглавление

- [Возможности](#-возможности)
- [Быстрый старт](#-быстрый-старт)
- [Подробная установка](#-подробная-установка)
- [Настройка окружения](#-настройка-окружения)
- [Архитектура проекта](#-архитектура-проекта)
- [API документация](#-api-документация)
- [Web UI](#-web-ui)
- [Docker](#-docker)
- [Мониторинг](#-мониторинг)
- [Безопасность](#-безопасность)
- [Устранение проблем](#-устранение-проблем)
- [Вклад в проект](#-вклад-в-проект)
- [Лицензия](#-лицензия)

---

## ✨ Возможности

### Основной функционал

| Функция | Описание |
|---------|----------|
| 🔄 **Автоматический сбор контента** | Парсинг RSS, веб-страниц, VK-пабликов по расписанию |
| 🤖 **AI-рерайтинг** | Интеграция с Ollama для уникализации контента |
| ✅ **Модерация** | Подтверждение постов через Telegram-бота перед публикацией |
| 📅 **Планировщик** | Отложенная публикация с учётом дневных лимитов |
| 🔁 **Дедупликация** | Защита от дублирования контента (exact + near-duplicate) |
| 📊 **Мониторинг** | Prometheus + Grafana дашборды |
| 🌐 **Web UI** | Веб-панель управления через Gradio |
| 🔗 **Мультипостинг** | Публикация в VK + пересылка в Telegram и другие каналы |

### Технические преимущества

- **Асинхронная архитектура** — высокая производительность до 180 постов/час
- **Clean Architecture** — чёткое разделение на domain/infrastructure/application слои
- **Idempotency** — защита от повторной публикации при сбоях
- **Backpressure** — адаптивная нагрузка при пиковых запросах
- **SSRF Protection** — защита от атак через внешние URL

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
```

### 2. Создание виртуального окружения

```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt

# (Опционально) Web UI на Gradio
pip install -r requirements-ui.txt
```

### 4. Настройка окружения

```bash
cp .env.example .env
```

Откройте `.env` и заполните обязательные переменные:

```dotenv
# VK API (получите на https://dev.vk.com/)
VK_ACCESS_TOKEN=ваш_токен_vk
VK_GROUP_ID=id_вашей_группы

# Telegram (создайте бота через @BotFather)
TELEGRAM_BOT_TOKEN=ваш_токен_telegram
TELEGRAM_MODERATOR_CHAT_ID=ваш_chat_id
```

### 5. Проверка конфигурации

```bash
python scripts/test_setup.py
```

### 6. Запуск приложения

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Проверка работы

Откройте в браузере:
- **Главная страница**: http://localhost:8000/
- **Swagger API**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

---

## 📖 Подробная установка

### Для Ubuntu/Debian VPS

👉 [Полная инструкция по установке на Ubuntu VPS](docs/UBUNTU_VPS_INSTALL.md)

**Кратко:**

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y git curl wget build-essential python3 python3-pip python3-venv

# Клонирование проекта
cd ~
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher

# Настройка
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Заполните токены

# Запуск как systemd service
sudo nano /etc/systemd/system/vk-publisher.service
sudo systemctl daemon-reload
sudo systemctl enable vk-publisher
sudo systemctl start vk-publisher
```

### Для Windows 10/11

👉 [Полная инструкция по установке на Windows](docs/WINDOWS_INSTALL.md)

**Кратко:**

```bat
# Установка Python (с галочкой "Add to PATH")
# Скачайте с https://www.python.org/downloads/windows/

# Клонирование
cd %USERPROFILE%
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher

# Виртуальное окружение
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Настройка
copy .env.example .env
notepad .env

# Запуск
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Через Docker Compose

```bash
# Базовый запуск
docker compose up -d

# С Ollama (для AI-рерайта)
docker compose --profile with-ollama up -d

# Просмотр логов
docker compose logs -f app

# Остановка
docker compose down
```

**Сервисы:**
- `app` — FastAPI приложение (порт 8000)
- `db` — PostgreSQL (порт 5432)
- `redis` — Redis кэш (порт 6379)
- `prometheus` — Мониторинг (порт 9090)
- `grafana` — Дашборды (порт 3000)
- `ollama` — AI модель (порт 11434, опционально)

---

## ⚙️ Настройка окружения

### Обязательные переменные

| Переменная | Описание | Пример |
|------------|----------|--------|
| `VK_ACCESS_TOKEN` | Токен доступа VK API (Stand-alone приложение) | `abc123...` |
| `VK_GROUP_ID` | ID сообщества ВКонтакте (положительное число) | `123456789` |
| `VK_API_VERSION` | Версия VK API | `5.199` |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота для модерации | `123456:ABCdef...` |
| `TELEGRAM_MODERATOR_CHAT_ID` | Ваш Chat ID для получения уведомлений | `987654321` |

### Опциональные переменные

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OLLAMA_BASE_URL` | URL сервиса Ollama для AI-рерайта | `http://localhost:11434` |
| `LLM_MODEL` | Модель для рерайта | `llama2` |
| `DATABASE_PATH` | Путь к SQLite базе данных | `./data/vk_publisher.db` |
| `DATABASE_URL` | PostgreSQL connection string (при использовании) | `postgresql+asyncpg://...` |
| `MAX_POSTS_PER_DAY` | Лимит публикаций в день | `50` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `LOG_FILE` | Путь к файлу логов | `logs/app.log` |
| `ENCRYPTION_KEY` | Ключ шифрования (минимум 32 символа) | `your_secret_key` |
| `API_HOST` | Хост для API сервера | `0.0.0.0` |
| `WEB_UI_HOST` | Хост для Web UI | `127.0.0.1` |

### Получение токенов

👉 [Подробная инструкция по получению VK API токена](docs/VK_API_SETUP.md)

**VK Access Token:**
1. Перейдите на https://dev.vk.com/my-apps
2. Создайте Standalone-приложение
3. Используйте URL для получения токена:
   ```
   https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,offline&response_type=token&v=5.199
   ```
4. Скопируйте токен из адресной строки после `access_token=`

**Telegram Bot Token:**
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Сохраните полученный токен

**Telegram Chat ID:**
1. Найдите @userinfobot или @getmyid_bot
2. Отправьте любое сообщение
3. Скопируйте ваш ID

---

## 🏗️ Архитектура проекта

### Общая схема

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Источники     │────▶│   Pipeline        │────▶│   Публикация    │
│   (RSS/Web/VK)  │     │   Обработка       │     │   (VK/Telegram) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   Модерация      │
                        │   (Telegram)     │
                        └──────────────────┘
```

### Конвейер обработки (Pipeline)

1. **Fetch** — Сбор контента из источников
2. **AI Rewrite** — Уникализация через Ollama (опционально)
3. **Moderation** — Проверка через Telegram-бота
4. **Publish** — Публикация в VK и другие каналы

### Структура кода

```
src/
├── main.py                 # Точка входа FastAPI
├── bootstrap/              # DI контейнер, инициализация
├── core/                   # Конфигурация, логирование, исключения
├── domain/                 # Бизнес-логика (Entities, Interfaces)
├── infrastructure/         # Внешние интеграции (VK, DB, TG, Ollama)
├── workers/                # Pipeline воркеры
├── api/                    # REST API endpoints
├── content_fetcher/        # Сбор контента (RSS, Web, VK)
├── processor/              # Обработка (dedup, rewrite)
├── publisher/              # Публикация и footer
├── telegram_bot/           # Бот для модерации
├── utils/                  # Утилиты (url_safety, error_handling)
└── web_ui.py               # Gradio веб-интерфейс
```

👉 [Подробнее о структуре проекта](docs/PROJECT_STRUCTURE.md)  
👉 [Канонические пути импортов](docs/CANONICAL_ARCHITECTURE.md)

---

## 📡 API документация

После запуска приложения доступна полная API документация:

### Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Главная страница с информацией |
| GET | `/health` | Проверка здоровья сервиса |
| GET | `/metrics` | Prometheus метрики |
| GET | `/api/v1/stats` | Статистика публикаций |
| GET | `/api/v1/posts` | Список постов |
| POST | `/api/v1/posts` | Создание поста |
| GET | `/api/v1/sources` | Список источников |
| POST | `/api/v1/sources` | Добавление источника |
| PUT | `/api/v1/sources/{id}` | Обновление источника |
| DELETE | `/api/v1/sources/{id}` | Удаление источника |
| GET | `/api/v1/config` | Получение конфигурации |
| PUT | `/api/v1/config` | Обновление конфигурации |

### Swagger UI

Откройте http://localhost:8000/docs для интерактивной документации.

### Пример запроса

```bash
# Получить статистику
curl http://localhost:8000/api/v1/stats

# Добавить источник
curl -X POST http://localhost:8000/api/v1/sources \
  -H "Content-Type: application/json" \
  -d '{"type": "rss", "url": "https://example.com/feed.xml", "active": true}'
```

---

## 🖥️ Web UI

Веб-панель управления на базе Gradio предоставляет удобный интерфейс для:

- ✅ Проверки состояния системы (health check)
- ✅ Просмотра статистики публикаций
- ✅ Управления источниками контента
- ✅ Редактирования конфигурации
- ✅ Ручного создания постов

### Запуск Web UI

```bash
# В отдельном терминале (API должно быть запущено)
python src/web_ui.py
```

Откройте http://localhost:7860 в браузере.

### Запуск на сервере

```bash
nohup python src/web_ui.py > webui.log 2>&1 &
```

👉 [Полное руководство по Web UI](docs/WEB_UI_GUIDE.md)

---

## 🐳 Docker

### Базовая конфигурация

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VK_ACCESS_TOKEN=${VK_ACCESS_TOKEN}
      - VK_GROUP_ID=${VK_GROUP_ID}
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=postgres
  
  redis:
    image: redis:7-alpine
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

### Команды

```bash
# Запуск всех сервисов
docker compose up -d

# Запуск с профилем (например, с Ollama)
docker compose --profile with-ollama up -d

# Просмотр логов
docker compose logs -f app

# Перезапуск приложения
docker compose restart app

# Остановка и удаление
docker compose down
docker compose down -v  # С удалением volumes
```

---

## 📊 Мониторинг

### Prometheus

Метрики доступны на http://localhost:9090

**Основные метрики:**
- `pipeline_posts_processed_total` — Всего обработано постов
- `pipeline_publish_success_total` — Успешные публикации
- `pipeline_publish_failed_total` — Ошибки публикации
- `pipeline_processing_duration_seconds` — Время обработки
- `vk_api_requests_total` — Запросы к VK API

### Grafana

Дашборды доступны на http://localhost:3000 (admin/admin)

**Преднастроенные дашборды:**
- Overview — Общая статистика
- Pipeline Performance — Производительность конвейера
- Error Tracking — Отслеживание ошибок
- Resource Usage — Использование ресурсов

### Health Checks

```bash
# Проверка API
curl http://localhost:8000/health

# Проверка базы данных
curl http://localhost:8000/api/v1/health/db

# Проверка VK API
curl http://localhost:8000/api/v1/health/vk
```

---

## 🔒 Безопасность

### Рекомендации

1. **Хранение секретов**
   - ❌ Никогда не коммитьте `.env` файлы в Git
   - ✅ Используйте `.env.example` с плейсхолдерами
   - ✅ Храните секреты в CI/CD secret manager

2. **Сетевая безопасность**
   - Используйте reverse proxy (Nginx/Caddy)
   - Включите HTTPS (Let's Encrypt)
   - Настройте firewall (UFW/iptables)
   - Ограничьте доступ к админским интерфейсам

3. **Rate Limiting**
   ```bash
   # Nginx пример
   limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
   ```

4. **Fail2Ban**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

5. **SSRF Protection**
   - Встроена защита от Server-Side Request Forgery
   - Блокировка private IP диапазонов
   - DNS resolution validation

👉 [Полный аудит безопасности](SECURITY_AND_PERFORMANCE_AUDIT.md)  
👉 [Политика безопасности](SECURITY.md)

---

## 🔧 Устранение проблем

### Частые ошибки

| Проблема | Решение |
|----------|---------|
| `python` не найден | Установите Python 3.10+ и добавьте в PATH |
| Порт 8000 занят | Измените порт: `--port 8001` |
| Ошибка подключения к VK | Проверьте токен и права доступа |
| Бот Telegram не отвечает | Проверьте токен и chat_id |
| ModuleNotFoundError | Активируйте venv: `source .venv/bin/activate` |
| Ошибки зависимостей | `pip install --upgrade pip setuptools` |

### Логи

```bash
# Просмотр логов приложения
tail -f logs/app.log

# Логи systemd (VPS)
sudo journalctl -u vk-publisher -f

# Логи Docker
docker compose logs -f app
```

### Диагностика

```bash
# Проверка окружения
python scripts/test_setup.py

# Проверка VK API
python scripts/test_vk_api.py

# Проверка базы данных
python scripts/test_database.py

# Запуск тестов
pytest -v
```

👉 [Полное руководство по troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🤝 Вклад в проект

### Разработка

```bash
# Установка dev зависимостей
pip install -r requirements-dev.txt

# Pre-commit хуки
pre-commit install

# Запуск тестов
pytest -v --cov=src

# Проверка кода
bandit -r src -ll
pip-audit
```

### Pull Request Process

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

👉 [Руководство для контрибьюторов](.github/CONTRIBUTING.md)  
👉 [Code of Conduct](.github/CODE_OF_CONDUCT.md)

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для деталей.

---

## 📞 Контакты и поддержка

- **GitHub Issues**: https://github.com/ilyatestov/vk_publisher/issues
- **Документация**: https://github.com/ilyatestov/vk_publisher/tree/main/docs
- **Email**: [добавить контакт]

---

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) — современный фреймворк
- [Ollama](https://ollama.ai/) — локальные LLM модели
- [Gradio](https://gradio.app/) — быстрый Web UI
- [VK API](https://dev.vk.com/) — платформа ВКонтакте

---

*Последнее обновление: 2026-04-24*


## 🧭 Blueprint для полной документации

Для целевой структуры README (с локальным запуском, Docker Compose, TaskIQ worker, Ollama и релизами под Windows/Linux) используйте шаблон: [`docs/README_BLUEPRINT.md`](docs/README_BLUEPRINT.md).

Также общий план модернизации вынесен в [`docs/ARCHITECTURE_MODERNIZATION_PLAN.md`](docs/ARCHITECTURE_MODERNIZATION_PLAN.md).
