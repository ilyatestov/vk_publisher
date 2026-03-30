"""Endpoint'ы статистики."""
from fastapi import APIRouter, Depends

from ..deps import get_container
from ...bootstrap.container import AppContainer

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get("/stats")
async def get_statistics(container: AppContainer = Depends(get_container)):
    stats = await container.storage.get_statistics()
    return {"statistics": stats}
