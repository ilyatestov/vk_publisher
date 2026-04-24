# 🚀 Краткое руководство по запуску vk_publisher

## Варианты запуска

### 1️⃣ Docker Compose (рекомендуется) ⭐

```bash
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
cp .env.example .env
nano .env  # Заполните токены

docker compose up -d
docker compose --profile with-ollama up -d  # С AI

# Проверка
curl http://localhost:8000/health
```

**Готово!** 
- API: http://localhost:8000/docs
- Web UI: http://localhost:7860
- Grafana: http://localhost:3000

---

### 2️⃣ Локально (Python)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
cp .env.example .env
nano .env

uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

### 3️⃣ Готовый .exe (Windows)

1. Скачайте релиз: https://github.com/ilyatestov/vk_publisher/releases
2. Распакуйте архив
3. Отредактируйте `.env`
4. Запустите `start.bat`

---

## Минимальная конфигурация (.env)

```dotenv
# Обязательно
VK_ACCESS_TOKEN=ваш_токен_vk
VK_GROUP_ID=123456789
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_MODERATOR_CHAT_ID=ваш_chat_id

# Опционально
OLLAMA_BASE_URL=http://localhost:11434
ENCRYPTION_KEY=замените_на_секретный_ключ_32+
```

---

## Получение токенов

### VK Access Token
1. https://dev.vk.com/my-apps → Создать Standalone
2. Перейдите по URL (замените YOUR_APP_ID):
   ```
   https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,offline&response_type=token&v=5.199
   ```
3. Скопируйте токен из адресной строки

### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. `/newbot` → следуйте инструкциям

### Telegram Chat ID
1. Найдите @userinfobot
2. Отправьте сообщение → скопируйте ID

---

## Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# API документация
open http://localhost:8000/docs

# Метрики
curl http://localhost:8000/metrics
```

---

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Порт 8000 занят | `--port 8001` |
| ModuleNotFoundError | Активируйте venv |
| Ошибка VK API | Проверьте токен |
| Бот не отвечает | Проверьте токен и chat_id |

**Полная документация**: https://github.com/ilyatestov/vk_publisher/tree/main/docs
