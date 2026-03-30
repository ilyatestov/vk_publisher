"""Системные endpoint'ы."""
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..deps import get_container
from ...bootstrap.container import AppContainer

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/")
async def root():
    return {
        "name": "VK Publisher",
        "version": "2.0.0",
        "description": "Система автопостинга ВКонтакте с ИИ-обработкой",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@router.get("/api/v1/system/runtime")
async def runtime_overview(container: AppContainer = Depends(get_container)):
    """Быстрый runtime-overview для отладки очередей и воркеров."""
    worker = container.pipeline_worker
    return {
        "queues": {
            "processor": worker.processor_queue.qsize(),
            "moderation": worker.moderation_queue.qsize(),
            "publisher": worker.publisher_queue.qsize(),
        },
        "moderation_tasks_active": len(worker._moderation_tasks),  # pylint: disable=protected-access
        "fetched_sleep_bounds_sec": {
            "min": worker._fetcher_sleep_min,  # pylint: disable=protected-access
            "max": worker._fetcher_sleep_max,  # pylint: disable=protected-access
        },
    }
