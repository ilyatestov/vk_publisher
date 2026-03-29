<?php

declare(strict_types=1);

namespace VkPublisher\Exceptions;

final class CaptchaRequiredException extends VkApiException
{
    public function __construct(
        string $message,
        public readonly string $captchaSid,
        public readonly string $captchaImg,
    ) {
        parent::__construct($message, 14, $message);
    }
}
