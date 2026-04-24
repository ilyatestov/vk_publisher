"""Background content rewrite tasks powered by Ollama."""
from __future__ import annotations

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from src.application.tasks.broker import broker

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b-instruct-q4_K_M"


@broker.task(task_name="rewrite.content")
async def rewrite_content_task(text: str, style: str = "telegram") -> dict[str, str]:
    """Rewrite a source text with quantized Ollama model in a worker process."""
    prompt = (
        "Ты редактор контента для соцсетей. "
        f"Перепиши текст в стиле {style}, сохрани факты, добавь ясную структуру:\n\n{text}"
    )

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(4),
        wait=wait_exponential_jitter(initial=1, max=20),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    ):
        with attempt:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_ctx": 4096,
                            "temperature": 0.6,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()

    return {
        "text": data.get("response", text),
        "model": OLLAMA_MODEL,
    }
