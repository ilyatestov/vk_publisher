"""
Модуль публикации
"""
from .footer_generator import FooterGenerator

__all__ = ['VKPublisher', 'FooterGenerator']


def __getattr__(name):
    """Ленивая загрузка тяжёлых зависимостей публикации."""
    if name == 'VKPublisher':
        from .vk_publisher import VKPublisher
        return VKPublisher
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
