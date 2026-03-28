"""
Модуль для ИИ-рерайта контента через локальную LLM (Ollama)
"""
import aiohttp
from typing import Optional, List, Dict, Any
from loguru import logger


class AIRewriter:
    """Класс для рерайта текста с помощью ИИ"""
    
    def __init__(self, base_url: str = "http://ollama:11434", model: str = "qwen2.5:1.5b"):
        """
        Инициализация ИИ-рерайтера
        
        Args:
            base_url: URL Ollama сервера
            model: Название модели для рерайта
        """
        self.base_url = base_url
        self.model = model
    
    async def rewrite(self, 
                      content: str, 
                      title: str = "",
                      max_length: int = 1500,
                      min_length: int = 500,
                      add_emojis: bool = True,
                      add_call_to_action: bool = True) -> Optional[str]:
        """
        Рерайт контента через ИИ
        
        Args:
            content: Исходный текст
            title: Заголовок
            max_length: Максимальная длина
            min_length: Минимальная длина
            add_emojis: Добавить эмодзи
            add_call_to_action: Добавить призыв к действию
            
        Returns:
            Уникальный переписанный текст или None при ошибке
        """
        try:
            prompt = self._create_prompt(
                content=content,
                title=title,
                max_length=max_length,
                min_length=min_length,
                add_emojis=add_emojis,
                add_call_to_action=add_call_to_action
            )
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 2000
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        rewritten_text = result.get('response', '').strip()
                        
                        if rewritten_text:
                            logger.success("Текст успешно переписан через ИИ")
                            return rewritten_text
                        else:
                            logger.warning("ИИ вернул пустой результат")
                            return None
                    else:
                        logger.error(f"Ошибка Ollama API: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка при рерайте через ИИ: {e}")
            return None
    
    def _create_prompt(self, 
                       content: str,
                       title: str,
                       max_length: int,
                       min_length: int,
                       add_emojis: bool,
                       add_call_to_action: bool) -> str:
        """
        Создание промпта для ИИ
        
        Returns:
            Промпт для генерации
        """
        emoji_instruction = "- Добавь 2-4 уместных эмодзи для привлечения внимания\n" if add_emojis else ""
        cta_instruction = "- Добавь призыв к действию в конце (подписаться, поставить лайк, написать комментарий)\n" if add_call_to_action else ""
        
        prompt = f"""Ты - профессиональный копирайтер для социальных сетей. Твоя задача - переписать текст для публикации ВКонтакте.

Исходный заголовок: {title if title else 'Без названия'}

Исходный текст:
{content}

Требования к рерайту:
- Сделай текст уникальным, добавь своё мнение и стиль
- Сохрани основной смысл и факты
- Длина текста: от {min_length} до {max_length} символов
- Сделай заголовок цепляющим и интересным
- Пиши в неформальном, дружеском стиле
- Избегай сложных терминов, пиши простым языком
{emoji_instruction}{cta_instruction}
Важно: Текст должен быть полностью уникальным, но сохранять точность информации.

Перепиши текст:"""
        
        return prompt
    
    async def generate_summary(self, articles: List[Dict[str, Any]]) -> Optional[str]:
        """
        Генерация саммари из нескольких статей на одну тему
        
        Args:
            articles: Список статей для объединения
            
        Returns:
            Объединённое саммари
        """
        if not articles:
            return None
        
        # Подготовка текстов статей
        texts = []
        for i, article in enumerate(articles[:5], 1):  # Берём максимум 5 статей
            title = article.get('title', 'Без названия')
            content = article.get('content', '')[:500]  # Первые 500 символов
            texts.append(f"Статья {i}: {title}\n{content}")
        
        combined_texts = "\n\n".join(texts)
        
        prompt = f"""Ты - редактор новостей. Твоя задача - создать краткое саммари из нескольких источников.

Источники:
{combined_texts}

Задание:
1. Проанализируй все источники
2. Выдели ключевые факты и общую информацию
3. Создай единый связный текст на русском языке
4. Укажи, что информация собрана из нескольких источников
5. Длина: 800-1200 символов
6. Стиль: информационный, но доступный

Создай саммари:"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.5,
                            "top_p": 0.9,
                            "max_tokens": 1500
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        logger.error(f"Ошибка при генерации саммари: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при генерации саммари: {e}")
            return None
    
    async def check_model_availability(self) -> bool:
        """
        Проверка доступности модели
        
        Returns:
            True если модель доступна
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        models = result.get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        
                        if self.model in model_names:
                            logger.info(f"Модель {self.model} доступна")
                            return True
                        else:
                            logger.warning(f"Модель {self.model} не найдена. Доступные: {model_names}")
                            return False
                    else:
                        logger.error(f"Ollama сервер недоступен: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка проверки модели: {e}")
            return False
