"""Background publishing tasks with cross-platform support."""
from __future__ import annotations

import asyncio
from typing import Optional

from src.application.tasks.broker import broker
from src.domain.publishers.base import PublishPayload, PublishResult


@broker.task(task_name="publish.cross_platform")
async def publish_cross_platform_task(
    text: str,
    platforms: list[str],
    media_urls: list[str] | None = None,
    hashtags: list[str] | None = None,
    scheduled_at: str | None = None,
) -> dict[str, dict]:
    """
    Публикует пост одновременно в несколько платформ.
    
    Args:
        text: Текст поста
        platforms: Список платформ ['vk', 'telegram', 'dzen']
        media_urls: URL медиафайлов
        hashtags: Хэштеги
        scheduled_at: ISO формат времени публикации
        
    Returns:
        Словарь результатов по платформам
    """
    from datetime import datetime
    
    payload = PublishPayload(
        text=text,
        media_urls=media_urls or [],
        hashtags=hashtags or [],
        scheduled_at=datetime.fromisoformat(scheduled_at) if scheduled_at else None,
    )
    
    results = {}
    
    async def publish_to_platform(platform: str) -> tuple[str, PublishResult]:
        if platform == "vk":
            from src.infrastructure.publishers.vk_publisher import VKPublisherAdapter
            # Инициализация через DI контейнер (упрощённо)
            result = PublishResult(ok=False, error="VK publisher not configured")
        elif platform == "telegram":
            from src.infrastructure.publishers.telegram_publisher import TelegramPublisher
            # Инициализация через DI контейнер (упрощённо)
            result = PublishResult(ok=False, error="Telegram publisher not configured")
        else:
            result = PublishResult(ok=False, error=f"Unknown platform: {platform}")
        
        return platform, result
    
    tasks = [publish_to_platform(p) for p in platforms]
    completed = await asyncio.gather(*tasks, return_exceptions=True)
    
    for item in completed:
        if isinstance(item, Exception):
            results["error"] = str(item)
        else:
            platform, result = item
            results[platform] = {
                "ok": result.ok,
                "duplicate": result.duplicate,
                "post_id": result.platform_post_id,
                "error": result.error,
            }
    
    return results


@broker.task(task_name="publish.scheduled")
async def publish_scheduled_task(
    post_id: int,
    platform: str,
) -> dict:
    """
    Публикует отложенный пост по расписанию.
    
    Args:
        post_id: ID поста в БД
        platform: Платформа для публикации
        
    Returns:
        Результат публикации
    """
    from src.infrastructure.database import DatabaseStorage
    from src.core.config import settings
    
    storage = DatabaseStorage(settings.database.url)
    await storage.initialize()
    
    # Получаем пост из БД
    post = await storage.get_post(post_id)
    if not post:
        return {"error": f"Post {post_id} not found"}
    
    payload = PublishPayload(
        text=post.content,
        media_urls=post.image_urls,
        hashtags=post.tags,
        metadata={"title": post.title, "post_id": post_id},
    )
    
    if platform == "vk":
        from src.infrastructure.publishers.vk_publisher import VKPublisherAdapter
        # Публикация в VK
        result = PublishResult(ok=False, error="VK publisher not configured")
    elif platform == "telegram":
        from src.infrastructure.publishers.telegram_publisher import TelegramPublisher
        # Публикация в Telegram
        result = PublishResult(ok=False, error="Telegram publisher not configured")
    else:
        result = PublishResult(ok=False, error=f"Unknown platform: {platform}")
    
    await storage.close()
    
    return {
        "post_id": post_id,
        "platform": platform,
        "ok": result.ok,
        "duplicate": result.duplicate,
        "platform_post_id": result.platform_post_id,
        "error": result.error,
    }
