"""
Core модуль - конфигурация, логирование, исключения
"""
from .config import settings, Settings
from .logging import log, setup_logger, mask_sensitive_data
from .exceptions import (
    VKPublisherError,
    VKAPIError,
    VKAuthError,
    VKRateLimitError,
    VKPermissionError,
    VKCaptchaError,
    OllamaError,
    OllamaTimeoutError,
    DatabaseError,
    ContentFetchError,
    ModerationError,
    ConfigurationError
)

__all__ = [
    "settings",
    "Settings",
    "log",
    "setup_logger",
    "mask_sensitive_data",
    "VKPublisherError",
    "VKAPIError",
    "VKAuthError",
    "VKRateLimitError",
    "VKPermissionError",
    "VKCaptchaError",
    "OllamaError",
    "OllamaTimeoutError",
    "DatabaseError",
    "ContentFetchError",
    "ModerationError",
    "ConfigurationError"
]
