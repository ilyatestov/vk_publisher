"""DI/bootstrap контейнер приложения."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from ..core.config import settings
from ..core.logging import log
from ..domain.entities import VKAccount
from ..infrastructure.database import DatabaseStorage
from ..infrastructure.ollama_processor import OllamaProcessor
from ..infrastructure.telegram_bot import TelegramModeratorBot
from ..infrastructure.vk_api_client import VKClient
from ..workers.pipeline import PipelineWorker


@dataclass
class AppContainer:
    """Runtime-компоненты приложения."""

    storage: DatabaseStorage
    processor: OllamaProcessor
    publisher: VKClient
    moderator: TelegramModeratorBot
    pipeline_worker: PipelineWorker
    pipeline_task: asyncio.Task


async def build_container() -> AppContainer:
    """Создает и запускает runtime-контейнер."""
    storage = DatabaseStorage(settings.database.url)
    await storage.initialize()

    processor = OllamaProcessor()
    await processor.__aenter__()

    publisher = VKClient()
    await publisher.__aenter__()

    if await processor.check_model_availability():
        log.success(f"ИИ модель {settings.ollama.model_name} доступна")
    else:
        log.warning(f"ИИ модель {settings.ollama.model_name} недоступна")

    moderator = TelegramModeratorBot()

    default_account = VKAccount(
        id=settings.vk.group_id,
        name="Default Group",
        access_token=settings.vk.access_token,
        daily_quota=settings.scheduler.max_daily_posts,
    )

    pipeline_worker = PipelineWorker(
        storage=storage,
        processor=processor,
        publisher=publisher,
        moderator=moderator,
    )
    pipeline_worker.set_default_account(default_account)

    pipeline_task = asyncio.create_task(pipeline_worker.start_workers(), name="pipeline")

    return AppContainer(
        storage=storage,
        processor=processor,
        publisher=publisher,
        moderator=moderator,
        pipeline_worker=pipeline_worker,
        pipeline_task=pipeline_task,
    )


async def shutdown_container(container: Optional[AppContainer]) -> None:
    """Корректно завершает runtime-компоненты."""
    if container is None:
        return

    if container.pipeline_worker:
        await container.pipeline_worker.shutdown()

    if container.pipeline_task and not container.pipeline_task.done():
        container.pipeline_task.cancel()
        try:
            await container.pipeline_task
        except asyncio.CancelledError:
            log.info("Конвейер остановлен")

    await container.publisher.__aexit__(None, None, None)
    await container.processor.__aexit__(None, None, None)
    await container.storage.close()
