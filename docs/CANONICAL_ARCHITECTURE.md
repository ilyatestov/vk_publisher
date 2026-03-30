# Canonical architecture paths

Этот документ фиксирует канонические пути импортов и модулей для нового кода.

## Runtime entrypoint
- Каноническая точка запуска API: `src/main.py`
- Роутеры: `src/api/routes/*`
- DI/deps: `src/api/deps.py`
- Bootstrap/runtime wiring: `src/bootstrap/container.py`

## Pipeline
- Каноническая реализация конвейера: `src/workers/pipeline.py`

## Инфраструктурные адаптеры
- VK: `src/infrastructure/vk_api_client.py`
- DB: `src/infrastructure/database.py`
- Telegram: `src/infrastructure/telegram_bot.py`
- AI/Ollama: `src/infrastructure/ollama_processor.py`

## Legacy candidates (постепенная депрекация)
- `src/vk_api_client.py`
- `src/publisher/*`

## Правило
- Новый код не должен добавлять зависимости на legacy candidates.
- При рефакторинге мигрировать импорты в canonical paths.
