"""
Асинхронный клиент VK API с retry-логикой, rate-limit и proxy-ротацией
"""
import asyncio
import aiohttp
import random
from typing import List, Optional, Dict, Any
from datetime import datetime
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from ..core.logging import log
from ..core.config import settings
from ..core.exceptions import (
    VKAPIError,
    VKAuthError,
    VKRateLimitError,
    VKPermissionError,
    VKCaptchaError
)
from ..domain.entities import SocialPost, VKAccount, PostStatus
from ..domain.interfaces import SocialPublisherInterface


class VKClient(SocialPublisherInterface):
    """
    Асинхронный клиент для работы с VK API
    
    Поддерживает:
    - Retry-логику с экспоненциальной задержкой
    - Rate limiting
    - Proxy-ротацию
    - Загрузку медиафайлов
    - Отложенную публикацию
    """

    def __init__(self):
        self.base_url = "https://api.vk.com/method/"
        self.api_version = settings.vk.api_version
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_proxy_index = 0
        self._rate_limit_lock = asyncio.Lock()
        self._last_request_time: float = 0

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _create_session(self):
        """Создает HTTP-сессию с настройками"""
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        log.info("VK API сессия создана")

    def _get_current_proxy(self) -> Optional[str]:
        """Получает текущий прокси из списка"""
        if not settings.vk.proxy_list:
            return None
        return settings.vk.proxy_list[self.current_proxy_index % len(settings.vk.proxy_list)]

    def _rotate_proxy(self):
        """Переключает на следующий прокси"""
        if settings.vk.proxy_list:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(settings.vk.proxy_list)
            log.info(f"Прокси переключен на индекс {self.current_proxy_index}")

    async def _apply_rate_limit(self):
        """Применяет rate limiting к запросам"""
        async with self._rate_limit_lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request_time
            min_interval = 1.0 / settings.vk.rate_limit_per_second
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            
            self._last_request_time = asyncio.get_event_loop().time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((VKAPIError, aiohttp.ClientError)),
        reraise=True
    )
    async def _make_request(
        self,
        method: str,
        params: Dict[str, Any],
        account: VKAccount
    ) -> Dict[str, Any]:
        """
        Выполняет запрос к VK API с retry-логикой
        
        Args:
            method: Метод API (например, 'wall.post')
            params: Параметры запроса
            account: Аккаунт для выполнения запроса
            
        Returns:
            Ответ от API
            
        Raises:
            VKAPIError: При ошибке API
            VKAuthError: При ошибке аутентификации
            VKRateLimitError: При превышении лимита
        """
        await self._apply_rate_limit()

        if not self.session:
            await self._create_session()

        params.update({
            'v': self.api_version,
            'access_token': account.access_token
        })

        proxy = self._get_current_proxy()
        proxy_str = f" (proxy: {proxy})" if proxy else ""
        
        try:
            async with self.session.post(
                f"{self.base_url}{method}",
                data=params,
                proxy=proxy
            ) as response:
                result = await response.json()

                if 'error' in result:
                    error_data = result['error']
                    error_code = error_data.get('error_code')
                    error_msg = error_data.get('error_msg', 'Unknown error')

                    log.warning(f"VK API error{proxy_str}: код {error_code} - {error_msg}")

                    # Обработка специфичных ошибок VK
                    if error_code == 5:
                        raise VKAuthError(error_msg)
                    elif error_code == 6:
                        raise VKRateLimitError(error_msg)
                    elif error_code == 9:
                        raise VKPermissionError(error_msg)
                    elif error_code == 14:
                        captcha_sid = error_data.get('captcha_sid')
                        captcha_img = error_data.get('captcha_img')
                        raise VKCaptchaError(
                            error_msg,
                            captcha_sid=captcha_sid,
                            captcha_img=captcha_img
                        )
                    else:
                        raise VKAPIError(error_msg, error_code=error_code)

                return result.get('response', {})

        except aiohttp.ClientError as e:
            log.error(f"Network error{proxy_str}: {e}")
            self._rotate_proxy()  # Переключаем прокси при сетевой ошибке
            raise
        except RetryError as e:
            log.error(f"Все попытки запроса исчерпаны: {e}")
            raise

    async def publish_post(self, post: SocialPost, account: VKAccount) -> bool:
        """
        Публикует пост в группе ВКонтакте
        
        Args:
            post: Пост для публикации
            account: Аккаунт для публикации
            
        Returns:
            True если публикация успешна
        """
        try:
            attachments = []

            # Загружаем изображения
            if post.image_urls:
                uploaded_photos = await self.upload_media(post.image_urls, account)
                attachments.extend(uploaded_photos)

            # Подготовка параметров для публикации
            message_parts = []
            
            if post.title:
                message_parts.append(f"<b>{post.title}</b>")
            
            message_parts.append(post.content)

            # Добавляем хэштеги
            if post.tags:
                hashtag_str = " ".join(f"#{tag}" for tag in post.tags)
                message_parts.append(f"\n\n{hashtag_str}")

            full_message = "\n\n".join(message_parts)

            params = {
                'owner_id': f"-{abs(account.id)}",  # Отрицательное значение для групп
                'message': full_message,
                'attachments': ','.join(attachments) if attachments else '',
                'from_group': 1
            }

            # Если есть запланированное время
            if post.scheduled_at and post.scheduled_at > datetime.utcnow():
                params['publish_date'] = int(post.scheduled_at.timestamp())

            result = await self._make_request('wall.post', params, account)

            post_id = result.get('post_id')
            log.success(f"Пост успешно опубликован. ID: {post_id}")
            
            # Обновляем метаданные поста
            post.metadata['vk_post_id'] = post_id
            post.metadata['published_at'] = datetime.utcnow().isoformat()

            return True

        except VKAPIError as e:
            log.error(f"Ошибка публикации поста в VK: {e}")
            post.metadata['error'] = str(e)
            return False
        except Exception as e:
            log.error(f"Неожиданная ошибка при публикации поста: {e}")
            post.metadata['error'] = str(e)
            return False

    async def upload_media(
        self,
        media_urls: List[str],
        account: VKAccount
    ) -> List[str]:
        """
        Загружает медиафайлы и возвращает ссылки для вставки
        
        Args:
            media_urls: Список URL медиафайлов
            account: Аккаунт для загрузки
            
        Returns:
            Список идентификаторов загруженных медиа
        """
        uploaded_attachments = []

        for media_url in media_urls:
            try:
                # Получаем сервер для загрузки фотографии
                server_response = await self._make_request(
                    'photos.getWallUploadServer',
                    {'group_id': abs(account.id)},
                    account
                )

                upload_url = server_response.get('upload_url')
                if not upload_url:
                    log.error("Не получен upload_url от VK API")
                    continue

                # Скачиваем файл по URL
                async with self.session.get(media_url) as img_response:
                    if img_response.status != 200:
                        log.error(f"Не удалось скачать изображение: {media_url}")
                        continue
                    img_data = await img_response.read()

                # Загружаем на сервер VK
                form_data = aiohttp.FormData()
                form_data.add_field('photo', img_data, filename='image.jpg')

                async with self.session.post(upload_url, data=form_data) as upload_resp:
                    if upload_resp.status != 200:
                        log.error(f"Ошибка загрузки на VK: {upload_resp.status}")
                        continue
                    upload_result = await upload_resp.json()

                # Сохраняем фотографию
                save_params = {
                    'group_id': abs(account.id),
                    'server': upload_result.get('server'),
                    'photo': upload_result.get('photo'),
                    'hash': upload_result.get('hash')
                }

                saved_photo = await self._make_request(
                    'photos.saveWallPhoto',
                    save_params,
                    account
                )

                if saved_photo:
                    photo = saved_photo[0]
                    attachment_str = f"photo{photo['owner_id']}_{photo['id']}"
                    uploaded_attachments.append(attachment_str)
                    log.info(f"Фото загружено: {attachment_str}")

            except Exception as e:
                log.error(f"Ошибка загрузки медиа {media_url}: {e}")
                continue

        return uploaded_attachments

    async def get_rate_limit_info(self, account: VKAccount) -> Dict[str, Any]:
        """
        Возвращает информацию о текущих лимитах
        
        Args:
            account: Аккаунт для проверки
            
        Returns:
            Информация о лимитах
        """
        return {
            'current_requests': 0,  # Будет отслеживаться в middleware
            'max_requests_per_second': settings.vk.rate_limit_per_second,
            'daily_quota_remaining': account.daily_quota - account.posts_today,
            'proxy_count': len(settings.vk.proxy_list),
            'current_proxy_index': self.current_proxy_index
        }

    async def schedule_post(
        self,
        post: SocialPost,
        account: VKAccount,
        publish_at: datetime
    ) -> Optional[int]:
        """
        Планирует публикацию поста на указанное время
        
        Args:
            post: Пост для публикации
            account: Аккаунт для публикации
            publish_at: Время публикации
            
        Returns:
            ID запланированного поста или None при ошибке
        """
        post.scheduled_at = publish_at
        success = await self.publish_post(post, account)
        
        if success:
            return post.metadata.get('vk_post_id')
        return None
