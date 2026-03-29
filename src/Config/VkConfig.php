<?php

declare(strict_types=1);

namespace VkPublisher\Config;

use VkPublisher\Exceptions\ValidationException;

final readonly class VkConfig
{
    public function __construct(
        public string $accessToken,
        public string $apiVersion = '5.199',
        public string $baseUri = 'https://api.vk.com/method/',
        public float $timeoutSeconds = 10.0,
        public float $connectTimeoutSeconds = 3.0,
        public int $maxRetries = 3,
        public int $groupId = 0,
    ) {
        if ($this->accessToken === '') {
            throw new ValidationException('VK access token must not be empty.');
        }

        if ($this->timeoutSeconds <= 0 || $this->connectTimeoutSeconds <= 0) {
            throw new ValidationException('Timeout values must be positive.');
        }

        if ($this->maxRetries < 0) {
            throw new ValidationException('maxRetries must be greater or equal to 0.');
        }
    }

    /**
     * @param array<string, string|false> $env
     */
    public static function fromEnv(array $env = []): self
    {
        $token = (string) ($env['VK_ACCESS_TOKEN'] ?? getenv('VK_ACCESS_TOKEN') ?: '');
        $apiVersion = (string) ($env['VK_API_VERSION'] ?? getenv('VK_API_VERSION') ?: '5.199');
        $baseUri = (string) ($env['VK_BASE_URI'] ?? getenv('VK_BASE_URI') ?: 'https://api.vk.com/method/');
        $timeout = (float) ($env['VK_TIMEOUT'] ?? getenv('VK_TIMEOUT') ?: 10.0);
        $connectTimeout = (float) ($env['VK_CONNECT_TIMEOUT'] ?? getenv('VK_CONNECT_TIMEOUT') ?: 3.0);
        $retries = (int) ($env['VK_MAX_RETRIES'] ?? getenv('VK_MAX_RETRIES') ?: 3);
        $groupId = (int) ($env['VK_GROUP_ID'] ?? getenv('VK_GROUP_ID') ?: 0);

        return new self(
            accessToken: $token,
            apiVersion: $apiVersion,
            baseUri: rtrim($baseUri, '/') . '/',
            timeoutSeconds: $timeout,
            connectTimeoutSeconds: $connectTimeout,
            maxRetries: $retries,
            groupId: $groupId,
        );
    }
}
