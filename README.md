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

## 🧪 Тестирование

Запуск модульных тестов:

```bash
# Установка зависимостей для тестирования
pip install pytest pytest-asyncio

# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ -v --cov=src
```

Структура тестов:
- `tests/test_database.py` - тесты базы данных (8 тестов)
- `tests/test_deduplicator.py` - тесты дедупликации (11 тестов)
- `tests/test_footer_generator.py` - тесты генератора футеров (10 тестов)

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

**Версия:** 1.1.0  
**Дата обновления:** 2025-01-XX
