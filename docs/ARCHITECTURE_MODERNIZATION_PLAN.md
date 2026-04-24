# План глубокой модернизации vk_publisher

## 1) Обновленная структура проекта (Clean Architecture)

```text
vk_publisher/
├── .github/
│   └── workflows/
│       ├── tests.yml
│       ├── static.yml
│       └── release.yml
├── src/
│   ├── domain/
│   │   ├── entities.py
│   │   ├── interfaces.py
│   │   └── publishers/
│   │       └── base.py
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── publish_post.py
│   │   │   ├── moderate_post.py
│   │   │   └── generate_hashtags.py
│   │   └── tasks/
│   │       ├── broker.py
│   │       └── rewrite_tasks.py
│   ├── infrastructure/
│   │   ├── publishers/
│   │   │   └── vk_publisher.py
│   │   ├── clients/
│   │   │   ├── vk_api_client.py
│   │   │   ├── telegram_api_client.py
│   │   │   └── ollama_client.py
│   │   ├── circuit_breakers/
│   │   ├── retries/
│   │   └── database.py
│   ├── api/
│   │   ├── routes/
│   │   └── deps.py
│   └── main.py
├── docker-compose.yml
├── README.md
└── docs/
    ├── ARCHITECTURE_MODERNIZATION_PLAN.md
    └── README_BLUEPRINT.md
```

## 2) Backend и производительность

- **Фоновые задачи:** TaskIQ + Redis для AI-рерайта, парсинга и загрузки медиа.
- **LLM оптимизация:** Ollama + квантизованные модели (`llama3:8b-instruct-q4_K_M`) для RTX 4060.
- **Надежность:** `tenacity` c exponential backoff + jitter, `aiobreaker` для VK/Ollama.
- **Идемпотентность:** SHA-256 ключ на основе текста + media + tags, хранение в `published_posts`.

## 3) Архитектурная трансформация

- `BasePublisher` как единая абстракция мультиканальности (VK, Telegram).
- Application слой хранит сценарии, infrastructure слой — API-клиенты, БД, retry/circuit-breaker.

## 4) AI/Data pipeline

- Pipeline: fetch -> normalize -> rewrite (TaskIQ) -> hashtag generation -> moderation -> publish.
- Для крипто-источников (Solana/TON): отдельный use case агрегации + AI-рерайт.
- Добавить этап генерации обложек и аудио-метаданных для Music AI (YuE / ACE-Step).

## 5) README: что обязательно

См. `docs/README_BLUEPRINT.md`.
