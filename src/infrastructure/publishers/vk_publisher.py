"""VK publisher implementation with retry, idempotency and circuit breaker."""
from __future__ import annotations

import hashlib

from aiobreaker import CircuitBreaker
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from src.domain.entities import ContentSource, SocialPost, VKAccount
from src.domain.publishers.base import BasePublisher, PublishPayload, PublishResult
from src.infrastructure.database import DatabaseStorage
from src.infrastructure.vk_api_client import VKClient


class VKPublisherAdapter(BasePublisher):
    """Adapter over VKClient that follows the new BasePublisher contract."""

    platform = "vk"

    def __init__(
        self,
        vk_client: VKClient,
        storage: DatabaseStorage,
        account: VKAccount,
    ) -> None:
        self._vk_client = vk_client
        self._storage = storage
        self._account = account
        self._breaker = CircuitBreaker(fail_max=5, timeout_duration=30)

    @staticmethod
    def _build_idempotency_key(payload: PublishPayload) -> str:
        raw = "|".join(
            [
                payload.text.strip(),
                ",".join(sorted(payload.media_urls)),
                ",".join(sorted(payload.hashtags)),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def publish(self, payload: PublishPayload) -> PublishResult:
        key = self._build_idempotency_key(payload)

        if await self._storage.is_publication_key_used(key):
            return PublishResult(ok=True, duplicate=True)

        post = SocialPost(
            title=payload.metadata.get("title") or "",
            content=payload.text,
            image_urls=payload.media_urls,
            tags=payload.hashtags,
            scheduled_at=payload.scheduled_at,
            source_type=ContentSource.MANUAL,
            metadata={"idempotency_key": key, **payload.metadata},
        )

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(4),
            wait=wait_exponential_jitter(initial=1, max=30),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        ):
            with attempt:
                published = await self._breaker.call_async(
                    self._vk_client.publish_post,
                    post,
                    self._account,
                )
                if not published:
                    raise RuntimeError("VK publish failed")

        await self._storage.register_publication_key(
            idempotency_key=key,
            vk_post_id=post.metadata.get("vk_post_id"),
        )

        return PublishResult(
            ok=True,
            platform_post_id=str(post.metadata.get("vk_post_id")) if post.metadata.get("vk_post_id") else None,
        )

    async def healthcheck(self) -> bool:
        return self._breaker.current_state != "open"
