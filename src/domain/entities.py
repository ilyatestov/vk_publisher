"""
Сущности предметной области
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PostStatus(str, Enum):
    """Статусы поста в системе"""
    NEW = "new"
    FETCHED = "fetched"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PENDING_MODERATION = "pending_moderation"
    MODERATED = "moderated"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class ContentSource(str, Enum):
    """Типы источников контента"""
    RSS = "rss"
    WEB = "web"
    VK_SEARCH = "vk_search"
    MANUAL = "manual"


class ModerationDecision(str, Enum):
    """Решения модератора"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class SocialPost(BaseModel):
    """
    Сущность поста для публикации в социальной сети
    
    Attributes:
        id: Уникальный идентификатор поста в БД
        title: Заголовок поста
        content: Основной текст поста
        source_url: URL источника контента
        image_urls: Список URL изображений для прикрепления
        tags: Список тегов/хэштегов
        scheduled_at: запланированное время публикации
        status: Текущий статус поста
        source_type: Тип источника контента
        created_at: Время создания записи
        updated_at: Время последнего обновления
        metadata: Дополнительные метаданные
    """
    id: Optional[int] = None
    title: str
    content: str
    source_url: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    status: PostStatus = PostStatus.NEW
    source_type: ContentSource
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def mark_processed(self) -> None:
        """Отмечает пост как обработанный"""
        self.status = PostStatus.PROCESSED
        self.updated_at = datetime.utcnow()

    def mark_published(self) -> None:
        """Отмечает пост как опубликованный"""
        self.status = PostStatus.PUBLISHED
        self.updated_at = datetime.utcnow()

    def mark_failed(self) -> None:
        """Отмечает пост как неудачный"""
        self.status = PostStatus.FAILED
        self.updated_at = datetime.utcnow()

    def schedule_for(self, dt: datetime) -> None:
        """Планирует публикацию на указанное время"""
        self.scheduled_at = dt
        self.status = PostStatus.SCHEDULED
        self.updated_at = datetime.utcnow()

    @property
    def is_ready_to_publish(self) -> bool:
        """Проверяет, готов ли пост к публикации"""
        if self.status not in [PostStatus.MODERATED, PostStatus.SCHEDULED]:
            return False
        
        if self.scheduled_at and self.scheduled_at > datetime.utcnow():
            return False
        
        return True


class VKAccount(BaseModel):
    """
    Сущность аккаунта ВКонтакте
    
    Attributes:
        id: Уникальный идентификатор аккаунта
        name: Название аккаунта/группы
        access_token: Токен доступа (может быть зашифрован)
        daily_quota: Дневная квота на публикацию
        posts_today: Количество постов сегодня
        last_reset_date: Дата последнего сброса счетчика
        is_active: Активен ли аккаунт
    """
    id: int
    name: str
    access_token: str
    daily_quota: int = 50
    posts_today: int = 0
    last_reset_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    def reset_daily_counter(self) -> None:
        """Сбрасывает счетчик постов за день"""
        today = datetime.utcnow().date()
        if self.last_reset_date.date() < today:
            self.posts_today = 0
            self.last_reset_date = datetime.utcnow()

    def can_post(self) -> bool:
        """Проверяет, можно ли публиковать посты"""
        self.reset_daily_counter()
        return self.is_active and self.posts_today < self.daily_quota

    def increment_post_count(self) -> None:
        """Увеличивает счетчик опубликованных постов"""
        self.posts_today += 1
