# Структура проекта VK Publisher (Production-ready SaaS)

Документ описывает архитектуру проекта с поддержкой Clean Architecture, мультиплатформенности и готовности к монетизации.

## 1. Корневая структура

```text
vk_publisher/
├── .github/
│   └── workflows/
│       ├── release.yml              # Сборка Windows/Linux/macOS релизов
│       ├── tests.yml                # Запуск тестов
│       ├── bandit.yml               # Security scan
│       └── docker-publish.yml       # Публикация Docker образов
│
├── src/
│   ├── domain/                      # Слой домена (бизнес-логика)
│   │   ├── __init__.py
│   │   ├── entities.py              # Сущности: Post, Account, Media, Analytics
│   │   ├── interfaces.py            # Протоколы: SocialPublisher, StorageInterface
│   │   └── publishers/
│   │       ├── __init__.py
│   │       └── base.py              # BasePublisher (абстрактный класс)
│   │
│   ├── application/                 # Слой приложений (Use Cases)
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── post_service.py      # Постинг, планирование
│   │   │   ├── scheduler_service.py # Cron, отложенные публикации
│   │   │   ├── ai_service.py        # Ollama интеграция
│   │   │   └── analytics_service.py # Метрики, отчёты
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── broker.py            # TaskIQ брокер
│   │       ├── rewrite_tasks.py     # AI рерайт задачи
│   │       ├── publish_tasks.py     # Фоновые публикации
│   │       └── moderation_tasks.py  # Модерация через Telegram
│   │
│   ├── infrastructure/              # Инфраструктурный слой
│   │   ├── __init__.py
│   │   ├── database.py              # SQLAlchemy + PostgreSQL/SQLite
│   │   ├── redis_cache.py           # Redis кэш с TTL
│   │   ├── ollama_processor.py      # Ollama клиент
│   │   ├── telegram_bot.py          # Telegram бот для модерации
│   │   ├── vk_api_client.py         # VK API клиент
│   │   └── publishers/
│   │       ├── __init__.py
│   │       ├── vk_publisher.py      # VK реализация
│   │       ├── telegram_publisher.py # Telegram реализация
│   │       └── dzen_publisher.py    # Дзен (опционально)
│   │
│   ├── interfaces/                  # Слои интерфейсов
│   │   ├── __init__.py
│   │   ├── api/                     # FastAPI REST API
│   │   │   ├── __init__.py
│   │   │   ├── app.py               # Основное приложение
│   │   │   ├── routes/
│   │   │   │   ├── posts.py         # CRUD постов
│   │   │   │   ├── accounts.py      # Управление аккаунтами
│   │   │   │   ├── analytics.py     # Статистика
│   │   │   │   └── auth.py          # JWT/OAuth2
│   │   │   ├── deps.py              # Dependency injection
│   │   │   └── middleware/
│   │   │       ├── rate_limit.py    # Rate limiting
│   │   │       └── security.py      # CORS, XSS защита
│   │   ├── web_ui/                  # Веб-дашборд
│   │   │   ├── __init__.py
│   │   │   └── dashboard.py
│   │   ├── telegram_bot/            # Telegram Mini App
│   │   │   ├── __init__.py
│   │   │   └── bot.py
│   │   └── cli/                     # CLI интерфейс
│   │       └── main.py
│   │
│   ├── core/                        # Ядро (конфигурация, логирование)
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic настройки
│   │   ├── logging.py               # Loguru конфигурация
│   │   └── exceptions.py            # Кастомные исключения
│   │
│   ├── bootstrap/                   # Инициализация приложения
│   │   ├── __init__.py
│   │   └── container.py             # DI контейнер
│   │
│   └── main.py                      # Точка входа
│
├── tests/                           # Тесты
│   ├── __init__.py
│   ├── conftest.py                  # pytest фикстуры
│   ├── unit/
│   │   ├── test_domain.py
│   │   └── test_application.py
│   ├── integration/
│   │   ├── test_vk_publisher.py
│   │   └── test_telegram_publisher.py
│   └── e2e/
│       └── test_pipeline.py
│
├── scripts/                         # Утилиты
│   ├── test_setup.py
│   ├── test_database.py
│   ├── test_vk_api.py
│   └── health_check.py
│
├── docker/                          # Docker конфигурации
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── prometheus.yml
│
├── docs/                            # Документация
│   ├── UBUNTU_VPS_INSTALL.md
│   ├── TELEGRAM_MINI_APP.md
│   └── MONETIZATION.md
│
├── .env.example                     # Пример конфигурации
├── .gitignore
├── pyproject.toml                   # Poetry/flit конфигурация
├── requirements.txt                 # pip зависимости
├── pytest.ini                       # pytest настройки
├── mypy.ini                         # mypy настройки
├── ruff.toml                        # linter настройки
├── README.md                        # Основная документация
├── README_RU.md                     # Русская версия README
└── QUICK_START_GUIDE.md             # Быстрый старт
```

