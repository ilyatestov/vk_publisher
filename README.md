# 🚀 Система автопостинга ВКонтакте

Полностью бесплатная, самописная система для автоматической публикации контента в группу ВКонтакте с функциями сбора, обработки и рерайта через ИИ.

## ✨ Возможности

- **Сбор контента** из RSS-лент, веб-сайтов и групп ВКонтакте
- **Проверка дубликатов** через SHA256 хеширование
- **Объединение одинаковых статей** в один пост
- **ИИ-рерайт** через локальную модель (Ollama)
- **Авто-футер** с ссылками на источники и соцсети
- **Модерация через Telegram** перед публикацией
- **Логирование** всех действий в SQLite

## 📋 Требования

- Docker и Docker Compose
- Python 3.10+
- Токен сообщества ВКонтакте
- (Опционально) Токен Telegram бота

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                   ИСТОЧНИКИ КОНТЕНТА                     │
│  RSS-ленты │ Парсинг сайтов │ VK API │ Telegram каналы  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   БЛОК ОБРАБОТКИ                         │
│  Нормализация → Дедупликация → ИИ-рерайт → Футеры      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   БЛОК ПУБЛИКАЦИИ                        │
│  Telegram модерация → VK API wall.post → Логирование   │
└─────────────────────────────────────────────────────────┘
```

## ⚙️ Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd vk-autoposter
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# VK API настройки
VK_ACCESS_TOKEN=your_vk_access_token_here
VK_GROUP_ID=your_group_id_here
VK_API_VERSION=5.131

# Telegram бот для модерации
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_TELEGRAM_ID=your_admin_telegram_id_here

# Настройки автопостинга
POST_INTERVAL_MINUTES=60
ENABLE_PREVIEW=true
MAX_POSTS_PER_DAY=10

# Ollama (локальная LLM)
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL=qwen2.5:1.5b
```

### 3. Настройка источников контента

Отредактируйте `config/sources.json`:

```json
{
  "rss": [
    {
      "url": "https://dtf.ru/rss",
      "topic": "игры и развлечения",
      "enabled": true,
      "priority": 1
    }
  ],
  "vk_groups": [],
  "websites": []
}
```

### 4. Настройка социальных сетей

Отредактируйте `config/social_links.json`:

```json
{
  "telegram": {
    "channel": "your_channel",
    "enabled": true
  },
  "hashtags": ["#новости", "#технологии"]
}
```

### 5. Запуск через Docker Compose

```bash
docker-compose up -d
```

### 6. Проверка логов

```bash
docker-compose logs -f vk-autoposter
```

## 🔑 Получение токена ВКонтакте

1. Перейдите на https://dev.vk.com/
2. Создайте Standalone-приложение
3. Получите токен сообщества с правами: `wall`, `groups`, `offline`
4. Используйте метод `groups.getToken` для получения токена группы

## 🤖 Настройка ИИ-рерайта

Система использует Ollama для локального рерайта. После запуска Docker Compose:

```bash
# Подключение к контейнеру Ollama
docker exec -it ollama bash

# Загрузка модели
ollama pull qwen2.5:1.5b

# Проверка
ollama run qwen2.5:1.5b "Привет!"
```

## 📊 Структура проекта

```
vk-autoposter/
├── docker-compose.yml          # Конфигурация Docker
├── Dockerfile                  # Образ приложения
├── .env.example               # Пример переменных окружения
├── requirements.txt           # Python зависимости
├── config/
│   ├── sources.json          # Источники контента
│   ├── social_links.json     # Соцсети для футера
│   └── vk_config.json        # VK API настройки
├── src/
│   ├── main.py               # Точка входа
│   ├── vk_api_client.py      # Клиент VK API
│   ├── content_fetcher/      # Сбор контента
│   │   ├── rss_parser.py
│   │   ├── web_parser.py
│   │   └── vk_scraper.py
│   ├── processor/            # Обработка
│   │   ├── ai_rewriter.py
│   │   └── deduplicator.py
│   ├── publisher/            # Публикация
│   │   ├── vk_publisher.py
│   │   └── footer_generator.py
│   ├── database/             # База данных
│   │   └── db.py
│   └── telegram_bot/         # Telegram бот
│       └── bot.py
├── data/                      # SQLite база
└── logs/                      # Логи
```

## 🎯 Использование

### Базовый запуск

```bash
docker-compose up -d
```

### Остановка

```bash
docker-compose down
```

### Просмотр логов

```bash
docker-compose logs -f
```

### Перезапуск

```bash
docker-compose restart
```

## 📈 Мониторинг

### Статистика из базы данных

```bash
docker exec -it vk-autoposter python -c "
import asyncio
from src.database import Database

async def get_stats():
    db = Database('/app/data/posts.db')
    stats = await db.get_statistics()
    print(stats)

asyncio.run(get_stats())
"
```

### Логи

```bash
tail -f logs/autoposter.log
```

## 🔧 Расширение функциональности

### Добавление нового источника

1. Откройте `config/sources.json`
2. Добавьте источник в соответствующий раздел
3. Перезапустите контейнер

### Изменение интервала публикации

В `.env` измените `POST_INTERVAL_MINUTES`

### Отключение модерации

В `.env` установите `ENABLE_PREVIEW=false`

## 🛠️ Решение проблем

### Ошибка "Модель недоступна"

```bash
docker exec -it ollama ollama pull qwen2.5:1.5b
```

### Ошибка VK API

Проверьте токен и права доступа в `.env`

### Переполнение базы данных

```bash
docker exec -it vk-autoposter sqlite3 /app/data/posts.db "VACUUM;"
```

## 📝 Лицензия

MIT License

## 🤝 Вклад в проект

Pull requests приветствуются! Для основных изменений сначала откройте issue.

## 📞 Поддержка

- GitHub Issues: для багов и фич
- Telegram: [ваш канал]

---

**Версия:** 1.0.0  
**Дата обновления:** 2025-01-XX
