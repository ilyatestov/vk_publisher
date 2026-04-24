# 🔧 Устранение проблем (Troubleshooting Guide)

Это руководство поможет вам решить наиболее распространённые проблемы при установке и эксплуатации VK Publisher.

---

## 📋 Оглавление

- [Проблемы установки](#проблемы-установки)
- [Проблемы с Python окружением](#проблемы-с-python-окружением)
- [Проблемы с зависимостями](#проблемы-с-зависимостями)
- [Проблемы с VK API](#проблемы-с-vk-api)
- [Проблемы с Telegram ботом](#проблемы-с-telegram-ботом)
- [Проблемы с базой данных](#проблемы-с-базой-данных)
- [Проблемы с Docker](#проблемы-с-docker)
- [Проблемы с производительностью](#проблемы-с-производительностью)
- [Проблемы с Web UI](#проблемы-с-web-ui)
- [Логи и диагностика](#логи-и-диагностика)

---

## Проблемы установки

### ❌ `python` или `python3` не найден

**Симптомы:**
```bash
bash: python: command not found
bash: python3: command not found
```

**Решение для Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

**Решение для Windows:**
1. Скачайте установщик с https://www.python.org/downloads/windows/
2. Запустите установщик
3. **ВАЖНО:** Поставьте галочку ✅ "Add Python to PATH"
4. Нажмите "Install Now"
5. Перезапустите терминал

**Проверка:**
```bash
python3 --version  # Должно показать Python 3.10.x или выше
```

---

### ❌ `pip` не найден

**Симптомы:**
```bash
bash: pip: command not found
bash: pip3: command not found
```

**Решение для Ubuntu/Debian:**
```bash
sudo apt install -y python3-pip
```

**Решение для Windows:**
Pip устанавливается автоматически вместе с Python. Если его нет:
```bash
python -m ensurepip --upgrade
```

**Проверка:**
```bash
pip3 --version
```

---

### ❌ `git` не найден

**Симптомы:**
```bash
bash: git: command not found
```

**Решение для Ubuntu/Debian:**
```bash
sudo apt install -y git
```

**Решение для Windows:**
1. Скачайте с https://git-scm.com/download/win
2. Установите с настройками по умолчанию
3. Перезапустите терминал

**Альтернатива без Git:**
- Скачайте ZIP-архив проекта с GitHub
- Распакуйте в нужную директорию

---

## Проблемы с Python окружением

### ❌ Ошибка активации виртуального окружения

**Симптомы (Windows):**
```powershell
.\.venv\Scripts\activate : File ... cannot be loaded because running scripts 
is disabled on this system.
```

**Решение для PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Решение для CMD:**
Используйте обычный Command Prompt вместо PowerShell.

**Решение для Linux/macOS:**
```bash
source .venv/bin/activate
```

---

### ❌ Модуль не найден после активации venv

**Симптомы:**
```python
ModuleNotFoundError: No module named 'fastapi'
```

**Причина:** Зависимости не установлены или venv не активирован.

**Решение:**
```bash
# Проверьте что venv активирован
# В начале строки должно быть (.venv)

# Переустановите зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Проверьте установку
pip list | grep fastapi
```

---

### ❌ Конфликт версий Python

**Симптомы:**
```bash
SyntaxError: invalid syntax
# или
ImportError: cannot import name '...' from '...'
```

**Причина:** Используется Python старше 3.10.

**Решение:**
```bash
# Проверьте версию
python3 --version

# Если версия < 3.10, установите новую
# Ubuntu 20.04 и новее:
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Создайте venv с конкретной версией
python3.10 -m venv .venv
```

---

## Проблемы с зависимостями

### ❌ Ошибка установки зависимостей

**Симптомы:**
```bash
ERROR: Could not find a version that satisfies the requirement...
ERROR: No matching distribution found for...
```

**Решение:**
```bash
# Обновите pip и setuptools
pip install --upgrade pip setuptools wheel

# Попробуйте установить заново
pip install -r requirements.txt

# Если не помогает, установите по одному пакету
pip install fastapi uvicorn sqlalchemy aiohttp
```

---

### ❌ Конфликт версий aiohttp и aiogram

**Симптомы:**
```bash
aiogram 3.13.1 requires aiohttp<3.11, but you have aiohttp 3.13.4
```

**Решение 1 (рекомендуется):** Обновить aiogram
```bash
pip install --upgrade aiogram
```

**Решение 2:** Использовать совместимую версию aiohttp
```bash
pip install 'aiohttp>=3.10,<3.11'
```

---

### ❌ Ошибка компиляции C расширений

**Симптомы:**
```bash
error: command 'gcc' failed: No such file or directory
```

**Решение для Ubuntu/Debian:**
```bash
sudo apt install -y build-essential python3-dev
```

**Решение для Windows:**
Установите Microsoft C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## Проблемы с VK API

### ❌ Ошибка авторизации VK

**Симптомы:**
```python
VkApiException: Invalid access token
```

**Возможные причины и решения:**

1. **Неверный токен:**
   - Проверьте что скопировали токен полностью (без пробелов)
   - Убедитесь что используете токен Standalone-приложения

2. **Истёк срок действия токена:**
   - Получите новый токен с параметром `offline`
   - Используйте URL:
     ```
     https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,offline&response_type=token&v=5.199
     ```

3. **Недостаточно прав доступа:**
   - При получении токена выдайте права: `wall`, `photos`, `offline`

4. **Неверный ID группы:**
   - ID должен быть положительным числом
   - Если адрес группы `vk.com/public123456789`, то ID = `123456789`
   - Если адрес `vk.com/my_group`, узнайте ID через https://regvk.com/tools/groupId/

**Диагностика:**
```bash
python scripts/test_vk_api.py
```

---

### ❌ Лимит запросов VK API

**Симптомы:**
```python
VkApiException: Too many requests (error code: 29)
```

**Решение:**
1. Приложение автоматически использует rate limiting
2. Увеличьте интервалы между запросами в конфигурации
3. Для массовых операций используйте ночное время

---

### ❌ Нет доступа к стене сообщества

**Симптомы:**
```python
VkApiException: Access denied (error code: 15)
```

**Решение:**
1. Убедитесь что вы администратор сообщества
2. Проверьте что токен имеет право `wall`
3. Для публичных страниц могут быть ограничения

---

## Проблемы с Telegram ботом

### ❌ Бот не отвечает

**Симптомы:**
- Бот не реагирует на команды
- Не приходят уведомления о модерации

**Возможные причины:**

1. **Неверный токен:**
   ```bash
   # Проверьте токен в .env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456
   ```

2. **Бот не запущен:**
   ```bash
   # Проверьте логи
   tail -f logs/app.log
   ```

3. **Неверный Chat ID:**
   - Узнайте свой ID через @userinfobot
   - Проверьте значение в `.env`

**Диагностика:**
```bash
# Проверка подключения к Telegram API
curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
```

---

### ❌ Ошибка отправки сообщения

**Симптомы:**
```python
TelegramError: Unauthorized
```

**Решение:**
1. Проверьте что добавили бота в чат (если это групповой чат)
2. Убедитесь что Chat ID верный
3. Проверьте что бот имеет права на отправку сообщений

---

## Проблемы с базой данных

### ❌ Ошибка подключения к SQLite

**Симптомы:**
```python
sqlite3.OperationalError: unable to open database file
```

**Решение:**
```bash
# Проверьте права на директорию
ls -la data/

# Создайте директорию если нет
mkdir -p data
chmod 755 data

# Проверьте путь в .env
DATABASE_PATH=./data/vk_publisher.db
```

---

### ❌ Ошибка миграции базы данных

**Симптомы:**
```python
sqlalchemy.exc.OperationalError: no such table: social_posts
```

**Решение:**
```bash
# Удалите старую базу (если нет важных данных)
rm data/vk_publisher.db

# Перезапустите приложение - таблицы создадутся автоматически
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

### ❌ Проблемы с PostgreSQL (Docker)

**Симптомы:**
```python
psycopg2.OperationalError: could not connect to server
```

**Решение:**
```bash
# Проверьте что контейнер запущен
docker compose ps

# Перезапустите базу данных
docker compose restart db

# Проверьте логи
docker compose logs db

# Убедитесь что DATABASE_URL верный
# postgresql+asyncpg://postgres:postgres@db:5432/vk_publisher
```

---

## Проблемы с Docker

### ❌ Container exited immediately

**Симптомы:**
```bash
Container vk_publisher-app-1 exited with code 1
```

**Решение:**
```bash
# Посмотрите логи
docker compose logs app

# Частые причины:
# 1. Не настроен .env
# 2. Порт 8000 занят
# 3. Ошибка в коде

# Исправьте .env и перезапустите
docker compose down
docker compose up -d
```

---

### ❌ Port already in use

**Симптомы:**
```bash
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Решение 1:** Освободить порт
```bash
# Найти процесс
sudo lsof -i :8000

# Убить процесс
sudo kill -9 PID
```

**Решение 2:** Изменить порт в docker-compose.yml
```yaml
ports:
  - "8001:8000"  # Используем порт 8001 снаружи
```

---

### ❌ Ollama не запускается

**Симптомы:**
```bash
Container vk_publisher-ollama-1 exited with code 1
```

**Решение:**
```bash
# Ollama требует много RAM (минимум 4GB)
# Проверьте доступную память
free -h

# Отключите профиль с Ollama если не используется
docker compose up -d  # Без --profile with-ollama

# Или увеличьте лимиты памяти
```

---

### ❌ Volume permission denied

**Симптомы:**
```bash
PermissionError: [Errno 13] Permission denied: '/app/data'
```

**Решение:**
```bash
# Исправьте права на директории
sudo chown -R $USER:$USER ./data
chmod -R 755 ./data

# Или в docker-compose.yml добавьте:
# user: "${UID}:${GID}"
```

---

## Проблемы с производительностью

### ❌ Медленная обработка постов

**Симптомы:**
- Обработка занимает больше 1 минуты на пост
- Очереди постоянно растут

**Возможные решения:**

1. **Увеличьте лимиты соединений:**
   ```python
   # В infrastructure/vk_api_client.py
   connector = aiohttp.TCPConnector(
       limit=50,  # Было 10
       limit_per_host=10  # Было 5
   )
   ```

2. **Оптимизируйте AI рерайтинг:**
   - Отключите если не нужен
   - Используйте более лёгкую модель
   - Увеличьте `OLLAMA_BASE_URL` timeout

3. **Проверьте backlog очередей:**
   ```bash
   curl http://localhost:8000/api/v1/stats
   ```

---

### ❌ Высокое потребление памяти

**Симптомы:**
- Приложение использует >1GB RAM
- Система начинает тормозить

**Решение:**
```bash
# Ограничьте размер очередей
# В workers/pipeline.py добавьте:
self._queue = asyncio.Queue(maxsize=100)

# Уменьшите concurrency
self._moderation_semaphore = asyncio.Semaphore(3)  # Было 5

# Используйте monitoring для отслеживания
curl http://localhost:8000/metrics
```

---

## Проблемы с Web UI

### ❌ Gradio не запускается

**Симптомы:**
```bash
ModuleNotFoundError: No module named 'gradio'
```

**Решение:**
```bash
# Установите gradio
pip install gradio

# Или переустановите все зависимости
pip install -r requirements.txt
```

---

### ❌ Web UI не подключается к API

**Симптомы:**
- Интерфейс загружается но данные не отображаются
- Ошибки CORS в консоли браузера

**Решение:**
```bash
# Убедитесь что API запущено
curl http://localhost:8000/health

# Проверьте что порты разные:
# API: 8000
# Web UI: 7860

# Перезапустите оба сервиса
```

---

### ❌ Доступ к Web UI извне

**Симптомы:**
- Локально работает, извне нет

**Решение:**
```bash
# В web_ui.py измените:
# demo.launch(server_name="0.0.0.0", server_port=7860)

# Для production используйте reverse proxy!
# См. docs/UBUNTU_VPS_INSTALL.md
```

---

## Логи и диагностика

### Где искать логи

**Логи приложения:**
```bash
# Файл логов
tail -f logs/app.log

# Через systemd (VPS)
sudo journalctl -u vk-publisher -f

# Через Docker
docker compose logs -f app
```

**Уровни логирования:**
```dotenv
# В .env установите DEBUG для подробных логов
LOG_LEVEL=DEBUG
```

---

### Скрипты диагностики

**Проверка окружения:**
```bash
python scripts/test_setup.py
```

**Проверка VK API:**
```bash
python scripts/test_vk_api.py
```

**Проверка базы данных:**
```bash
python scripts/test_database.py
```

**Проверка здоровья:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/stats
```

---

### Сбор информации для issue

Если создаёте issue на GitHub, приложите:

1. **Версию Python:**
   ```bash
   python3 --version
   ```

2. **Версию проекта:**
   ```bash
   git describe --tags
   ```

3. **Логи ошибки:**
   ```bash
   tail -n 100 logs/app.log
   ```

4. **Конфигурацию (без секретов!):**
   ```bash
   # Покажите структуру .env без значений
   cat .env | sed 's/=.*//=REDACTED/'
   ```

5. **Окружение:**
   - ОС и версия
   - Способ установки (venv/Docker)
   - Объем RAM и CPU

---

## Дополнительные ресурсы

- [Документация VK API](https://dev.vk.com/method/)
- [Документация Telegram Bot API](https://core.telegram.org/bots/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## Всё ещё есть проблемы?

1. Проверьте существующие issues на GitHub
2. Создайте новый issue с подробным описанием
3. Проверьте логи на наличие ошибок
4. Убедитесь что используете последнюю версию

**GitHub Issues:** https://github.com/ilyatestov/vk_publisher/issues

---

*Последнее обновление: 2026-04-24*
