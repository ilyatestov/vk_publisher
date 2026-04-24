import pytest

from src.application.tasks import rewrite_tasks


class _ResponseStub:
    def raise_for_status(self):
        return None

    def json(self):
        return {"response": "rewritten"}


class _AsyncClientStub:
    def __init__(self, timeout: float):
        self.timeout = timeout
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        self.calls.append((url, json))
        return _ResponseStub()


@pytest.mark.asyncio
async def test_rewrite_content_task_returns_rewritten_text(monkeypatch):
    client = _AsyncClientStub(timeout=90.0)

    def _factory(*args, **kwargs):
        assert kwargs["timeout"] == 90.0
        return client

    monkeypatch.setattr(rewrite_tasks.httpx, "AsyncClient", _factory)

    result = await rewrite_tasks.rewrite_content_task.original_func("Исходный текст", style="news")

    assert result["text"] == "rewritten"
    assert result["model"] == rewrite_tasks.OLLAMA_MODEL
    assert client.calls[0][0] == rewrite_tasks.OLLAMA_URL
    assert client.calls[0][1]["model"] == rewrite_tasks.OLLAMA_MODEL


def test_ollama_model_quantized_profile():
    assert rewrite_tasks.OLLAMA_MODEL.endswith("q4_K_M")
