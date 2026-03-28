"""
Публикация постов ВКонтакте
"""
from typing import Dict, Any, Optional, List
from loguru import logger


class VKPublisher:
    """Класс для публикации постов в ВКонтакте"""
    
    def __init__(self, vk_api_client, database):
        """
        Инициализация публикатора
        
        Args:
            vk_api_client: Клиент VK API
            database: Экземпляр базы данных
        """
        self.vk = vk_api_client
        self.db = database
    
    async def publish_post(self, 
                           post_data: Dict[str, Any],
                           enable_preview: bool = True) -> Optional[int]:
        """
        Публикация поста
        
        Args:
            post_data: Данные поста (текст, изображения и т.д.)
            enable_preview: Включить превью перед публикацией
            
        Returns:
            ID опубликованного поста или None при ошибке
        """
        try:
            text = post_data.get('text', '')
            image_url = post_data.get('image_url')
            sources = post_data.get('sources', [])
            content_hash = post_data.get('content_hash', '')
            
            if not text:
                logger.error("Пустой текст поста")
                await self.db.add_log(
                    action='publish',
                    source=post_data.get('source', 'unknown'),
                    post_id=None,
                    hash=content_hash,
                    status='failed',
                    error='Пустой текст поста'
                )
                return None
            
            # Если включено превью - отправляем на модерацию
            if enable_preview:
                from ..telegram_bot.bot import TelegramModerator
                moderator = TelegramModerator(None)  # Будет инициализирован позже
                
                approved = await moderator.send_for_preview(post_data)
                
                if not approved:
                    logger.info("Пост отклонён на модерации")
                    await self.db.add_log(
                        action='publish',
                        source=post_data.get('source', 'unknown'),
                        post_id=None,
                        hash=content_hash,
                        status='skipped',
                        error='Отклонено на модерации'
                    )
                    return None
            
            # Загрузка изображения (если есть)
            attachments = []
            if image_url:
                # TODO: Реализовать загрузку изображения по URL
                logger.info(f"Изображение будет загружено: {image_url}")
            
            # Публикация поста
            response = self.vk.post_to_wall(
                message=text,
                attachments=attachments if attachments else None
            )
            
            vk_post_id = response.get('post_id')
            
            if vk_post_id:
                # Сохранение в базу
                await self.db.add_published_post(
                    vk_post_id=vk_post_id,
                    content_hash=content_hash,
                    text=text[:1000],  # Первые 1000 символов
                    sources=[s.get('url', '') for s in sources]
                )
                
                # Логирование успеха
                await self.db.add_log(
                    action='publish',
                    source=post_data.get('source', 'unknown'),
                    post_id=vk_post_id,
                    hash=content_hash,
                    status='success',
                    error=None
                )
                
                logger.success(f"Пост успешно опубликован: VK ID {vk_post_id}")
                return vk_post_id
            else:
                logger.error("Не удалось получить ID поста из ответа VK")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при публикации поста: {e}")
            
            await self.db.add_log(
                action='publish',
                source=post_data.get('source', 'unknown'),
                post_id=None,
                hash=post_data.get('content_hash', ''),
                status='failed',
                error=str(e)
            )
            
            return None
    
    async def schedule_post(self,
                            post_data: Dict[str, Any],
                            publish_time: int) -> Optional[int]:
        """
        Отложенная публикация поста
        
        Args:
            post_data: Данные поста
            publish_time: Unix timestamp времени публикации
            
        Returns:
            ID запланированного поста или None
        """
        try:
            text = post_data.get('text', '')
            
            response = self.vk.post_to_wall(
                message=text,
                publish_date=publish_time
            )
            
            vk_post_id = response.get('post_id')
            
            if vk_post_id:
                logger.success(f"Пост запланирован на {publish_time}: VK ID {vk_post_id}")
                return vk_post_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при планировании поста: {e}")
            return None
