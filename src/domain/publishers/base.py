"""Domain contracts for social publishers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PublishPayload:
    """Cross-platform payload for posting content to social channels."""

    text: str
    media_urls: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    scheduled_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PublishResult:
    """Unified publishing result to simplify orchestration logic."""

    ok: bool
    platform_post_id: str | None = None
    duplicate: bool = False
    error: str | None = None


class BasePublisher(ABC):
    """Asynchronous abstraction for multi-channel publishing (VK, Telegram, etc)."""

    platform: str

    @abstractmethod
    async def publish(self, payload: PublishPayload) -> PublishResult:
        """Publish text/media payload to a target social channel."""

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Return provider availability for health probes and circuit opening logic."""
