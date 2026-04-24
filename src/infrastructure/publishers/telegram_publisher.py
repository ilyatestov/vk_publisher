"""Telegram publisher implementation with retry and circuit breaker."""
from __future__ import annotations

import hashlib
from typing import Optional

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


class TelegramPublisher(BasePublisher):
    """Adapter for publishing posts to Telegram channels/groups."""

    platform = "telegram"

    def __init__(
        self,
        bot_token: str,
        chat_id: int,
        storage: DatabaseStorage,
    ) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._storage = storage
        self._breaker = CircuitBreaker(fail_max=5, timeout_duration=30)
        self._base_url = f"https://api.telegram.org/bot{bot_token}"

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
        import httpx

        key = self._build_idempotency_key(payload)

        if await self._storage.is_publication_key_used(key):
            return PublishResult(ok=True, duplicate=True)

        # Формируем текст с хэштегами
        text = payload.text
        if payload.hashtags:
            text += "\n\n" + " ".join(payload.hashtags)

        post = SocialPost(
            title=payload.metadata.get("title") or "",
            content=text,
            image_urls=payload.media_urls,
            tags=payload.hashtags,
            scheduled_at=payload.scheduled_at,
            source_type=ContentSource.MANUAL,
            metadata={"idempotency_key": key},
        )

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(4),
            wait=wait_exponential_jitter(initial=1, max=30),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        ):
            with attempt:
                published = await self._breaker.call_async(
                    self._send_message,
                    text,
                    payload.media_urls,
                )
                if not published:
                    raise RuntimeError("Telegram publish failed")

        await self._storage.register_publication_key(
            idempotency_key=key,
            vk_post_id=post.metadata.get("telegram_message_id"),
        )

        return PublishResult(
            ok=True,
            platform_post_id=str(post.metadata.get("telegram_message_id"))
            if post.metadata.get("telegram_message_id")
            else None,
        )

    async def _send_message(
        self, text: str, media_urls: list[str]
    ) -> bool:
        """Отправляет сообщение в Telegram."""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            if media_urls:
                # Отправка с медиа (фото)
                url = f"{self._base_url}/sendPhoto"
                files = {"photo": open(media_urls[0], "rb") if media_urls[0].startswith("/") else None}
                data = {
                    "chat_id": self._chat_id,
                    "caption": text,
                    "parse_mode": "HTML",
                }
                if files["photo"] is None:
                    # Если URL, а не локальный файл
                    data["photo"] = media_urls[0]
                    files = None
                
                response = await client.post(url, data=data, files=files)
            else:
                # Текстовое сообщение
                url = f"{self._base_url}/sendMessage"
                response = await client.post(
                    url,
                    json={
                        "chat_id": self._chat_id,
                        "text": text,
                        "parse_mode": "HTML",
                    },
                )

            response.raise_for_status()
            result = response.json()
            return result.get("ok", False)

    async def healthcheck(self) -> bool:
        """Проверяет доступность Telegram Bot API."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self._base_url}/getMe"
                )
                return response.json().get("ok", False)
        except Exception:
            return False
