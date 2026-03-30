"""Dependency helpers для FastAPI."""
from fastapi import Request

from ..bootstrap.container import AppContainer


def get_container(request: Request) -> AppContainer:
    """Возвращает runtime-контейнер из app.state."""
    return request.app.state.container
