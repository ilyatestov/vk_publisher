"""
Модуль для проверки дубликатов и объединения контента
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict
from loguru import logger


class Deduplicator:
    """Класс для проверки дубликатов и группировки контента"""
    
    def __init__(self, database):
        """
        Инициализация дедупликатора
        
        Args:
            database: Экземпляр базы данных
        """
        self.db = database
    
    async def filter_duplicates(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрация дубликатов из списка контента
        
        Args:
            content_list: Список материалов
            
        Returns:
            Список без дубликатов
        """
        if not content_list:
            logger.info("Пустой список материалов, дедупликация не требуется")
            return []

        unique_content: List[Dict[str, Any]] = []
        duplicates_count = 0
        seen_hashes: set[str] = set()
        db_duplicate_cache: Dict[str, bool] = {}

        for item in content_list:
            content_hash = item.get('content_hash')

            if not content_hash:
                logger.warning("У материала нет хеша, пропускаем")
                continue

            
            if content_hash in seen_hashes:
                duplicates_count += 1
                logger.debug(f"Найден дубликат: {item.get('title', 'Без названия')[:50]}...")
                continue

            # Проверка на дубликат в базе (кэшируем результат для одинаковых хэшей)
            if content_hash not in db_duplicate_cache:
                db_duplicate_cache[content_hash] = await self.db.check_duplicate(content_hash, days=30)

            if db_duplicate_cache[content_hash]:
                duplicates_count += 1
                logger.debug(f"Найден дубликат: {item.get('title', 'Без названия')[:50]}...")
                continue

            seen_hashes.add(content_hash)
            unique_content.append(item)
        
        logger.info(f"Отфильтровано {duplicates_count} дубликатов из {len(content_list)} материалов")
        return unique_content
    
    def group_similar_articles(self, 
                               content_list: List[Dict[str, Any]], 
                               similarity_threshold: float = 0.8) -> Dict[str, List[Dict[str, Any]]]:
        """
        Группировка похожих статей по темам
        
        Args:
            content_list: Список материалов
            similarity_threshold: Порог схожести (не используется в базовой версии)
            
        Returns:
            Словарь с группами статей по темам
        """
        # Группировка по topic
        grouped = defaultdict(list)
        
        for item in content_list:
            topic = item.get('topic', 'general')
            grouped[topic].append(item)
        
        # Логирование
        for topic, items in grouped.items():
            if len(items) > 1:
                logger.info(f"Тема '{topic}': {len(items)} статей для возможного объединения")
        
        return dict(grouped)
    
    async def merge_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Объединение нескольких статей на одну тему в один пост
        
        Args:
            articles: Список статей для объединения
            
        Returns:
            Объединённый материал
        """
        if not articles:
            return {}
        
        if len(articles) == 1:
            # Если статья одна, просто возвращаем её
            return articles[0]
        
        logger.info(f"Объединение {len(articles)} статей в один пост")
        
        # Сбор всех источников
        sources = [
            {
                'title': article.get('title', 'Без названия'),
                'url': article.get('link', ''),
                'source': article.get('source', '')
            }
            for article in articles
        ]
        
        # Выбор лучшего изображения
        best_image = self._select_best_media(articles)
        
        # Создание заголовка
        merged_title = self._generate_merged_title(articles)
        
        # Объединённый контент (будет переписан через ИИ)
        merged_content = {
            'title': merged_title,
            'articles': articles,
            'sources': sources,
            'image_url': best_image,
            'type': 'merged',
            'needs_rewrite': True
        }
        
        return merged_content
    
    def _select_best_media(self, articles: List[Dict[str, Any]]) -> Optional[str]:
        """Выбор лучшего изображения из статей"""
        for article in articles:
            if article.get('image_url'):
                return article['image_url']
        return None
    
    def _generate_merged_title(self, articles: List[Dict[str, Any]]) -> str:
        """Генерация заголовка для объединённого поста"""
        if not articles:
            return "Обзор новостей"
        
        # Берём тему из первой статьи
        topic = articles[0].get('topic', 'новости')
        
        # Создаём обобщающий заголовок
        titles = [a.get('title', '')[:50] for a in articles[:3]]
        
        if len(articles) > 1:
            return f"Обзор по теме: {topic} ({len(articles)} источников)"
        else:
            return titles[0] if titles else "Новость"
