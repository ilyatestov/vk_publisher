"""Системные endpoint'ы."""
import asyncio

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
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
