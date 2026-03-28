"""
Асинхронный процессор ИИ на основе Ollama API
"""
import asyncio
import aiohttp
from typing import List, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from ..core.logging import log
from ..core.config import settings
from ..core.exceptions import OllamaError, OllamaTimeoutError
from ..domain.interfaces import AIProcessorInterface


class OllamaProcessor(AIProcessorInterface):
    """
    Асинхронный процессор для работы с Ollama API
    
    Поддерживает:
    - Рерайт текста
    - Суммаризацию нескольких текстов
    - Проверку доступности модели
    - Retry-логику при сбоях
    """

    def __init__(self):
        self.base_url = settings.ollama.base_url.rstrip('/')
        self.model_name = settings.ollama.model_name
        self.timeout_seconds = settings.ollama.timeout
        self.max_tokens = settings.ollama.max_tokens
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Создает HTTP-сессию при входе в контекст"""
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        self.session = aiohttp.ClientSession(timeout=timeout)
        log.info(f"Ollama сессия создана (модель: {self.model_name})")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрывает HTTP-сессию при выходе из контекста"""
        if self.session:
            await self.session.close()
            log.info("Ollama сессия закрыта")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((OllamaError, aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def _generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Выполняет генерацию текста через Ollama API
        
        Args:
            prompt: Промпт для генерации
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации (0.0-1.0)
            
        Returns:
            Сгенерированный текст
            
        Raises:
            OllamaError: При ошибке API
            OllamaTimeoutError: При таймауте
        """
        if not self.session:
            raise OllamaError("Сессия не инициализирована. Используйте async with.")

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "max_tokens": max_tokens or self.max_tokens
            }
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    log.error(f"Ollama API error: {response.status} - {error_text}")
                    raise OllamaError(
                        f"Ollama API returned status {response.status}",
                        status_code=response.status
                    )

                result = await response.json()
                generated_text = result.get('response', '').strip()

                if not generated_text:
                    log.warning("Ollama вернул пустой результат")
                    raise OllamaError("Пустой ответ от Ollama")

                return generated_text

        except asyncio.TimeoutError:
            log.error(f"Таймаут при обращении к Ollama (> {self.timeout_seconds}s)")
            raise OllamaTimeoutError()
        except aiohttp.ClientError as e:
            log.error(f"Network error при обращении к Ollama: {e}")
            raise OllamaError(f"Network error: {str(e)}")

    async def rewrite_content(self, text: str, title: str = "") -> str:
        """
        Переписывает текст с помощью ИИ
        
        Args:
            text: Исходный текст для рерайта
            title: Заголовок (опционально)
            
        Returns:
            Переписанный текст
        """
        prompt = self._create_rewrite_prompt(text, title)
        
        log.info(f"Начало рерайта текста (длина: {len(text)} символов)")
        
        try:
            rewritten = await self._generate(
                prompt,
                max_tokens=min(self.max_tokens, 2000),
                temperature=0.7
            )
            
            log.success(f"Текст успешно переписан (длина: {len(rewritten)} символов)")
            return rewritten
            
        except (OllamaError, RetryError) as e:
            log.error(f"Ошибка при рерайте текста: {e}")
            # Возвращаем исходный текст при ошибке
            return text

    async def summarize_content(self, texts: List[str]) -> str:
        """
        Создает суммаризацию нескольких текстов
        
        Args:
            texts: Список текстов для суммаризации
            
        Returns:
            Суммаризированный текст
        """
        if not texts:
            log.warning("Пустой список текстов для суммаризации")
            return ""

        if len(texts) == 1:
            return texts[0]

        # Берем максимум 5 статей для суммаризации
        limited_texts = texts[:5]
        
        prompt = self._create_summary_prompt(limited_texts)
        
        log.info(f"Начало суммаризации {len(limited_texts)} текстов")
        
        try:
            summary = await self._generate(
                prompt,
                max_tokens=min(self.max_tokens // 2, 500),
                temperature=0.5  # Более детерминированная генерация для суммаризации
            )
            
            log.success(f"Суммаризация выполнена (длина: {len(summary)} символов)")
            return summary
            
        except (OllamaError, RetryError) as e:
            log.error(f"Ошибка при суммаризации: {e}")
            # Возвращаем первый текст при ошибке
            return limited_texts[0] if limited_texts else ""

    async def check_model_availability(self) -> bool:
        """
        Проверяет доступность модели
        
        Returns:
            True если модель доступна
        """
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get(f"{self.base_url}/api/tags") as response:
                        if response.status == 200:
                            result = await response.json()
                            models = result.get('models', [])
                            model_names = [m.get('name', '') for m in models]
                            
                            if self.model_name in model_names:
                                log.info(f"Модель {self.model_name} доступна")
                                return True
                            else:
                                log.warning(
                                    f"Модель {self.model_name} не найдена. "
                                    f"Доступные: {model_names}"
                                )
                                return False
                        else:
                            log.error(f"Ollama сервер недоступен: {response.status}")
                            return False
                except Exception as e:
                    log.error(f"Ошибка проверки модели: {e}")
                    return False
        else:
            try:
                async with self.session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        result = await response.json()
                        models = result.get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        
                        if self.model_name in model_names:
                            log.info(f"Модель {self.model_name} доступна")
                            return True
                        else:
                            log.warning(
                                f"Модель {self.model_name} не найдена. "
                                f"Доступные: {model_names}"
                            )
                            return False
                    else:
                        log.error(f"Ollama сервер недоступен: {response.status}")
                        return False
            except Exception as e:
                log.error(f"Ошибка проверки модели: {e}")
                return False

    def _create_rewrite_prompt(self, text: str, title: str = "") -> str:
        """
        Создает промпт для рерайта текста
        
        Args:
            text: Исходный текст
            title: Заголовок
            
        Returns:
            Промпт для генерации
        """
        return f"""Ты - профессиональный копирайтер для социальных сетей. Твоя задача - переписать текст для публикации ВКонтакте.

Исходный заголовок: {title if title else 'Без названия'}

Исходный текст:
{text}

Требования к рерайту:
- Сделай текст уникальным, добавь свой стиль
- Сохрани основной смысл и факты
- Длина текста: от 500 до 1500 символов
- Сделай заголовок цепляющим и интересным
- Пиши в неформальном, дружеском стиле
- Избегай сложных терминов, пиши простым языком
- Добавь 2-4 уместных эмодзи для привлечения внимания
- Добавь призыв к действию в конце (подписаться, поставить лайк, написать комментарий)

Важно: Текст должен быть полностью уникальным, но сохранять точность информации.

Перепиши текст:"""

    def _create_summary_prompt(self, texts: List[str]) -> str:
        """
        Создает промпт для суммаризации текстов
        
        Args:
            texts: Список текстов
            
        Returns:
            Промпт для генерации
        """
        combined = "\n\n".join([f"Источник {i+1}:\n{t[:500]}" for i, t in enumerate(texts)])
        
        return f"""Ты - редактор новостей. Твоя задача - создать краткое саммари из нескольких источников.

Источники:
{combined}

Задание:
1. Проанализируй все источники
2. Выдели ключевые факты и общую информацию
3. Создай единый связный текст на русском языке
4. Укажи, что информация собрана из нескольких источников
5. Длина: 800-1200 символов
6. Стиль: информационный, но доступный

Создай саммари:"""
