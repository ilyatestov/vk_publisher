codex/revise-and-secure-vk_publisher-repository
# VK Publisher (PHP 8.2+)

Production-ready PHP библиотека для безопасной публикации контента во ВКонтакте через VK API.

## Что сделано в этой модернизации

- Полный переход на **PHP 8.2+**, `strict_types`, PSR-4.
- Новый HTTP-слой на **Guzzle** вместо прямого cURL.
- Retry с exponential backoff, таймауты, обработка VK API ошибок.
- Выделены слои: `Client`, `Services`, `DTO`, `Exceptions`, `Contracts`, `Config`.
- Dependency Injection + интерфейсы.
- Unit-тесты на PHPUnit с моками HTTP.
- DevEx: PHPStan, PHP-CS-Fixer, GitHub Actions CI.

---

## Установка

```bash
composer require vk-publisher/vk-publisher
```

Для разработки в репозитории:

```bash
composer install
composer test
```

---

## Структура

```text
src/
├── Client/
│   └── VkApiClient.php
├── Services/
│   ├── PostService.php
│   └── MediaService.php
├── DTO/
├── Exceptions/
├── Contracts/
└── Config/
```

---

## Конфигурация через ENV

`.env` (пример):

```dotenv
VK_ACCESS_TOKEN=vk1.a.xxxxx
VK_GROUP_ID=123456
VK_API_VERSION=5.199
VK_TIMEOUT=10
VK_CONNECT_TIMEOUT=3
VK_MAX_RETRIES=3
```

Создание конфигурации:

```php
use VkPublisher\Config\VkConfig;

$config = VkConfig::fromEnv();
```

> Никогда не коммитьте `VK_ACCESS_TOKEN` в Git.

---

## Пример использования

```php
<?php

declare(strict_types=1);

use VkPublisher\Client\VkApiClient;
use VkPublisher\Config\VkConfig;
use VkPublisher\DTO\PhotoUploadRequest;
use VkPublisher\DTO\PostRequest;
use VkPublisher\Services\MediaService;
use VkPublisher\Services\PostService;

require __DIR__ . '/vendor/autoload.php';

$config = VkConfig::fromEnv();
$client = new VkApiClient($config);

$postService = new PostService($client, $config->groupId);
$mediaService = new MediaService($client, new \GuzzleHttp\Client(), $config->groupId);

$attachment = $mediaService->uploadWallPhoto(new PhotoUploadRequest(__DIR__ . '/photo.jpg'));

$result = $postService->publish(new PostRequest(
    message: 'Новый пост через VK Publisher',
    publishDate: time() + 3600,
    attachments: [$attachment],
));

echo 'Post ID: ' . $result['post_id'] . PHP_EOL;
```

---

## Обработка ошибок

```php
use VkPublisher\Exceptions\CaptchaRequiredException;
use VkPublisher\Exceptions\RateLimitException;
use VkPublisher\Exceptions\VkApiException;

try {
    $postService->publish(new PostRequest('test'));
} catch (RateLimitException $e) {
    // backoff / очередь
} catch (CaptchaRequiredException $e) {
    // показать captcha_sid и captcha_img оператору
} catch (VkApiException $e) {
    // централизованный error handling
}
```

---

## Rate limit стратегия

- Автоматический retry при сетевых ошибках и VK кодах `6`, `9`, `29`.
- Exponential backoff: `200ms * 2^N`.
- После исчерпания retry выбрасывается `RateLimitException`.
- Для high-load рекомендуется внешняя очередь (RabbitMQ/SQS/Kafka) + worker pool.

---

## Тестирование и качество

```bash
composer test
composer stan
composer cs:check
```

---

## Миграция со старой версии

См. `docs/MIGRATION.md`.

---

## Security checklist
=======

main

- ✅ Токены только из ENV.
- ✅ Логи без секретов.
- ✅ Таймауты HTTP запросов включены.
- ✅ Валидация входных DTO.
- ✅ Единая типизированная модель исключений.