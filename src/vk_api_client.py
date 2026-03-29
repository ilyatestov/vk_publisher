"""
Клиент для работы с VK API
"""
import asyncio
import time
from functools import wraps
from typing import Optional, Dict, Any, List
import vk_api
from vk_api.exceptions import ApiError, AuthError
import requests.exceptions
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
    before_log,
    after_log
)
from loguru import logger


def rate_limit(calls_per_second: float = 2.5):
    """
    Декоратор для ограничения частоты вызовов API
    VK API лимит: ~3 запроса в секунду, используем с запасом
    """
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                await asyncio.sleep(left_to_wait)
            last_called[0] = time.time()
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        # Возвращаем нужный wrapper в зависимости от типа функции
        if asyncio.iscoroutinefunction(func):
            return wrapper
        else:
            return sync_wrapper
    
    return decorator


class VKAPIClient:
    """Клиент для работы с VK API"""
    
    @staticmethod
    def _extract_group_info_from_payload(payload: Any) -> Dict[str, Any]:
        """Извлекает данные группы из разных форматов ответа VK API."""
        response = payload
        if isinstance(response, dict) and 'response' in response:
            response = response.get('response')

        if isinstance(response, dict) and 'groups' in response:
            groups = response.get('groups') or []
            return groups[0] if groups else {}

        if isinstance(response, list):
            return response[0] if response else {}

        return {}

    def __init__(self, access_token: str, group_id: str, api_version: str = "5.131"):
        """
        Инициализация клиента VK API
        
        Args:
            access_token: Токен доступа сообщества
            group_id: ID группы для публикации
            api_version: Версия API
        """
        self.access_token = access_token
        self.group_id = group_id
        self.api_version = api_version
        
        # Инициализация vk_session
        self.vk_session = vk_api.VkApi(token=access_token, api_version=api_version)
        self.vk = self.vk_session.get_api()
        
        logger.info(f"VK API клиент инициализирован для группы {group_id}")
    
    @rate_limit(calls_per_second=2.5)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((ApiError, requests.exceptions.RequestException, ConnectionError)),
        before=before_log(logger, 'DEBUG'),
        after=after_log(logger, 'DEBUG')
    )
    def post_to_wall(self, 
                     message: str, 
                     attachments: Optional[List[str]] = None,
                     signed: bool = False,
                     publish_date: Optional[int] = None) -> Dict[str, Any]:
        """
        Публикация поста на стене группы
        
        Args:
            message: Текст поста
            attachments: Список вложений (фото, видео, ссылки)
            signed: Подписывать пост от имени администратора
            publish_date: Время публикации (Unix timestamp)
            
        Returns:
            Ответ от API с данными поста
        """
        try:
            params = {
                'owner_id': f'-{self.group_id}',  # Отрицательный ID для групп
                'message': message,
                'from_group': 1
            }
            
            if attachments:
                params['attachments'] = ','.join(attachments)
            
            if signed:
                params['signed'] = 1
            
            if publish_date:
                params['publish_date'] = publish_date
            
            response = self.vk.wall.post(**params)
            
            logger.success(f"Пост успешно опубликован. Post ID: {response.get('post_id')}")
            return response
            
        except vk_api.exceptions.ApiError as e:
            logger.error(f"Ошибка VK API при публикации: {e}")
            raise
        except Exception as e:
            logger.error(f"Неизвестная ошибка при публикации: {e}")
            raise
    
    @rate_limit(calls_per_second=2.5)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((ApiError, requests.exceptions.RequestException, ConnectionError)),
        before=before_log(logger, 'DEBUG'),
        after=after_log(logger, 'DEBUG')
    )
    def upload_photo(self, photo_path: str) -> str:
        """
        Загрузка фотографии для последующей публикации
        
        Args:
            photo_path: Путь к файлу фотографии
            
        Returns:
            Строка вложения для использования в wall.post
        """
        try:
            upload = vk_api.upload.VkUpload(self.vk_session)
            
            # Загрузка фото на стену группы
            photo = upload.photo_to_group_wall(
                group_id=self.group_id,
                photo_source=photo_path
            )
            
            attachment_string = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
            logger.info(f"Фото загружено: {attachment_string}")
            
            return attachment_string
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке фото: {e}")
            raise
    
    @rate_limit(calls_per_second=2.5)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((ApiError, requests.exceptions.RequestException, ConnectionError)),
        before=before_log(logger, 'DEBUG'),
        after=after_log(logger, 'DEBUG')
    )
    def search_newsfeed(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск контента через newsfeed.search
        
        Args:
            query: Поисковый запрос
            count: Количество результатов
            
        Returns:
            Список найденных постов
        """
        try:
            response = self.vk.newsfeed.search(
                q=query,
                count=count,
                start_time=int(time.time()) - 86400  # За последние 24 часа
            )
            
            items = response.get('items', [])
            logger.info(f"Найдено {len(items)} постов по запросу '{query}'")
            
            return items
            
        except vk_api.exceptions.ApiError as e:
            logger.error(f"Ошибка VK API при поиске: {e}")
            return []
        except Exception as e:
            logger.error(f"Неизвестная ошибка при поиске: {e}")
            return []
    
    def get_group_info(self) -> Dict[str, Any]:
        """
        Получение информации о группе
        
        Returns:
            Информация о группе
        """
        try:
            response = self.vk.groups.getById(group_id=self.group_id)


            logger.warning(f"Неожиданный формат ответа groups.getById: {type(response)}")
            return {}
        except Exception as e:
            logger.error(f"Ошибка при получении информации о группе: {e}")
            return {}
