"""
Интеграционные тесты парсинга реальных payload-структур VK/Ollama
"""
import json
import os
import sys
from pathlib import Path

# Добавляем src в path для импортов
src_path = Path(__file__).parent / ".." / "src"
sys.path.insert(0, str(src_path.resolve()))

from infrastructure.ollama_processor import OllamaProcessor
from infrastructure.vk_api_client import VKAPIClient


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "integration"


def _load_json(name: str):
    with open(FIXTURES_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def test_extract_model_names_from_ollama_tags_payload():
    payload = _load_json("ollama_tags_payload.json")

    model_names = OllamaProcessor._extract_model_names(payload)

    assert "qwen2.5:1.5b" in model_names
    assert "llama3.1:8b" in model_names


def test_extract_group_info_from_vk_payload_groups_key():
    payload = _load_json("vk_group_payload_groups_key.json")

    group = VKAPIClient._extract_group_info_from_payload(payload)

    assert group["id"] == 123456
    assert group["screen_name"] == "test_group"


def test_extract_group_info_from_vk_payload_response_key():
    payload = _load_json("vk_group_payload_response_key.json")

    group = VKAPIClient._extract_group_info_from_payload(payload)

    assert group["id"] == 123456
    assert group["name"] == "Test Group"
