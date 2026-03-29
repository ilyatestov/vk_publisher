<?php

declare(strict_types=1);

namespace VkPublisher\DTO;

use VkPublisher\Exceptions\ValidationException;

final readonly class PhotoUploadRequest
{
    public function __construct(
        public string $filePath,
        public ?string $caption = null,
    ) {
        if ($this->filePath === '' || !is_readable($this->filePath)) {
            throw new ValidationException('Photo file path must exist and be readable.');
        }
    }
}
