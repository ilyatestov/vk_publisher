"""Endpoint'ы runtime-конфигов."""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

SOCIAL_LINKS_PATH = Path(__file__).resolve().parents[3] / "config" / "social_links.json"

router = APIRouter(prefix="/api/v1/config", tags=["config"])


async def _read_social_links_config() -> Dict[str, Any]:
    if not SOCIAL_LINKS_PATH.exists():
        return {}

    def _read() -> Dict[str, Any]:
        with open(SOCIAL_LINKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return await asyncio.to_thread(_read)


async def _write_social_links_config(config: Dict[str, Any]) -> None:
    SOCIAL_LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _write() -> None:
        with open(SOCIAL_LINKS_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    await asyncio.to_thread(_write)


@router.get("/social-links")
async def get_social_links_config():
    try:
        config = await _read_social_links_config()
        return {"config": config, "path": str(SOCIAL_LINKS_PATH)}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка JSON-конфига соцсетей: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось прочитать конфиг соцсетей: {e}") from e


@router.put("/social-links")
async def update_social_links_config(payload: Dict[str, Any]):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Ожидался JSON-объект")

    try:
        await _write_social_links_config(payload)
        return {"status": "ok", "message": "Конфигурация соцсетей сохранена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось сохранить конфиг соцсетей: {e}") from e
