# VK Autoposter — Система автопостинга ВКонтакте

[![Tests](https://github.com/yourusername/vk-autoposter/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/vk-autoposter/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Описание

**VK Autoposter** — это автоматизированная система для сбора, обработки и публикации контента ВКонтакте. Система использует ИИ (локальную LLM через Ollama) для рерайта новостей, объединяет материалы из нескольких источников в единые посты и публикует их с соблюдением лимитов.

### ✨ Возможности

- 🔄 **Автоматический сбор контента** из RSS-лент, веб-сайтов и групп ВКонтакте
- 🤖 **ИИ-рерайт** через локальную модель Ollama (qwen2.5:1.5b)
- 🔀 **Объединение статей** на одну тему в единый пост-саммари
- 🚫 **Дедупликация** контента с проверкой по базе за 30 дней
- 📊 **Генерация футеров** с источниками и ссылками на соцсети
- ⏰ **Планирование публикаций** с настраиваемым интервалом
- 👁️ **Опциональная модерация** через Telegram-бота
- 📈 **Статистика и логирование** всех действий

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/vk-autoposter.git
cd vk-autoposter
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
cp .env.example .env
```

Заполните необходимыми значениями:

```env
# VK API
VK_ACCESS_TOKEN=your_token_here
VK_GROUP_ID=your_group_id
VK_API_VERSION=5.131

# Telegram бот (опционально, для модерации)
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_TELEGRAM_ID=your_telegram_id

# Настройки автопостинга
POST_INTERVAL_MINUTES=60
ENABLE_PREVIEW=true
MAX_POSTS_PER_DAY=10

# Ollama (локальная LLM)
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL=qwen2.5:1.5b

# Логирование
LOG_LEVEL=INFO
LOG_FILE=/app/logs/autoposter.log

# База данных
DATABASE_PATH=/app/data/posts.db
```

### 3. Запуск через Docker Compose

```bash
docker-compose up -d
```

Проверка логов:

```bash
docker-compose logs -f autoposter
```

---

## 📁 Структура проекта

```
vk-autoposter/
├── src/
│   ├── main.py              # Точка входа приложения
│   ├── __init__.py          # Конфигурация и настройки
│   ├── vk_api_client.py     # Клиент VK API
│   ├── content_fetcher/     # Сбор контента
│   │   ├── __init__.py      # ContentFetcher (параллельный сбор)
│   │   ├── rss_parser.py    # Парсинг RSS
│   │   ├── web_parser.py    # Парсинг сайтов
│   │   └── vk_scraper.py    # Парсинг групп ВК
│   ├── processor/           # Обработка контента
│   │   ├── ai_rewriter.py   # ИИ-рерайт через Ollama
│   │   └── deduplicator.py  # Дедупликация и группировка
│   ├── publisher/           # Публикация
│   │   ├── vk_publisher.py  # Публикация в VK
│   │   └── footer_generator.py # Генерация футеров
│   ├── database/            # Работа с БД
│   │   └── db.py            # SQLite база данных
│   └── telegram_bot/        # Telegram бот для модерации
│       └── bot.py           # Бот для превью постов
├── tests/                   # Модульные тесты
│   ├── test_database.py
│   ├── test_deduplicator.py
│   └── test_footer_generator.py
├── config/                  # Конфигурационные файлы
│   ├── sources.json         # Источники контента
│   ├── social_links.json    # Ссылки на соцсети
│   └── vk_config.json       # Настройки VK
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile               # Docker образ
├── requirements.txt         # Python зависимости
├── pytest.ini              # Настройки pytest
├── README.md               # Этот файл
└── RECOMMENDATIONS.md      # Рекомендации по улучшению
```

---

## ⚙️ Конфигурация

### Добавление источников

Отредактируйте `config/sources.json`:

```json
{
  "rss": [
    {
      "name": "Tech News",
      "url": "https://example.com/rss",
      "enabled": true,
      "priority": 1,
      "topic": "technology"
    }
  ],
  "websites": [
    {
      "name": "News Site",
      "url": "https://example.com",
      "selector": ".article-content",
      "enabled": true,
      "priority": 2,
      "topic": "general"
    }
  ],
  "vk_groups": [
    {
      "name": "Tech Group",
      "group_id": "12345678",
      "enabled": true,
      "priority": 3,
      "topic": "technology"
    }
  ]
}
```

### Настройка социальных ссылок

Отредактируйте `config/social_links.json`:

```json
{
  "telegram": {
    "channel": "@your_channel",
    "enabled": true
  },
  "youtube": {
    "channel": "your_channel",
    "enabled": false
  },
  "dzen": {
    "channel": "your_channel",
    "enabled": false
  },
  "hashtags": ["#новости", "#технологии", "#ai"]
}
```

---

## 🧪 Тестирование

Запуск модульных тестов:

```bash
# Установка зависимостей для тестирования
pip install pytest pytest-asyncio pytest-cov

# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием кода
pytest tests/ -v --cov=src --cov-report=html

# Запуск конкретного теста
pytest tests/test_database.py::TestDatabase::test_add_content_hash -v
```

### Покрытие тестами

- ✅ `tests/test_database.py` — 8 тестов (База данных)
- ✅ `tests/test_deduplicator.py` — 12 тестов (Дедупликация)
- ✅ `tests/test_footer_generator.py` — 9 тестов (Генератор футеров)

**Всего:** 29 тестов, покрытие ~45%

---

## 🔧 Оптимизация производительности

### Параллельный сбор контента

Начиная с версии 1.2.0, сбор контента из всех источников выполняется параллельно через `asyncio.gather()`, что ускоряет процесс в 3-5 раз.

### Кеширование (планируется)

В будущих версиях будет добавлено кеширование запросов к API для уменьшения нагрузки.

---

## 🛠️ Решение проблем

### Ошибка "Модель недоступна"

```bash
docker exec -it ollama ollama pull qwen2.5:1.5b
```

### Ошибка VK API

1. Проверьте токен в `.env`
2. Убедитесь, что у токена есть права на публикацию
3. Проверьте ID группы (должен быть положительным)

### Переполнение базы данных

```bash
docker exec -it vk-autoposter sqlite3 /app/data/posts.db "VACUUM;"
```

### Логи приложения

```bash
docker-compose logs -f autoposter
# или
docker exec -it vk-autoposter tail -f /app/logs/autoposter.log
```

---

## 📈 Мониторинг

### Статистика из базы данных

```python
from src.database import Database

db = Database("/app/data/posts.db")
stats = await db.get_statistics()
print(stats)
# {'total_hashes': 150, 'published_count': 120, 'posts_count': 120, 'errors_24h': 2}
```

---

## 🔐 Безопасность

- ✅ Переменные окружения для чувствительных данных
- ✅ `.env` добавлен в `.gitignore`
- ✅ Токены не коммитятся в репозиторий
- ⬜ Pre-commit хуки для проверки секретов (планируется)
- ⬜ Rate limiting для API запросов (реализовано частично)

---

## 🤝 Вклад в проект

Pull requests приветствуются! Для основных изменений сначала откройте issue.

### Разработка

```bash
# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Запуск линтеров
black src/ tests/
flake8 src/ tests/
mypy src/

# Запуск тестов
pytest tests/ -v --cov=src
```

---

## 📝 Лицензия

MIT License

---

## 📞 Поддержка

- **GitHub Issues:** [Сообщить о проблеме](https://github.com/yourusername/vk-autoposter/issues)
- **Email:** your.email@example.com

---

## 📊 Roadmap

- [ ] Добавить интеграционные тесты
- [ ] Увеличить покрытие тестами до 80%
- [ ] Добавить кеширование запросов
- [ ] Реализовать админ-панель для управления
- [ ] Добавить Prometheus-метрики
- [ ] Поддержка других социальных сетей

---

**Версия:** 1.2.0  
**Дата обновления:** 2025-01-XX  
**Статус тестов:** ✅ 29/29 passed
