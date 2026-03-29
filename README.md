# VK Publisher

Автопостинг и контент-пайплайн для VK с веб-интерфейсом, дедупликацией, модерацией и публикацией.

> Текущий репозиторий содержит **смешанный стек** (Python-приложение + PHP-библиотека).
> Это рабочее состояние, но его нужно структурно разделить (см. раздел «Реконструкция» ниже).

---

## 1) Что в проекте сейчас

### Python-часть (основной рантайм)
- pipeline-воркеры (`fetch -> process -> moderate -> publish`)
- работа с БД (SQLite/aiosqlite)
- дедупликация и обработка контента
- web UI

### PHP-часть (библиотека VK API)
- `src/Client`, `src/Services`, `src/DTO`, `src/Exceptions`
- unit-тесты PHPUnit

---

## 2) Быстрый старт (Python)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```

Запуск приложения:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Запуск веб-интерфейса:

```bash
python src/web_ui.py
```

---

## 3) Быстрый старт (PHP)

```bash
composer install
vendor/bin/phpunit --testdox
vendor/bin/phpstan analyse --no-progress
```

---

## 4) Документация

### Главный индекс документации
- [`docs/README_RU.md`](docs/README_RU.md)

### Ключевые документы
- Аудит: [`docs/PROJECT_AUDIT_RU.md`](docs/PROJECT_AUDIT_RU.md)
- План продукта: [`docs/PRODUCT_IMPROVEMENT_PLAN_RU.md`](docs/PRODUCT_IMPROVEMENT_PLAN_RU.md)
- План реконструкции кода: [`docs/ARCHITECTURE_RECONSTRUCTION_RU.md`](docs/ARCHITECTURE_RECONSTRUCTION_RU.md)
- Настройка VK API: [`docs/VK_API_SETUP.md`](docs/VK_API_SETUP.md)
- Установка на VPS: [`docs/UBUNTU_VPS_INSTALL.md`](docs/UBUNTU_VPS_INSTALL.md)
- Установка на Windows: [`docs/WINDOWS_INSTALL.md`](docs/WINDOWS_INSTALL.md)
- Web UI: [`docs/WEB_UI_GUIDE.md`](docs/WEB_UI_GUIDE.md)

---

## 5) Текущее состояние архитектуры (честно)

Сейчас в проекте есть «исторический слой» и дублирование ответственности:
- `src/vk_api_client.py` и `src/infrastructure/vk_api_client.py`
- разные стили организации кода (чистая архитектура + legacy модули)
- часть документации устарела и пересекается

Это главная причина, почему тяжело ориентироваться.

---

## 6) Реконструкция (как привести к нормальному виду)

Коротко:
1. Зафиксировать **канонический runtime path** (какой код «боевой», какой legacy).
2. Разнести Python app и PHP library (минимум логически в документации, лучше физически по подпапкам/репозиториям).
3. Ввести единый `docs/README_RU.md` как точку входа.
4. Обновлять docs только через архитектурный план, чтобы не плодить дубли.

Подробный пошаговый план: [`docs/ARCHITECTURE_RECONSTRUCTION_RU.md`](docs/ARCHITECTURE_RECONSTRUCTION_RU.md).

---

## 7) Что с PR #25 (почему «странный»)

На странице PR видно технические сбои загрузки GitHub UI (`Sorry, something went wrong` / `Uh oh!`) и автоматический комментарий от бота Codex про лимиты ревью. Это похоже на проблемы интерфейса/лимитов интеграции, а не на корректность кода как такового.

PR: <https://github.com/ilyatestov/vk_publisher/pull/25>

---

## 8) Минимальные правила порядка в репо

- Не добавлять новые фичи без обновления `docs/ARCHITECTURE_RECONSTRUCTION_RU.md`.
- Для каждой функциональной правки: тест + обновление релевантного документа.
- Не смешивать новые Python-модули с legacy без явной пометки `deprecated`.

