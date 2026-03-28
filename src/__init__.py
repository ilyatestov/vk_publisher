"""
Конфигурация системы автопостинга ВКонтакте
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # VK API настройки
    vk_access_token: str = Field(..., env="VK_ACCESS_TOKEN")
    vk_group_id: str = Field(..., env="VK_GROUP_ID")
    vk_api_version: str = Field(default="5.131", env="VK_API_VERSION")
    
    # Telegram бот для модерации
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    admin_telegram_id: Optional[int] = Field(default=None, env="ADMIN_TELEGRAM_ID")
    
    # Настройки автопостинга
    post_interval_minutes: int = Field(default=60, env="POST_INTERVAL_MINUTES")
    enable_preview: bool = Field(default=True, env="ENABLE_PREVIEW")
    max_posts_per_day: int = Field(default=10, env="MAX_POSTS_PER_DAY")
    
    # Ollama (локальная LLM)
    ollama_base_url: str = Field(default="http://ollama:11434", env="OLLAMA_BASE_URL")
    llm_model: str = Field(default="qwen2.5:1.5b", env="LLM_MODEL")
    
    # Прокси (опционально, для парсинга)
    proxy_list: Optional[List[str]] = Field(default=None, env="PROXY_LIST")
    
    # Логирование
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="/app/logs/autoposter.log", env="LOG_FILE")
    
    # База данных
    database_path: str = Field(default="/app/data/posts.db", env="DATABASE_PATH")
    
    # Пути к конфигурационным файлам
    sources_config_path: str = "/app/config/sources.json"
    social_links_config_path: str = "/app/config/social_links.json"
    vk_config_path: str = "/app/config/vk_config.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()
