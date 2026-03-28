"""
VK Publisher v2.0 - Main Entry Point

Асинхронное приложение для автопостинга ВКонтакте с:
- Clean Architecture
- Конвейерной обработкой через asyncio.Queue
- REST API на FastAPI
- Метриками Prometheus
- Telegram модерацией
"""
import asyncio
import signal
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .core.logging import log
from .core.config import settings
from .domain.entities import VKAccount, ContentSource
from .infrastructure.database import DatabaseStorage
from .infrastructure.vk_api_client import VKClient
from .infrastructure.ollama_processor import OllamaProcessor
from .infrastructure.telegram_bot import TelegramModeratorBot
from .workers.pipeline import PipelineWorker


# Глобальные переменные для управления жизненным циклом
pipeline_worker: PipelineWorker = None
pipeline_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Управление жизненным циклом приложения"""
    global pipeline_worker, pipeline_task
    
    log.info("=" * 60)
    log.info("Инициализация VK Publisher v2.0...")
    log.info("=" * 60)
    
    # Инициализация базы данных
    storage = DatabaseStorage(settings.database.url)
    await storage.initialize()
    
    # Создание компонентов
    async with OllamaProcessor() as processor, VKClient() as publisher:
        # Проверка доступности модели ИИ
        if await processor.check_model_availability():
            log.success(f"ИИ модель {settings.ollama.model_name} доступна")
        else:
            log.warning(f"ИИ модель {settings.ollama.model_name} недоступна")
        
        # Инициализация Telegram бота для модерации
        moderator = TelegramModeratorBot()
        
        # Создание аккаунта по умолчанию
        default_account = VKAccount(
            id=settings.vk.group_id,
            name="Default Group",
            access_token=settings.vk.access_token,
            daily_quota=settings.scheduler.max_daily_posts
        )
        
        # Создание конвейера
        pipeline_worker = PipelineWorker(
            storage=storage,
            processor=processor,
            publisher=publisher,
            moderator=moderator
        )
        pipeline_worker.set_default_account(default_account)
        
        # Запуск воркеров в фоне
        pipeline_task = asyncio.create_task(
            pipeline_worker.start_workers(),
            name="pipeline"
        )
        
        log.info("Все компоненты инициализированы")
        log.info("=" * 60)
        
        yield
        
        # Завершение работы
        log.info("=" * 60)
        log.info("Завершение работы приложения...")
        
        if pipeline_worker:
            await pipeline_worker.shutdown()
        
        if pipeline_task and not pipeline_task.done():
            pipeline_task.cancel()
            try:
                await pipeline_task
            except asyncio.CancelledError:
                log.info("Конвейер остановлен")
        
        await storage.close()
        log.info("Приложение остановлено")
        log.info("=" * 60)


# Создание FastAPI приложения
app = FastAPI(
    title="VK Publisher API",
    description="REST API для системы автопостинга ВКонтакте",
    version="2.0.0",
    lifespan=lifespan
)

# Добавление метрик Prometheus
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health_check():
    """
    Health check endpoint для Docker/K8s
    
    Returns:
        Статус здоровья приложения
    """
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/")
async def root():
    """Корневой endpoint с информацией о приложении"""
    return {
        "name": "VK Publisher",
        "version": "2.0.0",
        "description": "Система автопостинга ВКонтакте с ИИ-обработкой",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/api/v1/stats")
async def get_statistics():
    """Получение статистики по постам"""
    from .infrastructure.database import DatabaseStorage
    storage = DatabaseStorage(settings.database.url)
    try:
        await storage.initialize()
        stats = await storage.get_statistics()
        return {"statistics": stats}
    finally:
        await storage.close()


def main():
    """Точка входа для запуска через uvicorn"""
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
