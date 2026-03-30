# Установка VK Publisher на Windows 10/11

Инструкция для запуска на домашнем ПК или рабочей машине.

## 1) Требования

- Windows 10/11 x64
- Python 3.10+
- Git (желательно)
- 2+ GB RAM
- Интернет для VK/Telegram API

## 2) Установка Python

1. Скачайте с https://www.python.org/downloads/windows/
2. При установке обязательно включите **Add Python to PATH**.
3. Проверьте:

```bat
python --version
pip --version
```

## 3) Получение проекта

### Вариант A (Git)

```bat
cd %USERPROFILE%
git clone https://github.com/ilyatestov/vk_publisher.git
cd vk_publisher
```

### Вариант B (ZIP)

- Скачайте ZIP с GitHub
- Распакуйте, например, в `C:\vk_publisher`
- Откройте терминал в папке проекта

## 4) Виртуальное окружение

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Настройка `.env`

```bat
copy .env.example .env
```

Откройте `.env` и заполните минимум:

```dotenv
VK_ACCESS_TOKEN=...
VK_GROUP_ID=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_MODERATOR_CHAT_ID=...
```

## 6) Проверка конфигурации

```bat
python scripts\test_setup.py
```

## 7) Запуск API

```bat
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Проверки в браузере:
- http://localhost:8000/
- http://localhost:8000/docs
- http://localhost:8000/health

## 8) Запуск Web UI (опционально)

В отдельном терминале:

```bat
.venv\Scripts\activate
python src\web_ui.py
```

Откройте: http://localhost:7860

## 9) Автозапуск на Windows

Простой вариант: создать `.bat`-файл и добавить его в «Планировщик задач».

Пример `start_vk_publisher.bat`:

```bat
@echo off
cd /d C:\vk_publisher
call .venv\Scripts\activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 10) Частые проблемы

### `python` не найден
- Переустановите Python с галочкой PATH.

### Ошибка активации `.venv`
- Используйте `cmd` или разрешите execution policy в PowerShell.

### Порт 8000 занят
```bat
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Ошибки зависимостей
```bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 11) Рекомендации для домашнего использования

1. Храните проект вне синхронизируемых папок с публичным доступом.
2. Не публикуйте `.env`.
3. При длительной работе лучше запускать в WSL2/Linux VPS.
4. Если нужен стабильный 24/7 режим — используйте VPS с systemd.
