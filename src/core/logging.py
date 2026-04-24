"""
Модуль логирования с маскировкой чувствительных данных
"""
import json
import re
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from .config import settings


def mask_sensitive_data(message: str) -> str:
    """
    Маскирует чувствительные данные в сообщениях логов
    
    Args:
        message: Исходное сообщение
        
    Returns:
        Сообщение с замаскированными токенами и секретами
    """
    if not settings.security.mask_sensitive_data:
        return message
    
    # Маскировка токенов VK (access_token=...)
    token_pattern = r'access_token=[\w\d]+'  # nosec B105 - используется для маскировки, не для хранения
    message = re.sub(token_pattern, 'access_token=***', message)
    
    # Маскировка URL с токенами
    url_token_pattern = r'(https?://\S*token=\w+)'  # nosec B105 - используется для маскировки
    message = re.sub(url_token_pattern, lambda m: m.group(1)[:30] + '***', message)
    
    # Маскировка Telegram токенов
    tg_token_pattern = r'[0-9]+:[A-Za-z0-9_-]{35}'  # nosec B105 - используется для маскировки
    message = re.sub(tg_token_pattern, '***', message)
    
    # Маскировка ключей шифрования
    key_pattern = r'encryption_key=[\w\d]+'
    message = re.sub(key_pattern, 'encryption_key=***', message)
    
    return message


def serialize_record(record) -> str:
    """
    Сериализует запись лога в JSON формат
    
    Args:
        record: Запись лога от loguru (может быть dict или Message object)
        
    Returns:
        JSON строка с данными лога
    """
    try:
        # Loguru передает record как dict через **kwargs
        # Но при вызове функции напрямую может прийти Message object
        if hasattr(record, '__getitem__'):
            # Это dict-like объект
            time_obj = record.get("time")
            level_obj = record.get("level", {})
            message_text = str(record.get("message", ""))
            module_name = record.get("name", "")
            func_name = record.get("function", "")
            line_num = record.get("line", "")
            extra_data = record.get("extra", {})
        else:
            # Это Message object от loguru
            time_obj = getattr(record, 'time', None)
            level_obj = getattr(record, 'level', 'INFO')
            message_text = str(getattr(record, 'message', ''))
            module_name = getattr(record, 'name', '')
            func_name = getattr(record, 'function', '')
            line_num = getattr(record, 'line', '')
            extra_data = getattr(record, 'extra', {})
        
        # Получаем timestamp корректно
        if hasattr(time_obj, "timestamp"):
            timestamp = datetime.fromtimestamp(time_obj.timestamp()).isoformat()
        elif isinstance(time_obj, str):
            timestamp = time_obj
        else:
            timestamp = datetime.now().isoformat()
        
        # Получаем уровень лога
        if isinstance(level_obj, dict):
            level_name = level_obj.get("name", "INFO")
        elif hasattr(level_obj, "name"):
            level_name = level_obj.name
        else:
            level_name = str(level_obj)
        
        subset = {
            "timestamp": timestamp,
            "level": level_name,
            "message": mask_sensitive_data(message_text),
            "module": module_name,
            "function": func_name,
            "line": line_num,
            "extra": extra_data
        }
        return json.dumps(subset, ensure_ascii=False)
    except Exception as e:
        # Fallback для ошибок сериализации
        return json.dumps({"error": f"Serialization error: {str(e)}"}, ensure_ascii=False)


def setup_logger() -> logger:
    """
    Настройка структурированного логирования
    
    Returns:
        Настроенный экземпляр logger
    """
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Консольный вывод с цветом
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.logging.level,
        colorize=True
    )
    
    # Файловый вывод с ротацией
    logger.add(
        settings.logging.file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        level=settings.logging.level,
        filter=lambda record: mask_sensitive_data(record["message"])
    )
    
    # JSON логирование для сбора метрик
    logger.add(
        serialize_record,
        format="{message}",
        level="INFO"
    )

    logger.info("Логгер настроен")
    return logger


# Глобальный экземпляр логгера
log = setup_logger()
