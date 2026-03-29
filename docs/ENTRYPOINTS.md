# Entrypoints (canonical)

Этот файл фиксирует, какие точки запуска считаются каноническими.

## Python runtime (app)

- API/приложение: `src/main.py`
- Web UI: `src/web_ui.py`
- Pipeline runtime: `src/workers/pipeline.py` (`PipelineWorker`)
- Canonical async VK client: `src/infrastructure/vk_api_client.py` (`VKClient`)

## Legacy compatibility (временно)

- `src/vk_api_client.py` — shim, deprecated
- `src/publisher/vk_publisher.py` — shim, deprecated
- Реализации перенесены в `src/legacy/*`

## PHP library

- Клиент: `src/Client/VkApiClient.php`
- Сервисы: `src/Services/PostService.php`, `src/Services/MediaService.php`
- Конфиг: `src/Config/VkConfig.php`

## Правило

Новые фичи не добавлять в legacy entrypoints.