## 2. Основной Python-контур (runtime)

- `src/main.py` — точка входа FastAPI приложения, lifespan, запуск pipeline, API endpoints.
- `src/workers/pipeline.py` — реализация 4-этапного конвейера обработки постов.
- `src/core/config.py` — конфигурация через Pydantic Settings (`.env`, nested и legacy env).
- `src/infrastructure/` — интеграции с внешними системами (VK, DB, Telegram, Ollama).
- `src/domain/` — доменные сущности и интерфейсы.
- `src/content_fetcher/` — модули получения контента (RSS/VK/Web).
- `src/web_ui.py` — операторская панель Gradio (часть кнопок пока как заглушки).

## 3. Асинхронный pipeline

```
fetch → rewrite (Ollama) → moderate → enrich (hashtags) → publish → analytics
  ↓         ↓                ↓            ↓                ↓         ↓
RSS     TaskIQ          Telegram     AI Service      VK/Tele   Prometheus
VK      Background      Bot          Hashtags       Dzen      Grafana
```

## 4. Мультиплатформенность

```python
# Интерфейс для всех платформ
from src.domain.publishers.base import BasePublisher, PublishPayload, PublishResult

class VkPublisher(BasePublisher):
    platform = "vk"
    async def publish(self, payload: PublishPayload) -> PublishResult: ...
    
class TelegramPublisher(BasePublisher):
    platform = "telegram"
    async def publish(self, payload: PublishPayload) -> PublishResult: ...
    
class DzenPublisher(BasePublisher):
    platform = "dzen"
    async def publish(self, payload: PublishPayload) -> PublishResult: ...
```

## 5. PHP package внутри репозитория

Для совместимости и отдельного использования как composer package:

- `src/Client/`, `src/Services/`, `src/DTO/`, `src/Config/`, `src/Exceptions/`.
- Фокус: строго типизированный VK client и сервисы публикации/медиа.
- Тесты: `tests/Unit/*.php`.

## 6. Что считать основным путём запуска

Для новой установки ориентируйтесь на Python-контур:

1. `uvicorn src.main:app`
2. `scripts/test_setup.py`
3. `src/web_ui.py` (опционально)
4. `docker compose up -d` для контейнерного окружения

PHP-часть используйте отдельно, если нужен composer package-клиент.

## 7. Структурные рекомендации

### Уже принято в проекте
- Разделение на `domain / infrastructure / workers`.
- Вынос deployment-инструкций в `docs/`.
- Подготовка окружения через `.env.example`.

### Рекомендации на ближайшее развитие
1. Явно отметить legacy-модули в `src/` и зафиксировать roadmap удаления дублей.
2. Добавить `docs/ARCHITECTURE.md` с диаграммой потока данных.
3. Разделить README на две части: `README.md` (Python runtime) и `README_PHP.md` (package).
4. Вынести политику версионирования и release-процесс в `docs/RELEASE.md`.

## 8. Какие файлы редактировать при типичных задачах

- Интеграции и API: `src/main.py`, `src/infrastructure/*`, `src/workers/*`
- Настройка окружения: `.env.example`, `src/core/config.py`, `docs/*INSTALL*.md`
- UI: `src/web_ui.py`, `docs/WEB_UI_GUIDE.md`
- VK ключи/доступы: `docs/VK_API_SETUP.md`
- Операционные инструкции: `docs/UBUNTU_VPS_INSTALL.md`, `docs/WINDOWS_INSTALL.md`
