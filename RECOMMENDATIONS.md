# Рекомендации по улучшению VK Publisher

Актуальная версия рекомендаций и результатов аудита: **[docs/PROJECT_AUDIT_RU.md](docs/PROJECT_AUDIT_RU.md)**.

## Кратко

1. **Производительность:** переиспользовать HTTP session, измерять p95 latency pipeline, добавить backpressure.
2. **Архитектура:** убрать дубли модулей и закрепить единый путь dependency flow.
3. **Безопасность:** включить `bandit`/`pip-audit`, запретить хранение секретов в репозитории, добавить URL allowlist.
4. **Эксплуатация:** расширить CI (tests + security scans), контролировать качество зависимостей.

## Быстрые команды

```bash
pytest -q
bandit -r src
pip-audit
```

