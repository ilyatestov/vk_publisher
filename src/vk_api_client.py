"""Compatibility shim for legacy VK API client.

Канонический async-клиент: ``src.infrastructure.vk_api_client.VKClient``.
Этот модуль сохранён только для обратной совместимости со старым sync API.
"""
import warnings

warnings.warn(
    "src.vk_api_client is deprecated; use src.infrastructure.vk_api_client.VKClient",
    DeprecationWarning,
    stacklevel=2,
)

from .legacy.vk_api_client import *  # noqa: F401,F403
