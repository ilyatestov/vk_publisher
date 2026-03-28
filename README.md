# VK Publisher — Автопостинг ВКонтакте

[![Tests](https://github.com/ilyatestov/vk_publisher/actions/workflows/tests.yml/badge.svg)](https://github.com/ilyatestov/vk_publisher/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

📌 **Автоматическая система публикации контента в группы ВКонтакте**  
с проверкой дубликатов, ИИ-рерайтом и модерацией через Telegram.

---

## ⚡ Быстрый старт (5 минут)

### Вариант 1: Docker (рекомендуется)

**1. Клонировать репозиторий:**

```bash
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
```

**2. Настроить конфигурацию:**

```bash
cp .env.example .env
# Отредактировать .env — заполнить VK_ACCESS_TOKEN и VK_GROUP_ID
```

**3. Запустить:**

```bash
docker-compose up -d
```

**4. Проверить логи:**

```bash
docker-compose logs -f vk-autoposter
```

---

### Вариант 2: Windows (без Docker)

**1. Установить Python 3.10+:**  
https://www.python.org/downloads/

**2. Установить зависимости:**

```bash
pip install -r requirements.txt
```

**3. Установить Ollama (для ИИ):**  
https://ollama.com/download/windows

**4. Загрузить модель:**

```bash
ollama pull qwen2.5:1.5b
```

**5. Настроить и запустить:**

```bash
cp .env.example .env
python src/main.py
```

---

### Вариант 3: VPS (Ubuntu/Debian)

**1. Подключиться к серверу:**

```bash
ssh user@your-vps-ip
```

**2. Установить Docker:**

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
exit
# Переподключитесь к серверу
```

**3. Клонировать и настроить:**

```bash
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
cp .env.example .env
# Редактировать .env (nano .env)
```

**4. Запустить:**

```bash
docker-compose up -d
```

**5. Добавить в автозагрузку:**

```bash
docker-compose restart --always
```

---

## 🔑 Получение VK токена

1. Перейти на https://dev.vk.com/
2. Создать приложение типа **"Standalone"**
3. В настройках получить токен с правами: **wall, groups, offline**
4. Вставить токен в `.env` (`VK_ACCESS_TOKEN`)

**Важно:** Токен должен быть выдан от имени администратора сообщества.

---

## 📊 Структура проекта

```
vk_publisher/
├── src/
│   ├── main.py              # Точка входа приложения
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
├── scripts/                 # Скрипты проверки
│   ├── test_setup.py        # Проверка готовности системы
│   ├── test_vk_api.py       # Тест подключения к VK API
│   ├── test_database.py     # Тест базы данных
│   └── health_check.py      # Health check для Docker
├── tests/                   # Модульные тесты
│   ├── test_database.py
│   ├── test_deduplicator.py
│   └── test_footer_generator.py
├── config/                  # Конфигурационные файлы
│   ├── sources.json         # Источники контента
│   ├── social_links.json    # Ссылки на соцсети
│   └── vk_config.json       # Настройки VK
├── data/                    # Данные (БД, бэкапы)
│   └── posts.db             # SQLite база
├── logs/                    # Логи приложения
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile               # Docker образ
├── requirements.txt         # Python зависимости
├── .env.example             # Шаблон переменных окружения
├── README.md                # Этот файл
└── RECOMMENDATIONS.md       # Рекомендации по улучшению
```

---

## 🗄️ База данных

Система использует SQLite (файл `data/posts.db`).

### Таблицы:

| Таблица | Описание |
|---------|----------|
| `posts` | Опубликованные посты |
| `duplicates` | Хеши проверенного контента |
| `sources` | Источники контента |
| `logs` | Журнал действий |
| `stats` | Статистика публикаций |

### Просмотр данных:

```bash
sqlite3 data/posts.db ".tables"
sqlite3 data/posts.db "SELECT * FROM posts LIMIT 5;"
```

### Бэкап:

```bash
cp data/posts.db data/posts.backup.db
```

---

## 🔧 Настройка источников контента

### RSS-ленты (`config/sources.json`):

```json
{
  "rss": [
    {"url": "https://dtf.ru/rss", "category": "games"},
    {"url": "https://vc.ru/rss", "category": "business"}
  ]
}
```

### Поиск ВКонтакте:

```env
VK_SEARCH_QUERIES=технологии,новости,ai
```

---

## 📱 Telegram бот для модерации

**1. Создать бота через @BotFather**

**2. Узнать свой ID через @userinfobot**

**3. Вставить в `.env`:**

```env
TELEGRAM_BOT_TOKEN=ваш_токен
ADMIN_TELEGRAM_ID=ваш_id
ENABLE_PREVIEW=true
```

**4. При `ENABLE_PREVIEW=true`** — бот будет запрашивать подтверждение перед публикацией.

---

## 🤖 ИИ-рерайт (Ollama)

### Доступные модели:

| Модель | Качество | Требования |
|--------|---------|------------|
| `qwen2.5:1.5b` | Хорошее | 2GB RAM (рекомендуется) |
| `qwen2.5:3b` | Лучшее | 4GB RAM |
| `llama3:8b` | Отличное | 8GB+ RAM |

### Проверка работы:

```bash
curl http://localhost:11434/api/tags
```

### Загрузка модели:

```bash
ollama pull qwen2.5:1.5b
```

### Отключение ИИ:

Если ИИ не нужен, установите в `.env`:

```env
ENABLE_AI_REWRITE=false
```

---

## 🧪 Проверка работоспособности

### Перед запуском:

```bash
python scripts/test_setup.py
```

### Тест VK API:

```bash
python scripts/test_vk_api.py
```

### Тест базы данных:

```bash
python scripts/test_database.py
```

### Модульные тесты:

```bash
pytest tests/ -v
```

---

## ⚠️ Troubleshooting

### Ошибка "Invalid token"

→ Проверить `VK_ACCESS_TOKEN` в `.env`  
→ Убедиться что токен имеет права **wall, groups**

### Ошибка "Model not found"

```bash
ollama pull qwen2.5:1.5b
```

→ Проверить `OLLAMA_BASE_URL` в `.env`

### Контейнер не стартует

```bash
docker-compose logs vk-autoposter
```

→ Проверить права на папку `data/`

### Дубликаты не фильтруются

→ Проверить `DATABASE_PATH` в `.env`  
```bash
sqlite3 data/posts.db "SELECT * FROM duplicates;"
```

### Ошибка доступа к группе

→ Убедиться что токен выдан от имени **администратора**  
→ Проверить `VK_GROUP_ID` (должен быть без `@`)

---

## 📈 Мониторинг

### Просмотр логов:

```bash
docker-compose logs -f vk-autoposter
```

### Статистика публикаций:

```bash
sqlite3 data/posts.db "SELECT date(created_at), count(*) FROM posts GROUP BY date(created_at);"
```

### Проверка здоровья:

```bash
docker exec vk-autoposter python scripts/health_check.py
```

---

## 🔒 Безопасность

- ✅ Никогда не коммитьте `.env` в git
- ✅ Регулярно обновляйте зависимости
- ✅ Используйте прокси при парсинге больших объёмов
- ✅ Ограничьте `MAX_POSTS_PER_DAY` для новых групп

---

## 📞 Поддержка

- **Issues:** https://github.com/ilyatestov/vk_publisher/issues
- **Версия:** 1.2.0

---

## 📊 Roadmap

- [ ] Интеграционные тесты VK API
- [ ] Кеширование запросов к источникам
- [ ] Админ-панель для управления
- [ ] Prometheus-метрики
- [ ] Поддержка других соцсетей (Telegram, OK)

---

**Лицензия:** MIT  
**Последнее обновление:** 2025-01
