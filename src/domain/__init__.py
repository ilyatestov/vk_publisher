"""
Domain слой - сущности и интерфейсы
"""
from .entities import (
    SocialPost,
    PostStatus,
    ContentSource,
    VKAccount,
    ModerationDecision
)
from .interfaces import (
    SocialPublisherInterface,
    ContentFetcherInterface,
    AIProcessorInterface,
    StorageInterface,
    ModerationInterface
)

__all__ = [
    "SocialPost",
    "PostStatus",
    "ContentSource",
    "VKAccount",
    "ModerationDecision",
    "SocialPublisherInterface",
    "ContentFetcherInterface",
    "AIProcessorInterface",
    "StorageInterface",
    "ModerationInterface"
]
