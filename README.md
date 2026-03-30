# VK Publisher

VK Publisher — это репозиторий с двумя направлениями:

1. **Основное приложение (Python/FastAPI)** для автоматизации публикаций во ВКонтакте.
2. **PHP-библиотека (`vk-publisher/vk-publisher`)** для безопасной публикации через VK API.

> Ниже основной фокус — эксплуатация Python-приложения (API, pipeline, модерация, деплой).

## Что умеет проект

### Основной runtime (Python)
- Асинхронный конвейер обработки контента: `fetch -> AI rewrite -> moderation -> publish`.
- FastAPI API с endpoint'ами: `/`, `/health`, `/metrics`, `/api/v1/stats`.
- Сохранение состояния/постов в БД (SQLite или PostgreSQL через SQLAlchemy Async).
- Интеграция с VK API для публикации.
- Модерация через Telegram-бота.
- Интеграция с Ollama для AI-рерайта (опционально).
- Gradio Web UI для операторских задач (частично функциональный интерфейс).
- Набор тестов на Python (`pytest`) и отдельные PHP unit-тесты.

### PHP-библиотека
- VK API client на Guzzle, retry/backoff, typed exceptions, DTO, сервисы публикации и загрузки медиа.
- Подходит как отдельный package через Composer.

---

## Быстрый старт (локально)

### 1) Клонирование и окружение
```bash
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Конфиг
```bash
cp .env.example .env
```

Минимально заполните:
- `VK_ACCESS_TOKEN`
- `VK_GROUP_ID`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_MODERATOR_CHAT_ID`

### 3) Проверка готовности
```bash
python scripts/test_setup.py
```

### 4) Запуск API
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Полезные URL:
- API root: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`

### 5) (Опционально) запуск Web UI
```bash
python src/web_ui.py
```
Откройте `http://localhost:7860`.

---

## Документация

- [Установка на Ubuntu/VPS](docs/UBUNTU_VPS_INSTALL.md)
- [Установка на Windows](docs/WINDOWS_INSTALL.md)
- [Настройка VK API и Telegram](docs/VK_API_SETUP.md)
- [Web UI: запуск и ограничения](docs/WEB_UI_GUIDE.md)
- [Структура проекта (подробно)](docs/PROJECT_STRUCTURE.md)
- [Канонические архитектурные пути](docs/CANONICAL_ARCHITECTURE.md)
- [Миграция по PHP-библиотеке](docs/MIGRATION.md)
- [Рекомендации и улучшения](RECOMMENDATIONS.md)

---

## Конфигурация `.env`

Проект поддерживает **оба варианта** переменных:
- Плоские (legacy): `VK_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, ...
- Nested (`__`): `VK__ACCESS_TOKEN`, `TELEGRAM__TOKEN`, ...

Рекомендуется использовать плоские ключи из `.env.example` для простоты.

---

## Запуск через Docker Compose

```bash
docker compose up -d
```

Сервисы:
- `app` (FastAPI)
- `db` (PostgreSQL)
- `redis`
- `prometheus`
- `grafana`
- `ollama` (по профилю `with-ollama`)

Остановка:
```bash
docker compose down
```

---

## Проверка качества

### Python
```bash
pytest
```

### PHP library
```bash
composer install
composer test
composer stan
composer cs:check
```

---

## Рекомендованная структура эксплуатации

1. Сначала поднять API и проверить `/health`.
2. Проверить конфиг и токены через `scripts/test_setup.py`.
3. Включать Ollama только при необходимости AI-рерайта.
4. Для продакшена использовать systemd + reverse proxy (Nginx/Caddy).
5. Использовать Prometheus/Grafana для мониторинга.

---

## Лицензия

MIT
