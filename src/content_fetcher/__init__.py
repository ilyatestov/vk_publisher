"""
Модуль для сбора контента из всех источников
"""
import json
from typing import List, Dict, Any
from loguru import logger

from .rss_parser import RSSParser
from .web_parser import WebParser
from .vk_scraper import VKScraper


class ContentFetcher:
    """Основной класс для сбора контента из всех источников"""
    
    def __init__(self, vk_api_client=None, proxy: str = None):
        """
        Инициализация сборщика контента
        
        Args:
            vk_api_client: Клиент VK API (для парсинга групп ВК)
            proxy: Прокси для парсинга сайтов
        """
        self.rss_parser = RSSParser()
        self.web_parser = WebParser(proxy=proxy)
        self.vk_scraper = VKScraper(vk_api_client) if vk_api_client else None
    
    def load_sources(self, config_path: str) -> Dict[str, Any]:
        """
        Загрузка конфигурации источников
        
        Args:
            config_path: Путь к файлу конфигурации
            
        Returns:
            Словарь с конфигурацией источников
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Загружена конфигурация источников из {config_path}")
            return config
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации источников: {e}")
            return {'rss': [], 'vk_groups': [], 'websites': []}
    
    async def fetch_all(self, sources_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Сбор контента из всех источников
        
        Args:
            sources_config: Конфигурация источников
            
        Returns:
            Список всех собранных материалов
        """
        all_content = []
        
        # Парсинг RSS лент
        rss_sources = sources_config.get('rss', [])
        for source in rss_sources:
            if source.get('enabled', False):
                content = self.rss_parser.parse_feed(
                    url=source['url'],
                    limit=10
                )
                # Добавляем метаданные источника
                for item in content:
                    item['priority'] = source.get('priority', 3)
                    item['topic'] = source.get('topic', 'general')
                all_content.extend(content)
        
        # Парсинг веб-сайтов
        website_sources = sources_config.get('websites', [])
        for source in website_sources:
            if source.get('enabled', False):
                content = await self.web_parser.parse_website(
                    url=source['url'],
                    selector=source['selector'],
                    limit=10
                )
                # Добавляем метаданные источника
                for item in content:
                    item['priority'] = source.get('priority', 3)
                    item['topic'] = source.get('topic', 'general')
                all_content.extend(content)
        
        # Парсинг групп ВК
        if self.vk_scraper:
            vk_sources = sources_config.get('vk_groups', [])
            for source in vk_sources:
                if source.get('enabled', False):
                    content = self.vk_scraper.fetch_from_group(
                        group_id=source['group_id'],
                        count=10,
                        topic=source.get('topic')
                    )
                    # Добавляем метаданные источника
                    for item in content:
                        item['priority'] = source.get('priority', 3)
                        item['topic'] = source.get('topic', 'general')
                    all_content.extend(content)
        
        logger.info(f"Всего собрано {len(all_content)} материалов из всех источников")
        
        # Сортировка по приоритету и дате
        all_content.sort(key=lambda x: (x.get('priority', 3), x.get('published')), reverse=False)
        
        return all_content
