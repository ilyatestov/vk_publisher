# 🚀 VK Publisher — Production-Ready SaaS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com/)
[![CI/CD](https://github.com/ilyatestov/vk_publisher/actions/workflows/release.yml/badge.svg)](https://github.com/ilyatestov/vk_publisher/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/ilyatestov/vk_publisher)](https://github.com/ilyatestov/vk_publisher/releases)

**VK Publisher** — масштабируемый SaaS-сервис для автопостинга ВКонтакте с поддержкой AI-рерайта, мультиплатформенности (VK, Telegram, Дзен), планирования публикаций и готовностью к монетизации.

---

## 📋 Оглавление

- [Возможности](#-возможности)
- [🔥 Быстрый старт (5 минут)](#-быстрый-старт-5-минут)
- [📖 Подробная установка](#-подробная-установка)
- [⚙️ Конфигурация](#️-конфигурация)
- [🏗️ Архитектура](#️-архитектура)
- [🎵 Музыкальные проекты](#-музыкальные-проекты)
- [💰 Монетизация](#-монетизация)
- [🔐 Безопасность](#-безопасность)
- [🧪 Тестирование](#-тестирование)
- [📡 API Документация](#-api-документация)
- [🖥️ Web UI](#️-web-ui)
- [🐳 Docker](#-docker)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 Лицензия](#-лицензия)

---

## ✨ Возможности

### Основной функционал

| Функция | Описание |
|---------|----------|
| 🔄 **Авто-сбор контента** | Парсинг RSS, веб-страниц, VK-пабликов по расписанию |
| 🤖 **AI-рерайтинг** | Интеграция с Ollama (Llama 3, Mistral) для уникализации |
| ✅ **Модерация** | Подтверждение постов через Telegram-бота или Web UI |
| 📅 **Планировщик** | Отложенная публикация, cron-расписание, учёт лимитов |
| 🔁 **Дедупликация** | Exact + near-duplicate защита от дублей |
| 🌐 **Мультипостинг** | VK + Telegram + Дзен + Одноклассники (адаптеры) |
| 📊 **Аналитика** | Просмотры, лайки, вовлечённость, AI-инсайты |
| 🎵 **Аудио-контент** | Генерация музыки (YuE, ACE-Step), обложки, метаданные |
| 💰 **Тарифы** | Free/Pro планы, лимиты, партнёрские ссылки |

### Технические преимущества

- **Clean Architecture** — domain/application/infrastructure/interfaces
- **Асинхронный pipeline** — fetch → rewrite → moderate → publish → analytics
- **TaskIQ + Redis** — фоновые задачи, очереди, retry с jitter
- **Circuit Breaker** — защита от сбоев внешних сервисов
- **Идемпотентность** — хэш контента в БД, защита от дублей
- **Rate Limiting** — slowapi middleware для защиты API
- **JWT/OAuth2** — безопасные админские эндпоинты
- **Шифрование токенов** — cryptography.Fernet в БД

---

## 🚀 Быстрый старт (5 минут)

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Клонирование
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher

# Настройка (.env)
cp .env.example .env
nano .env  # Заполните VK_ACCESS_TOKEN, TELEGRAM_BOT_TOKEN

# Запуск
docker compose up -d

# С Ollama (для AI)
docker compose --profile with-ollama up -d

# Проверка
curl http://localhost:8000/health
```

**Готово!** Откройте:
- **API**: http://localhost:8000/docs
- **Web UI**: http://localhost:7860
- **Grafana**: http://localhost:3000 (admin/admin)

### Вариант 2: Локальный запуск (Python)

```bash
# Python 3.11+
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
cp .env.example .env
nano .env

# Запуск API
uvicorn src.main:app --host 0.0.0.0 --port 8000

# В другом терминале: Web UI
python src/web_ui.py
```

### Вариант 3: Готовый .exe (Windows)

1. Скачайте последний релиз: https://github.com/ilyatestov/vk_publisher/releases
2. Распакуйте `vk_publisher-vX.X.X-windows.zip`
3. Отредактируйте `.env.example` → переименуйте в `.env`
4. Запустите `start.bat`

---

## 📖 Подробная установка

### Для Ubuntu/Debian VPS

```bash
# Обновление
sudo apt update && sudo apt upgrade -y

# Зависимости
sudo apt install -y git curl wget build-essential python3.11 python3.11-venv postgresql redis-server

# Проект
cd ~
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher

# Установка
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Настройка
cp .env.example .env
nano .env

# systemd service
sudo nano /etc/systemd/system/vk-publisher.service
```

👉 [Полная инструкция для Ubuntu VPS](docs/UBUNTU_VPS_INSTALL.md)

### Для Windows 10/11

```bat
# Python 3.11+ (добавьте в PATH при установке)
# https://www.python.org/downloads/windows/

cd %USERPROFILE%
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
notepad .env

uvicorn src.main:app --host 0.0.0.0 --port 8000
```

👉 [Полная инструкция для Windows](docs/WINDOWS_INSTALL.md)

### Через PyInstaller (сборка .exe)

```bash
# Linux/macOS
pip install pyinstaller
pyinstaller --onefile --name=vk_publisher src/main.py

# Windows (PowerShell)
pip install pyinstaller
pyinstaller --onefile --name=vk_publisher-windows src/main.py
```

---

## ⚙️ Конфигурация

### Обязательные переменные (.env)

| Переменная | Описание | Пример |
|------------|----------|--------|
| `VK_ACCESS_TOKEN` | Токен VK API (Stand-alone) | `abc123...` |
| `VK_GROUP_ID` | ID сообщества VK | `123456789` |
| `TELEGRAM_BOT_TOKEN` | Токен бота для модерации | `123456:ABCdef...` |
| `TELEGRAM_MODERATOR_CHAT_ID` | Ваш Chat ID | `987654321` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/vk_publisher` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379/0` |
| `ENCRYPTION_KEY` | Ключ шифрования (32+ символа) | `your_secret_key_here_32chars!` |

### Опциональные переменные

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OLLAMA_BASE_URL` | URL Ollama для AI | `http://localhost:11434` |
| `LLM_MODEL` | Модель для рерайта | `llama3:8b` |
| `MAX_POSTS_PER_DAY` | Лимит постов в день | `50` |
| `TASKIQ_REDIS_URL` | Redis для TaskIQ | `redis://localhost:6379/1` |
| `JWT_SECRET_KEY` | Секрет для JWT | `auto-generated` |
| `LOG_LEVEL` | Уровень логов | `INFO` |

### Получение токенов

**VK Access Token:**
1. https://dev.vk.com/my-apps → Создать Standalone-приложение
2. URL: `https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,offline&response_type=token&v=5.199`
3. Скопируйте токен из адресной строки

**Telegram Bot Token:**
1. @BotFather → `/newbot`
2. Следуйте инструкциям

**Telegram Chat ID:**
1. @userinfobot → отправьте сообщение
2. Скопируйте ID

👉 [Подробно о VK API](docs/VK_API_SETUP.md)

---

## 🏗️ Архитектура

### Clean Architecture

```
src/
├── domain/           # Сущности: Post, Account, Media, Analytics
├── application/      # UseCases: PostService, SchedulerService, AIService
├── infrastructure/   # Реализации: VKClient, TelegramClient, OllamaClient
├── interfaces/       # API (FastAPI), CLI, Web UI, Telegram Bot
├── workers/          # TaskIQ воркеры
└── main.py           # Точка входа
```

### Pipeline обработки

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Fetch     │────▶│ AI Rewrite   │────▶│  Moderate   │────▶│   Publish    │
│ (RSS/Web/VK)│     │   (Ollama)   │     │ (Telegram)  │     │ (VK/TG/etc)  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                                   │
                                                                   ▼
                                                            ┌──────────────┐
                                                            │  Analytics   │
                                                            └──────────────┘
```

### Интерфейс мультиплатформенности

```python
from typing import Protocol

class SocialPublisher(Protocol):
    async def publish(self, post: Post) -> PublishResult: ...
    async def validate_credentials(self) -> bool: ...
    async def get_rate_limits(self) -> RateLimitInfo: ...

# Реализации: VkPublisher, TelegramPublisher, DzenPublisher
```

👉 [Подробнее об архитектуре](docs/CANONICAL_ARCHITECTURE.md)

---

## 🎵 Музыкальные проекты

VK Publisher поддерживает монетизацию AI-генерируемой музыки:

### Интеграция с YuE / ACE-Step

```bash
# Установка аудио-зависимостей
pip install -r requirements.txt[audio]

# Настройка в .env
AUDIO_GENERATION_ENABLED=true
YUE_MODEL_PATH=/path/to/yue.pt
ACE_STEP_MODEL_PATH=/path/to/ace-step.pt
```

### Авто-публикация треков

1. Генерация музыки через локальную нейросеть
2. Авто-создание обложки (AI)
3. Заполнение метаданных (исполнитель, жанр, теги)
4. Публикация в VK Музыку / Яндекс.Музыку

### Пример использования

```python
from src.infrastructure.audio.yue_client import YueClient

yue = YueClient(model_path="models/yue.pt")
track = await yue.generate(prompt="lo-fi hip hop beat", duration=120)
await publisher.publish_track(track, platform="vk_music")
```

---

## 💰 Монетизация

### Система тарифов

| Тариф | Цена | Лимиты |
|-------|------|--------|
| **Free** | 0 ₽ | 1 группа, 10 постов/день, базовый AI |
| **Pro** | 990 ₽/мес | 10 групп, безлимит постов, приоритетный AI |
| **Business** | 2990 ₽/мес | Безлимит групп, API доступ, white-label |

### Партнёрские ссылки

В настройках можно добавить партнёрские ссылки на:
- Хостинг (Timeweb, Reg.ru)
- VPN (NordVPN, ExpressVPN)
- AI-сервисы (Ollama Pro, OpenAI)

### API как сервис

Документация для сторонних разработчиков доступна по `/docs` после включения в конфиге:

```dotenv
API_PUBLIC_DOCS=true
```

---

## 🔐 Безопасность

### Рекомендации

1. **Хранение секретов**
   - ❌ Не коммитьте `.env` в Git
   - ✅ Используйте HashiCorp Vault (prod)
   - ✅ Secrets в CI/CD

2. **Сетевая безопасность**
   - Reverse proxy (Nginx/Caddy)
   - HTTPS (Let's Encrypt)
   - Firewall (UFW)
   - Rate limiting

3. **Шифрование**
   - Токены в БД шифруются через `cryptography.Fernet`
   - JWT для админских эндпоинтов

4. **Audit Log**
   ```bash
   # Просмотр критических действий
   curl http://localhost:8000/api/v1/audit-log
   ```

👉 [Полный аудит безопасности](SECURITY_AND_PERFORMANCE_AUDIT.md)

---

## 🧪 Тестирование

```bash
# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Запуск тестов
pytest -v --cov=src

# Type checking
mypy src --strict

# Linting
ruff check src
bandit -r src -ll

# Security scan
semgrep --config auto src
```

### Покрытие

Требуется ≥80% для критических модулей:
- `src/domain/`
- `src/application/`
- `src/infrastructure/publishers/`

---

## 📡 API Документация

После запуска откройте http://localhost:8000/docs

### Основные endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/health` | Health check |
| GET | `/api/v1/stats` | Статистика |
| GET | `/api/v1/posts` | Список постов |
| POST | `/api/v1/posts` | Создание поста |
| GET | `/api/v1/sources` | Источники |
| POST | `/api/v1/sources` | Добавить источник |
| GET | `/api/v1/analytics` | Аналитика |
| POST | `/api/v1/publish/{id}` | Опубликовать |

---

## 🖥️ Web UI

### Запуск

```bash
python src/web_ui.py
```

Откройте http://localhost:7860

### Функции

- ✅ Календарь публикаций (drag-and-drop)
- ✅ Предпросмотр поста
- ✅ Статистика в реальном времени
- ✅ Логи и audit trail
- ✅ Мастер первого запуска

### Telegram Mini App (TWA)

Приоритетный сценарий:
1. Бот присылает: "Новый пост на модерацию"
2. Кнопка "Открыть редактор" → Web App в Telegram
3. Правки → "Опубликовать" → без перехода в браузер

---

## 🐳 Docker

### Команды

```bash
# Запуск
docker compose up -d

# С Ollama
docker compose --profile with-ollama up -d

# Логи
docker compose logs -f app

# Остановка
docker compose down
```

### Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| `app` | 8000 | FastAPI приложение |
| `db` | 5432 | PostgreSQL |
| `redis` | 6379 | Redis кэш/очереди |
| `prometheus` | 9090 | Метрики |
| `grafana` | 3000 | Дашборды |
| `ollama` | 11434 | AI модели (опционально) |

---

## 🔧 Troubleshooting

### Частые проблемы

| Проблема | Решение |
|----------|---------|
| Порт 8000 занят | `--port 8001` |
| Ошибка VK API | Проверьте токен и права |
| ModuleNotFoundError | Активируйте venv |
| Бот не отвечает | Проверьте токен и chat_id |

### Диагностика

```bash
python scripts/test_setup.py
python scripts/test_vk_api.py
tail -f logs/app.log
```

👉 [Полный troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🤝 Contributing

### Pull Request Process

1. Fork
2. Feature branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open PR

### Разработка

```bash
pip install -r requirements-dev.txt
pre-commit install
pytest -v --cov=src
```

---

## 📄 Лицензия

MIT License — см. [LICENSE](LICENSE)

---

## 📞 Поддержка

- **GitHub Issues**: https://github.com/ilyatestov/vk_publisher/issues
- **Релизы**: https://github.com/ilyatestov/vk_publisher/releases
- **Документация**: https://github.com/ilyatestov/vk_publisher/tree/main/docs

---

*Последнее обновление: 2026-04-24*
