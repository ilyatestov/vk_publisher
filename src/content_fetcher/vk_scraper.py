"""
Парсер для сбора контента из групп ВКонтакте
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import hashlib


class VKScraper:
    """Скрейпер для сбора контента из групп ВК"""
    
    def __init__(self, vk_api_client):
        """
        Инициализация скрепера
        
        Args:
            vk_api_client: Экземпляр клиента VK API
        """
        self.vk = vk_api_client
    
    def fetch_from_group(self, 
                         group_id: int, 
                         count: int = 10,
                         topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получение постов из группы ВК
        
        Args:
            group_id: ID группы
            count: Количество постов
            topic: Тема для фильтрации (опционально)
            
        Returns:
            Список постов
        """
        try:
            logger.info(f"Получение постов из группы {group_id}")
            
            # Получение постов со стены группы
            posts = self.vk.vk.wall.get(
                owner_id=-group_id,  # Отрицательный ID для групп
                count=count,
                filter='owner'  # Только посты от владельца группы
            )
            
            items = []
            for post in posts.get('items', []):
                parsed_post = self._parse_post(post, group_id, topic)
                if parsed_post:
                    items.append(parsed_post)
            
            logger.success(f"Извлечено {len(items)} постов из группы {group_id}")
            return items
            
        except Exception as e:
            logger.error(f"Ошибка при получении постов из группы {group_id}: {e}")
            return []
    
    def _parse_post(self, 
                    post: Dict[str, Any], 
                    group_id: int,
                    topic: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Разбор поста ВК
        
        Args:
            post: Данные поста от API
            group_id: ID группы
            topic: Тема для фильтрации
            
        Returns:
            Словарь с данными поста или None
        """
        try:
            # Пропуск репостов
            if 'copy_history' in post:
                return None
            
            # Извлечение текста
            text = post.get('text', '')
            
            # Фильтрация по теме (если указана)
            if topic and topic.lower() not in text.lower():
                return None
            
            # Извлечение вложений
            attachments = post.get('attachments', [])
            image_url = self._extract_image(attachments)
            
            # Создание хеша
            content_hash = self._create_hash(text[:100], text)
            
            # Дата публикации
            published = datetime.fromtimestamp(post.get('date', 0))
            
            return {
                'title': text[:100] + '...' if len(text) > 100 else text,
                'content': text,
                'link': f"https://vk.com/wall-{group_id}_{post.get('id')}",
                'published': published,
                'source': f'vk_group_{group_id}',
                'image_url': image_url,
                'content_hash': content_hash,
                'type': 'vk_group',
                'post_id': post.get('id'),
                'likes': post.get('likes', {}).get('count', 0),
                'comments': post.get('comments', {}).get('count', 0),
                'shares': post.get('reposts', {}).get('count', 0)
            }
            
        except Exception as e:
            logger.error(f"Ошибка при разборе поста ВК: {e}")
            return None
    
    def _extract_image(self, attachments: List[Dict[str, Any]]) -> Optional[str]:
        """Извлечение URL изображения из вложений"""
        for attachment in attachments:
            att_type = attachment.get('type')
            
            if att_type == 'photo':
                photo = attachment.get('photo', {})
                # Возвращаем фото наилучшего качества
                for size_key in ['w', 'z', 'y', 'x', 'l', 'm']:
                    if size_key in photo:
                        return photo[size_key]
            
            elif att_type == 'doc' and attachment.get('doc', {}).get('type') == 'image':
                doc = attachment.get('doc', {})
                return doc.get('url')
        
        return None
    
    def _create_hash(self, title: str, content: str) -> str:
        """Создание хеша для проверки дубликатов"""
        content_preview = content[:500] if len(content) > 500 else content
        hash_string = f"{title}:{content_preview}"
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
