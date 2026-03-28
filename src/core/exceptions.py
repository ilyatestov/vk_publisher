"""
Модуль исключений приложения
"""


class VKPublisherError(Exception):
    """Базовое исключение для приложения VK Publisher"""
    pass


class VKAPIError(VKPublisherError):
    """Исключение для ошибок VK API"""
    def __init__(self, message: str, error_code: int = None):
        self.message = message
        self.error_code = error_code
        super().__init__(f"VK API Error {error_code}: {message}" if error_code else message)


class VKAuthError(VKAPIError):
    """Ошибка аутентификации VK (код 5)"""
    def __init__(self, message: str = "Invalid access token"):
        super().__init__(message, error_code=5)


class VKRateLimitError(VKAPIError):
    """Превышение лимита запросов VK (код 6)"""
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, error_code=6)


class VKPermissionError(VKAPIError):
    """Ошибка прав доступа VK (код 9)"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, error_code=9)


class VKCaptchaError(VKAPIError):
    """Требуется ввод капчи VK (код 14)"""
    def __init__(self, message: str = "Captcha required", captcha_sid: str = None, captcha_img: str = None):
        self.captcha_sid = captcha_sid
        self.captcha_img = captcha_img
        super().__init__(message, error_code=14)


class OllamaError(VKPublisherError):
    """Исключение для ошибок Ollama API"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"Ollama Error {status_code}: {message}" if status_code else message)


class OllamaTimeoutError(OllamaError):
    """Таймаут при обращении к Ollama"""
    def __init__(self, message: str = "Ollama request timeout"):
        super().__init__(message)


class DatabaseError(VKPublisherError):
    """Исключение для ошибок базы данных"""
    pass


class ContentFetchError(VKPublisherError):
    """Исключение для ошибок получения контента"""
    pass


class ModerationError(VKPublisherError):
    """Исключение для ошибок модерации"""
    pass


class ConfigurationError(VKPublisherError):
    """Исключение для ошибок конфигурации"""
    pass
