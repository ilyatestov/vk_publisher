"""
VK Publisher v2.0 - Main Entry Point

Асинхронное приложение для автопостинга ВКонтакте с:
- Clean Architecture
- Конвейерной обработкой через asyncio.Queue
- REST API на FastAPI
- Метриками Prometheus
- Telegram модерацией
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .api.routes.config import router as config_router
from .api.routes.stats import router as stats_router
from .api.routes.system import router as system_router
from .bootstrap.container import AppContainer, build_container, shutdown_container
from .core.logging import log


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Управление жизненным циклом приложения"""
    log.info("=" * 60)
    log.info("Инициализация VK Publisher v2.0...")
    log.info("=" * 60)

    container: AppContainer = await build_container()
    app.state.container = container

    log.info("Все компоненты инициализированы")
    log.info("=" * 60)

    yield

    log.info("=" * 60)
    log.info("Завершение работы приложения...")
    await shutdown_container(getattr(app.state, "container", None))
    log.info("Приложение остановлено")
    log.info("=" * 60)


app = FastAPI(
    title="VK Publisher API",
    description="REST API для системы автопостинга ВКонтакте",
    version="2.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(system_router)
app.include_router(stats_router)
app.include_router(config_router)


def main():
    """Точка входа для запуска через uvicorn"""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
