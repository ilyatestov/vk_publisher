"""
Интерфейсы (абстракции) для инфраструктуры
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from .entities import SocialPost, VKAccount, ModerationDecision


class SocialPublisherInterface(ABC):
    """
    Абстрактный интерфейс для публикации в социальные сети
    
    Позволяет легко добавлять новые платформы (Telegram, Instagram и т.д.)
    """

    @abstractmethod
    async def publish_post(self, post: SocialPost, account: VKAccount) -> bool:
        """
        Публикует пост в социальной сети
        
        Args:
            post: Пост для публикации
            account: Аккаунт для публикации
            
        Returns:
            True если публикация успешна
        """
        pass

    @abstractmethod
    async def upload_media(self, media_urls: List[str], account: VKAccount) -> List[str]:
        """
        Загружает медиафайлы и возвращает ссылки для вставки
        
        Args:
            media_urls: Список URL медиафайлов
            account: Аккаунт для загрузки
            
        Returns:
            Список идентификаторов загруженных медиа для вставки в пост
        """
        pass

    @abstractmethod
    async def get_rate_limit_info(self, account: VKAccount) -> Dict[str, Any]:
        """
        Возвращает информацию о текущих лимитах
        
        Args:
            account: Аккаунт для проверки
            
        Returns:
            Информация о лимитах
        """
        pass

    @abstractmethod
    async def schedule_post(self, post: SocialPost, account: VKAccount, publish_at: datetime) -> Optional[int]:
        """
        Планирует публикацию поста на указанное время
        
        Args:
            post: Пост для публикации
            account: Аккаунт для публикации
            publish_at: Время публикации
            
        Returns:
            ID запланированного поста или None при ошибке
        """
        pass


class ContentFetcherInterface(ABC):
    """
    Интерфейс для получения контента из различных источников
    """

    @abstractmethod
    async def fetch_content(self) -> List[SocialPost]:
        """
        Получает контент из источника
        
        Returns:
            Список полученных постов
        """
        pass

    @abstractmethod
    async def check_source_availability(self) -> bool:
        """
        Проверяет доступность источника
        
        Returns:
            True если источник доступен
        """
        pass


class AIProcessorInterface(ABC):
    """
    Интерфейс для обработки контента с помощью ИИ
    """

    @abstractmethod
    async def rewrite_content(self, text: str, title: str = "") -> str:
        """
        Переписывает текст с помощью ИИ
        
        Args:
            text: Исходный текст
            title: Заголовок
            
        Returns:
            Переписанный текст
        """
        pass

    @abstractmethod
    async def summarize_content(self, texts: List[str]) -> str:
        """
        Создает суммаризацию нескольких текстов
        
        Args:
            texts: Список текстов для суммаризации
            
        Returns:
            Суммаризированный текст
        """
        pass

    @abstractmethod
    async def check_model_availability(self) -> bool:
        """
        Проверяет доступность модели ИИ
        
        Returns:
            True если модель доступна
        """
        pass


class StorageInterface(ABC):
    """
    Интерфейс для хранения данных
    """

    @abstractmethod
    async def save_post(self, post: SocialPost) -> SocialPost:
        """
        Сохраняет пост в хранилище
        
        Args:
            post: Пост для сохранения
            
        Returns:
            Сохраненный пост с ID
        """
        pass

    @abstractmethod
    async def get_post(self, post_id: int) -> Optional[SocialPost]:
        """
        Получает пост по ID
        
        Args:
            post_id: ID поста
            
        Returns:
            Пост или None если не найден
        """
        pass

    @abstractmethod
    async def update_post_status(self, post_id: int, status: str) -> bool:
        """
        Обновляет статус поста
        
        Args:
            post_id: ID поста
            status: Новый статус
            
        Returns:
            True если обновление успешно
        """
        pass

    @abstractmethod
    async def get_pending_posts(self, limit: int = 100) -> List[SocialPost]:
        """
        Получает посты в ожидании обработки
        
        Args:
            limit: Максимальное количество постов
            
        Returns:
            Список постов
        """
        pass

    @abstractmethod
    async def get_posts_by_status(self, status: str, limit: int = 100) -> List[SocialPost]:
        """
        Получает посты по статусу
        
        Args:
            status: Статус для фильтрации
            limit: Максимальное количество постов
            
        Returns:
            Список постов
        """
        pass

    @abstractmethod
    async def delete_post(self, post_id: int) -> bool:
        """
        Удаляет пост из хранилища
        
        Args:
            post_id: ID поста для удаления
            
        Returns:
            True если удаление успешно
        """
        pass


class ModerationInterface(ABC):
    """
    Интерфейс для модерации контента
    """

    @abstractmethod
    async def send_for_moderation(self, post: SocialPost) -> str:
        """
        Отправляет пост на модерацию
        
        Args:
            post: Пост для модерации
            
        Returns:
            ID задачи модерации
        """
        pass

    @abstractmethod
    async def get_moderation_decision(self, moderation_id: str) -> Optional[ModerationDecision]:
        """
        Получает решение модератора
        
        Args:
            moderation_id: ID задачи модерации
            
        Returns:
            Решение модератора или None если еще не принято
        """
        pass

    @abstractmethod
    async def approve_post(self, moderation_id: str) -> bool:
        """
        Одобряет пост
        
        Args:
            moderation_id: ID задачи модерации
            
        Returns:
            True если одобрение успешно
        """
        pass

    @abstractmethod
    async def reject_post(self, moderation_id: str, reason: str = "") -> bool:
        """
        Отклоняет пост
        
        Args:
            moderation_id: ID задачи модерации
            reason: Причина отклонения
            
        Returns:
            True если отклонение успешно
        """
        pass
