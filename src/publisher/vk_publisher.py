"""Compatibility shim for legacy publisher module.

Канонический pipeline: ``src.workers.pipeline.PipelineWorker``.
"""
import warnings

warnings.warn(
    "src.publisher.vk_publisher is deprecated; use src.workers.pipeline.PipelineWorker",
    DeprecationWarning,
    stacklevel=2,
)

from ..legacy.vk_publisher import *  # noqa: F401,F403
