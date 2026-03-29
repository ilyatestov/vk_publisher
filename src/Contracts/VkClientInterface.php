<?php

declare(strict_types=1);

namespace VkPublisher\Contracts;

interface VkClientInterface
{
    /**
     * @param array<string, scalar|array<array-key, scalar>|null> $params
     * @return array<int|string, mixed>
     */
    public function request(string $method, array $params = []): array;

    /**
     * @param list<string> $commands
     * @return array<int|string, mixed>
     */
    public function executeBatch(array $commands): array;
}
