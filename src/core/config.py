"""
Модуль конфигурации приложения на основе Pydantic v2
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class VKSettings(BaseSettings):
    """Настройки VK API"""
    model_config = SettingsConfigDict(extra='ignore')
    
    access_token: str = Field(default="", validation_alias="VK_ACCESS_TOKEN")
    group_id: int = Field(default=0, validation_alias="VK_GROUP_ID")
    api_version: str = "5.199"
    rate_limit_per_second: float = 3.0
    proxy_list: List[str] = Field(default_factory=list, validation_alias="VK_PROXY_LIST")

    @field_validator('proxy_list', mode='before')
    @classmethod
    def parse_proxy_list(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(',') if p.strip()]
        return v or []


class OllamaSettings(BaseSettings):
    """Настройки Ollama (ИИ)"""
    base_url: str = "http://localhost:11434"
    model_name: str = "llama2"
    timeout: int = 60
    max_tokens: int = 1000


class DatabaseSettings(BaseSettings):
    """Настройки базы данных"""
    url: str = "sqlite+aiosqlite:///./data/vk_publisher.db"
    echo: bool = False


class TelegramBotSettings(BaseSettings):
    """Настройки Telegram бота"""
    model_config = SettingsConfigDict(extra='ignore')
    
    token: str = Field(default="", validation_alias="TELEGRAM_BOT_TOKEN")
    moderator_chat_id: int = Field(default=0, validation_alias="TELEGRAM_MODERATOR_CHAT_ID")


class SchedulerSettings(BaseSettings):
    """Настройки планировщика"""
    check_interval: int = 60  # секунды
    max_daily_posts: int = 50
    post_interval_minutes: int = 60


class SecuritySettings(BaseSettings):
    """Настройки безопасности"""
    encryption_key: str = Field(default="", description="Ключ для шифрования токенов")
    mask_sensitive_data: bool = True


class LoggingSettings(BaseSettings):
    """Настройки логирования"""
    level: str = "INFO"
    file: str = "logs/app.log"
    rotation: str = "10 MB"
    retention: str = "7 days"


class Settings(BaseSettings):
    """Основной класс настроек приложения"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra='ignore'
    )

    # Legacy поля для обратной совместимости (читаются из старого .env)
    vk_access_token: Optional[str] = Field(default=None, validation_alias="VK_ACCESS_TOKEN")
    vk_group_id_raw: Optional[str] = Field(default=None, validation_alias="VK_GROUP_ID")
    vk_api_version: Optional[str] = Field(default=None, validation_alias="VK_API_VERSION")
    ollama_base_url: Optional[str] = Field(default=None, validation_alias="OLLAMA_BASE_URL")
    llm_model: Optional[str] = Field(default=None, validation_alias="LLM_MODEL")
    telegram_bot_token: Optional[str] = Field(default=None, validation_alias="TELEGRAM_BOT_TOKEN")
    admin_telegram_id_raw: Optional[str] = Field(default=None, validation_alias="ADMIN_TELEGRAM_ID")
    database_path: Optional[str] = Field(default=None, validation_alias="DATABASE_PATH")
    max_posts_per_day: Optional[int] = Field(default=None, validation_alias="MAX_POSTS_PER_DAY")
    proxy_list_raw: Optional[str] = Field(default=None, validation_alias="PROXY_LIST")
    log_level: Optional[str] = Field(default=None, validation_alias="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, validation_alias="LOG_FILE")
    
    # Вложенные настройки с дефолтными значениями
    vk: VKSettings = Field(default_factory=VKSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    telegram: TelegramBotSettings = Field(default_factory=TelegramBotSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Поддержка legacy полей из старого .env
        if self.vk_access_token and not self.vk.access_token:
            self.vk.access_token = self.vk_access_token
        
        # Парсим group_id из строки (удаляем комментарии)
        if self.vk_group_id_raw:
            group_id_str = self.vk_group_id_raw.split('#')[0].strip()
            if group_id_str and not self.vk.group_id:
                try:
                    self.vk.group_id = int(group_id_str)
                except ValueError:
                    pass
        
        if self.vk_api_version:
            self.vk.api_version = self.vk_api_version
        if self.ollama_base_url:
            self.ollama.base_url = self.ollama_base_url
        if self.llm_model:
            self.ollama.model_name = self.llm_model
        if self.telegram_bot_token and not self.telegram.token:
            self.telegram.token = self.telegram_bot_token
        
        # Парсим admin_telegram_id из строки (удаляем комментарии)
        if self.admin_telegram_id_raw:
            admin_id_str = self.admin_telegram_id_raw.split('#')[0].strip()
            if admin_id_str and not self.telegram.moderator_chat_id:
                try:
                    self.telegram.moderator_chat_id = int(admin_id_str)
                except ValueError:
                    pass
        
        if self.database_path:
            self.database.url = f"sqlite+aiosqlite:///{self.database_path}"
        if self.max_posts_per_day:
            self.scheduler.max_daily_posts = self.max_posts_per_day
        if self.proxy_list_raw:
            # Парсим строку прокси в список (удаляем комментарии)
            proxy_str = self.proxy_list_raw.split('#')[0].strip()
            if proxy_str:
                self.vk.proxy_list = [p.strip() for p in proxy_str.split(',') if p.strip()]
        if self.log_level:
            self.logging.level = self.log_level
        if self.log_file:
            self.logging.file = self.log_file


# Глобальный экземпляр настроек
settings = Settings()
