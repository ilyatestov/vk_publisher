# VK Publisher v2.0

Асинхронное приложение для автопостинга ВКонтакте с использованием Clean Architecture, ИИ-обработки контента и Telegram модерации.

## 🚀 Особенности

- **Clean Architecture** - разделение на domain, infrastructure, application слои
- **Конвейерная обработка** - 4 воркера через asyncio.Queue (fetcher, processor, moderation, publisher)
- **REST API** - FastAPI с автоматической документацией (Swagger/OpenAPI)
- **Метрики Prometheus** - мониторинг производительности и ошибок
- **Telegram модерация** - aiogram 3.x для одобрения постов перед публикацией
- **ИИ-рерайт** - Ollama (локальная LLM) для переписывания контента
- **База данных** - SQLAlchemy + asyncpg (PostgreSQL) / aiosqlite (SQLite)
- **Docker** - multi-stage сборка, docker-compose для production

## 📁 Структура проекта

```
vk_publisher/
├── src/
│   ├── core/              # Конфигурация, логирование, исключения
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── domain/            # Бизнес-сущности и интерфейсы
│   │   ├── entities.py
│   │   └── interfaces.py
│   ├── infrastructure/    # Реализации интерфейсов
│   │   ├── vk_api_client.py
│   │   ├── ollama_processor.py
│   │   ├── database.py
│   │   └── telegram_bot.py
│   ├── workers/           # Конвейерные воркеры
│   │   └── pipeline.py
│   ├── presentation/      # REST API endpoints
│   └── main.py            # Точка входа
├── tests/                 # Unit и integration тесты
├── docker/                # Docker конфигурации
├── .env.example           # Шаблон переменных окружения
├── docker-compose.yml     # Docker Compose для production
└── requirements.txt       # Python зависимости
```

## 🔧 Установка

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/vk_publisher.git
cd vk_publisher
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # для разработки
```

4. Скопируйте `.env.example` в `.env` и заполните значения:
```bash
cp .env.example .env
```

5. Запустите приложение:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

6. Откройте Swagger UI: http://localhost:8000/docs

### Docker Compose (Production)

1. Заполните `.env` файл необходимыми токенами:
```bash
VK_ACCESS_TOKEN=your_vk_token
VK_GROUP_ID=your_group_id
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_TELEGRAM_ID=your_telegram_id
ENCRYPTION_KEY=your_32_char_encryption_key
```

2. Запустите все сервисы:
```bash
docker-compose up -d
```

3. Проверьте статус:
```bash
docker-compose ps
```

4. Остановите сервисы:
```bash
docker-compose down
```

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `VK__ACCESS_TOKEN` | Токен доступа к VK API | `abc123...` |
| `VK__GROUP_ID` | ID группы ВКонтакте | `123456789` |
| `TELEGRAM__TOKEN` | Токен Telegram бота | `123456:ABC-DEF...` |
| `TELEGRAM__MODERATOR_CHAT_ID` | ID чата модератора | `987654321` |
| `OLLAMA__BASE_URL` | URL Ollama сервера | `http://ollama:11434` |
| `OLLAMA__MODEL_NAME` | Модель для рерайта | `qwen2.5:1.5b` |
| `DATABASE__URL` | Connection string БД | `postgresql+asyncpg://...` |
| `SCHEDULER__MAX_DAILY_POSTS` | Лимит постов в день | `50` |

## 📊 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/` | GET | Информация о приложении |
| `/health` | GET | Health check для Docker/K8s |
| `/metrics` | GET | Метрики Prometheus |
| `/api/v1/stats` | GET | Статистика по постам |
| `/docs` | GET | Swagger UI документация |

## 🏗️ Архитектура

### Слои приложения

1. **Domain Layer** (`src/domain/`)
   - Сущности: `SocialPost`, `VKAccount`
   - Интерфейсы: `SocialPublisherInterface`, `AIProcessorInterface`, etc.

2. **Infrastructure Layer** (`src/infrastructure/`)
   - Реализации интерфейсов: `VKClient`, `OllamaProcessor`, `DatabaseStorage`, `TelegramModeratorBot`

3. **Application Layer** (`src/application/`)
   - Use cases и бизнес-логика

4. **Presentation Layer** (`src/presentation/`)
   - REST API endpoints (FastAPI)

### Конвейер обработки

```
[Sources] → [Fetcher Worker] → [Processor Worker] → [Moderation Worker] → [Publisher Worker] → [VK]
                    ↓                  ↓                    ↓                      ↓
               asyncio.Queue    asyncio.Queue        asyncio.Queue          asyncio.Queue
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src --cov-report=html

# Запуск конкретного теста
pytest tests/test_database.py -v
```

## 📈 Мониторинг

### Prometheus

Откройте http://localhost:9090 для просмотра метрик:
- Количество запросов к API
- Время ответа
- Количество ошибок
- Длина очередей задач

### Grafana

Откройте http://localhost:3000 (admin/admin):
- Готовые дашборды для мониторинга
- Графики производительности
- Алерты при ошибках

## 🔐 Безопасность

- Маскировка чувствительных данных в логах
- Шифрование токенов (опционально)
- Non-root пользователь в Docker контейнере
- Health checks для всех сервисов

## 🤝 Contributing

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 License

MIT License

## 📞 Контакты

- Telegram: @yourusername
- Email: your@email.com
