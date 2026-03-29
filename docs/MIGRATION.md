# Migration guide: legacy -> v2 (PHP)

## Ключевые изменения

1. Проект переехал на PHP 8.2+ и Composer.
2. Низкоуровневые вызовы cURL заменены на `VkApiClient` (Guzzle).
3. Прямые массивы параметров заменены на DTO (`PostRequest`, `PhotoUploadRequest`).
4. Ошибки теперь типизированы: `VkApiException`, `RateLimitException`, `ValidationException`.
5. Конфигурация берётся из ENV через `VkConfig::fromEnv()`.

## Было / Стало

### Инициализация

**Было (условно):**

```php
$client = new LegacyVkClient($token);
$client->post($groupId, $message);
```

**Стало:**

```php
$config = VkConfig::fromEnv();
$client = new VkApiClient($config);
$postService = new PostService($client, $config->groupId);
$postService->publish(new PostRequest('message'));
```

### Ошибки

**Было:** строки и коды без доменной типизации.

**Стало:**

```php
try {
    $postService->publish(new PostRequest('hello'));
} catch (RateLimitException $e) {
    // retry later
} catch (VkApiException $e) {
    // generic VK error
}
```

## План миграции

1. Добавить ENV-переменные в инфраструктуру деплоя.
2. Заменить старые вызовы на `PostService` / `MediaService`.
3. Перенести обработку ошибок в централизованный middleware.
4. Подключить CI проверки (`composer test`, `composer stan`, `composer cs:check`).
5. Удалить legacy-клиент после стабилизации.
