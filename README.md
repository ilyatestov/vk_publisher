# VK Publisher

Сервис для автоматизированного сбора, обработки и публикации контента во ВКонтакте.

## Что сделано в этой ревизии

- Проведён технический аудит репозитория: производительность, безопасность, архитектура и сопровождение.
- Подготовлен план реконструкции кода по этапам (без «большого взрыва»).
- Обновлены практики гигиены репозитория (`.gitignore`, удаление локальной SQLite из Git).
- Добавлен безопасный шаблон переменных окружения (`.env.example`).

Подробный аудит: **[docs/PROJECT_AUDIT_RU.md](docs/PROJECT_AUDIT_RU.md)**.

---

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
pytest -q
```

Запуск API:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Структура проекта

```text
src/
  core/              # конфигурация, логирование, исключения
  domain/            # сущности и интерфейсы
  infrastructure/    # интеграции (БД, VK, Telegram, Ollama)
  workers/           # асинхронный pipeline
  content_fetcher/   # RSS/Web/VK сбор контента
  processor/         # обработка (dedup, AI rewrite)
  publisher/         # публикация во ВК
  main.py            # точка входа
tests/               # unit/integration тесты
scripts/             # вспомогательные проверки
docs/                # документация и план улучшений
```

---

## Реконструкция кода (рекомендуемый порядок)

1. **Стабилизировать зависимости и CI**: гарантировать установку `requirements*.txt` и зелёный `pytest`.
2. **Убрать дубли архитектурных слоёв**: определить единый runtime-путь (`src/infrastructure` vs `src/publisher`, `src/vk_api_client.py` vs `src/infrastructure/vk_api_client.py`).
3. **Вынести I/O политики**: централизованный HTTP клиент с таймаутами, retry, пулом соединений.
4. **Ввести наблюдаемость**: метрики очередей pipeline, latency по этапам, ошибки по источникам.
5. **Повысить безопасность**: валидация URL источников, ограничение SSRF, маскирование чувствительных данных в логах.

Детализация по шагам и приоритетам — в `docs/PROJECT_AUDIT_RU.md`.

---

## Поиск уязвимостей и hardening

Рекомендуемый минимум перед продом:

```bash
pip-audit
bandit -r src
safety check
```

Также:
- не хранить секреты в `config/*.json`;
- не коммитить локальные базы данных;
- ограничить исходящие HTTP-запросы allowlist-ом доменов;
- включить ротацию и редактирование логов.

---

## Очистка веток и мусора репозитория

Удаление локальных merged-веток:

```bash
git branch --merged | grep -v '^*\|main\|master\|work' | xargs -r git branch -d
```

Удаление remote-tracking «хвостов»:

```bash
git remote prune origin
```

> В текущем состоянии обнаружена только активная ветка `work`, поэтому удалять ветки сейчас не требуется.

