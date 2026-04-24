"""TaskIQ broker configuration for background AI jobs."""
from __future__ import annotations

from taskiq import TaskiqEvents
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.core.config import settings

redis_url = settings.redis.url if hasattr(settings, "redis") else "redis://redis:6379/0"

broker = ListQueueBroker(url=redis_url).with_result_backend(
    RedisAsyncResultBackend(redis_url)
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup() -> None:
    """Hook for worker startup actions (metrics, warmup, etc)."""


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown() -> None:
    """Hook for graceful worker shutdown."""
