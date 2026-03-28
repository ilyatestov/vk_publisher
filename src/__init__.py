"""
Конфигурация системы автопостинга ВКонтакте
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'  # Игнорируем неизвестные переменные из старого .env
    )
    
    # VK API настройки
    vk_access_token: str = Field(default="", validation_alias="VK_ACCESS_TOKEN")
    vk_group_id: str = Field(default="", validation_alias="VK_GROUP_ID")
    vk_api_version: str = Field(default="5.131", validation_alias="VK_API_VERSION")
    
    # Telegram бот для модерации
    telegram_bot_token: Optional[str] = Field(default=None, validation_alias="TELEGRAM_BOT_TOKEN")
    admin_telegram_id: Optional[int] = Field(default=None, validation_alias="ADMIN_TELEGRAM_ID")
    
    # Настройки автопостинга
    post_interval_minutes: int = Field(default=60, validation_alias="POST_INTERVAL_MINUTES")
    enable_preview: bool = Field(default=True, validation_alias="ENABLE_PREVIEW")
    max_posts_per_day: int = Field(default=10, validation_alias="MAX_POSTS_PER_DAY")
    
    # Ollama (локальная LLM)
    ollama_base_url: str = Field(default="http://ollama:11434", validation_alias="OLLAMA_BASE_URL")
    llm_model: str = Field(default="qwen2.5:1.5b", validation_alias="LLM_MODEL")
    
    # Прокси (опционально, для парсинга)
    proxy_list: Optional[List[str]] = Field(default=None, validation_alias="PROXY_LIST")
    
    # Логирование
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file: str = Field(default="/app/logs/autoposter.log", validation_alias="LOG_FILE")
    
    # База данных
    database_path: str = Field(default="/app/data/posts.db", validation_alias="DATABASE_PATH")
    
    # Пути к конфигурационным файлам
    sources_config_path: str = "/app/config/sources.json"
    social_links_config_path: str = "/app/config/social_links.json"
    vk_config_path: str = "/app/config/vk_config.json"
    
    @field_validator('admin_telegram_id', mode='before')
    @classmethod
    def parse_admin_id(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            # Удаляем комментарии и пробелы
            v = v.split('#')[0].strip()
            if not v:
                return None
            try:
                return int(v)
            except ValueError:
                return None
        return v
    
    @field_validator('proxy_list', mode='before')
    @classmethod
    def parse_proxy_list(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            # Удаляем комментарии и пробелы
            v = v.split('#')[0].strip()
            if not v:
                return None
            return [p.strip() for p in v.split(',') if p.strip()]
        return v


# Глобальный экземпляр настроек
settings = Settings()
