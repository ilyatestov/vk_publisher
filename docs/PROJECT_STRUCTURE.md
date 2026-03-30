# Структура проекта VK Publisher

Документ объясняет, как устроен репозиторий, какие части являются «боевыми», а какие — вспомогательными/legacy.

## 1. Корневая структура

```text
vk_publisher/
├── src/                     # Основной код приложения (Python + PHP package classes)
├── docs/                    # Документация по установке и эксплуатации
├── tests/                   # Тесты Python и PHPUnit
├── scripts/                 # Утилиты проверки окружения/здоровья
├── config/                  # JSON-конфиги источников и соц.ссылок
├── docker/                  # Конфиги Docker/Prometheus
├── monitoring/              # Конфиги Grafana/Prometheus дашбордов
├── README.md                # Главная точка входа
├── requirements.txt         # Python зависимости
├── composer.json            # PHP package зависимости
└── docker-compose.yml       # Локальный/серверный orchestration
```

## 2. Основной Python-контур (runtime)

- `src/main.py` — точка входа FastAPI приложения, lifespan, запуск pipeline, API endpoints.
- `src/workers/pipeline.py` — реализация 4-этапного конвейера обработки постов.
- `src/core/config.py` — конфигурация через Pydantic Settings (`.env`, nested и legacy env).
- `src/infrastructure/` — интеграции с внешними системами (VK, DB, Telegram, Ollama).
- `src/domain/` — доменные сущности и интерфейсы.
- `src/content_fetcher/` — модули получения контента (RSS/VK/Web).
- `src/web_ui.py` — операторская панель Gradio (часть кнопок пока как заглушки).

## 3. PHP package внутри репозитория

Для совместимости и отдельного использования как composer package:

- `src/Client/`, `src/Services/`, `src/DTO/`, `src/Config/`, `src/Exceptions/`.
- Фокус: строго типизированный VK client и сервисы публикации/медиа.
- Тесты: `tests/Unit/*.php`.

## 4. Что считать основным путём запуска

Для новой установки ориентируйтесь на Python-контур:

1. `uvicorn src.main:app`
2. `scripts/test_setup.py`
3. `src/web_ui.py` (опционально)
4. `docker compose up -d` для контейнерного окружения

PHP-часть используйте отдельно, если нужен composer package-клиент.

## 5. Структурные рекомендации

### Уже принято в проекте
- Разделение на `domain / infrastructure / workers`.
- Вынос deployment-инструкций в `docs/`.
- Подготовка окружения через `.env.example`.

### Рекомендации на ближайшее развитие
1. Явно отметить legacy-модули в `src/` и зафиксировать roadmap удаления дублей.
2. Добавить `docs/ARCHITECTURE.md` с диаграммой потока данных.
3. Разделить README на две части: `README.md` (Python runtime) и `README_PHP.md` (package).
4. Вынести политику версионирования и release-процесс в `docs/RELEASE.md`.

## 6. Какие файлы редактировать при типичных задачах

- Интеграции и API: `src/main.py`, `src/infrastructure/*`, `src/workers/*`
- Настройка окружения: `.env.example`, `src/core/config.py`, `docs/*INSTALL*.md`
- UI: `src/web_ui.py`, `docs/WEB_UI_GUIDE.md`
- VK ключи/доступы: `docs/VK_API_SETUP.md`
- Операционные инструкции: `docs/UBUNTU_VPS_INSTALL.md`, `docs/WINDOWS_INSTALL.md`
