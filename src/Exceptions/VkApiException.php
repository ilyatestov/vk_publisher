<?php

declare(strict_types=1);

namespace VkPublisher\Exceptions;

use RuntimeException;

class VkApiException extends RuntimeException
{
    public function __construct(
        string $message,
        public readonly int $vkErrorCode = 0,
        public readonly ?string $vkErrorMessage = null,
    ) {
        parent::__construct($message, $vkErrorCode);
    }
}
