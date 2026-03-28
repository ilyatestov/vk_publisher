"""
Infrastructure слой - реализации интерфейсов
"""
from .vk_api_client import VKClient
from .ollama_processor import OllamaProcessor
from .database import DatabaseStorage
from .telegram_bot import TelegramModeratorBot

__all__ = [
    "VKClient",
    "OllamaProcessor",
    "DatabaseStorage",
    "TelegramModeratorBot"
]
