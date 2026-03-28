# 🌐 WEB UI ИНТЕРФЕЙС ДЛЯ VK PUBLISHER

Приложение теперь включает в себя удобный веб-интерфейс на базе Gradio для управления автопостингом ВКонтакте.

---

## 🎯 ВОЗМОЖНОСТИ WEB UI

- ✅ **Проверка статуса** приложения в реальном времени
- ✅ **Просмотр статистики** публикаций
- ✅ **Добавление источников** контента (RSS, VK группы, сайты)
- ✅ **Создание постов** вручную с планированием
- ✅ **Просмотр последних** публикаций
- ✅ **Быстрый доступ** к документации и API

---

## 🚀 ЗАПУСК WEB UI

### Предварительные требования

1. Установите зависимости (если еще не установлены):
```bash
pip install -r requirements.txt
```

2. Убедитесь что основное приложение запущено:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Запуск интерфейса

#### Вариант 1: Отдельный процесс
Откройте новый терминал и выполните:

```bash
python src/web_ui.py
```

#### Вариант 2: С указанием порта
```bash
python src/web_ui.py --port 7860
```

#### Вариант 3: С публичным доступом (ngrok)
```bash
python src/web_ui.py --share
```

---

## 📊 ДОСТУП К ИНТЕРФЕЙСУ

После запуска откройте браузер и перейдите по адресу:

**http://localhost:7860**

Или если запускаете на сервере:
**http://ВАШ_IP:7860**

---

## 🏗️ СТРУКТУРА ИНТЕРФЕЙСА

### Вкладка "📊 Состояние"
- Проверка здоровья приложения
- Статистика по публикациям
- Кнопки обновления данных

### Вкладка "📰 Источники контента"
- Добавление RSS лент
- Добавление групп ВКонтакте
- Добавление сайтов для парсинга

### Вкладка "✍️ Создать пост"
- Текстовое поле для содержимого
- Выбор времени публикации
- Мгновенная отправка или планирование

### Вкладка "📋 Последние посты"
- Список недавних публикаций
- Статус каждого поста
- Даты и время

### Вкладка "📚 Документация"
- Ссылки на API документацию
- Инструкции по настройке
- Полезные ресурсы

---

## 🔧 НАСТРОЙКА ДЛЯ VPS

### 1. Откройте порт в firewall
```bash
sudo ufw allow 7860/tcp
```

### 2. Запустите в фоне через nohup
```bash
nohup python src/web_ui.py > webui.log 2>&1 &
```

### 3. Или создайте systemd сервис

```bash
sudo nano /etc/systemd/system/vk-publisher-ui.service
```

Вставьте:
```ini
[Unit]
Description=VK Publisher Web UI
After=network.target vk-publisher.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/vk_publisher
Environment="PATH=/home/ubuntu/vk_publisher/.venv/bin"
ExecStart=/home/ubuntu/vk_publisher/.venv/bin/python src/web_ui.py --server_name 0.0.0.0 --server_port 7860
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vk-publisher-ui
sudo systemctl start vk-publisher-ui
```

---

## 🌐 ДОСТУП ЧЕРЕЗ NGINX (ОПЦИОНАЛЬНО)

Если хотите использовать доменное имя:

### 1. Создайте конфиг Nginx
```bash
sudo nano /etc/nginx/sites-available/vk-publisher-ui
```

### 2. Вставьте конфигурацию:
```nginx
server {
    listen 80;
    server_name ui.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Для WebSocket (если используется share=True)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Активируйте сайт
```bash
sudo ln -s /etc/nginx/sites-available/vk-publisher-ui /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Настройте SSL (рекомендуется)
```bash
sudo certbot --nginx -d ui.your-domain.com
```

---

## 🔐 БЕЗОПАСНОСТЬ

### Рекомендации для production:

1. **Не открывайте порт 7860 напрямую** без защиты
2. **Используйте Nginx** как reverse proxy
3. **Настройте SSL** через Let's Encrypt
4. **Ограничьте доступ** по IP через firewall
5. **Используйте аутентификацию** (см. ниже)

### Добавление базовой аутентификации:

Установите gradio с поддержкой auth:
```bash
pip install gradio[auth]
```

Измените запуск:
```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    auth=("admin", "your_password"),  # логин:пароль
    auth_message="Введите credentials для доступа"
)
```

---

## 🎨 КАСТОМИЗАЦИЯ ИНТЕРФЕЙСА

Вы можете изменить внешний вид редактируя `src/web_ui.py`:

### Изменение темы:
```python
with gr.Blocks(theme=gr.themes.Soft()) as demo:  # Soft, Base, Glass, Monochrome
```

### Добавление новых вкладок:
```python
with gr.Tab("🔧 Настройки"):
    # ваши элементы
```

### Изменение порта:
```python
demo.launch(server_port=8080)  # любой свободный порт
```

---

## 📱 МОБИЛЬНАЯ ВЕРСИЯ

Интерфейс автоматически адаптируется под мобильные устройства. Просто откройте ссылку на смартфоне или планшете.

---

## 🐳 ЗАПУСК ЧЕРЕЗ DOCKER

Добавьте сервис в `docker-compose.yml`:

```yaml
webui:
  build: .
  ports:
    - "7860:7860"
  command: python src/web_ui.py
  environment:
    - API_BASE_URL=http://app:8000
  depends_on:
    - app
  networks:
    - vk_publisher_net
```

Запустите:
```bash
docker-compose up -d webui
```

---

## ❌ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема: "ModuleNotFoundError: No module named 'gradio'"
**Решение:**
```bash
pip install gradio==4.44.0
```

### Проблема: Порт 7860 уже занят
**Решение:**
```bash
# Найдите процесс
lsof -i :7860

# Или измените порт в web_ui.py
demo.launch(server_port=7861)
```

### Проблема: Не подключается к API
**Решение:**
- Убедитесь что основное приложение запущено на порту 8000
- Проверьте URL в web_ui.py (API_BASE_URL)

### Проблема: Медленная работа
**Решение:**
- Запустите UI на том же сервере что и API
- Используйте прямое подключение вместо network

---

## 💡 СОВЕТЫ ПО ИСПОЛЬЗОВАНИЮ

1. **Запускайте UI в отдельном окне терминала** чтобы видеть логи
2. **Используйте Ctrl+C** для остановки UI
3. **Обновляйте страницу** при проблемах с подключением
4. **Смотрите логи** основного приложения для отладки

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- Документация Gradio: https://www.gradio.app/docs
- Примеры интерфейсов: https://www.gradio.app/guides
- API документация VK Publisher: http://localhost:8000/docs

---

## 🎯 СЛЕДУЮЩИЕ УЛУЧШЕНИЯ

В будущих версиях планируется:
- [ ] Полноценная интеграция с API для всех функций
- [ ] Редактирование и удаление постов
- [ ] Управление источниками контента
- [ ] Графики и диаграммы статистики
- [ ] Экспорт/импорт настроек
- [ ] Мультиязычность
- [ ] Темная тема

---

Если у вас есть предложения по улучшению интерфейса - создайте issue в репозитории проекта!
