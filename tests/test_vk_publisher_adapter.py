import pytest

from src.domain.entities import VKAccount
from src.domain.publishers.base import PublishPayload
from src.infrastructure.publishers.vk_publisher import VKPublisherAdapter


class _StorageStub:
    def __init__(self, used: bool = False):
        self.used = used
        self.registered = []

    async def is_publication_key_used(self, key: str) -> bool:
        return self.used

    async def register_publication_key(self, idempotency_key: str, vk_post_id: int | None = None) -> None:
        self.registered.append((idempotency_key, vk_post_id))


class _VKClientStub:
    def __init__(self, should_publish: bool = True):
        self.should_publish = should_publish
        self.calls = 0

    async def publish_post(self, post, account):
        self.calls += 1
        if self.should_publish:
            post.metadata["vk_post_id"] = 101
        return self.should_publish


@pytest.mark.asyncio
async def test_publish_skips_duplicates():
    storage = _StorageStub(used=True)
    client = _VKClientStub()
    account = VKAccount(id=1, name="group", access_token="token")
    adapter = VKPublisherAdapter(vk_client=client, storage=storage, account=account)

    result = await adapter.publish(PublishPayload(text="hello"))

    assert result.ok is True
    assert result.duplicate is True
    assert client.calls == 0
    assert storage.registered == []


@pytest.mark.asyncio
async def test_publish_registers_idempotency_key_after_success():
    storage = _StorageStub(used=False)
    client = _VKClientStub(should_publish=True)
    account = VKAccount(id=1, name="group", access_token="token")
    adapter = VKPublisherAdapter(vk_client=client, storage=storage, account=account)

    result = await adapter.publish(PublishPayload(text="hello", hashtags=["vk"]))

    assert result.ok is True
    assert result.platform_post_id == "101"
    assert client.calls == 1
    assert len(storage.registered) == 1
