<?php

declare(strict_types=1);

namespace VkPublisher\DTO;

use VkPublisher\Exceptions\ValidationException;

final readonly class PostRequest
{
    /**
     * @param list<string> $attachments
     */
    public function __construct(
        public string $message,
        public ?int $publishDate = null,
        public array $attachments = [],
        public ?int $fromGroup = 1,
    ) {
        if (trim($this->message) === '' && $this->attachments === []) {
            throw new ValidationException('Either message or attachments must be provided.');
        }

        if ($this->publishDate !== null && $this->publishDate <= time()) {
            throw new ValidationException('publishDate must be in the future UNIX timestamp.');
        }
    }
}
