"""
RSS парсер для сбора контента из лент
"""
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import hashlib

from ..utils.url_safety import is_safe_public_url


class RSSParser:
    """Парсер RSS лент"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def parse_feed(self, url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Парсинг RSS ленты
        
        Args:
            url: URL RSS ленты
            limit: Максимальное количество записей
            
        Returns:
            Список распарсенных записей
        """
        try:
            logger.info(f"Парсинг RSS ленты: {url}")

            if not is_safe_public_url(url):
                logger.warning(f"Небезопасный URL RSS отклонён (SSRF guard): {url}")
                return []
            
            feed = feedparser.parse(url)
            
            if feed.bozo:
                logger.warning(f"RSS лента {url} содержит ошибки парсинга")
            
            entries = []
            for entry in feed.entries[:limit]:
                parsed_entry = self._parse_entry(entry, url)
                if parsed_entry:
                    entries.append(parsed_entry)
            
            logger.success(f"Извлечено {len(entries)} записей из {url}")
            return entries
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге RSS {url}: {e}")
            return []
    
    def _parse_entry(self, entry: feedparser.FeedParserDict, source_url: str) -> Optional[Dict[str, Any]]:
        """
        Разбор отдельной записи RSS
        
        Args:
            entry: Запись из feedparser
            source_url: URL источника
            
        Returns:
            Словарь с данными записи или None
        """
        try:
            # Извлечение текста
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            
            # Очистка HTML тегов
            content = self._clean_html(content)
            
            # Извлечение изображения
            image_url = self._extract_image(entry)
            
            # Создание хеша для проверки дубликатов
            content_hash = self._create_hash(entry.title, content)
            
            return {
                'title': entry.title if hasattr(entry, 'title') else 'Без названия',
                'content': content,
                'link': entry.link if hasattr(entry, 'link') else source_url,
                'published': self._parse_date(entry),
                'source': source_url,
                'image_url': image_url,
                'content_hash': content_hash,
                'type': 'rss'
            }
            
        except Exception as e:
            logger.error(f"Ошибка при разборе записи RSS: {e}")
            return None
    
    def _clean_html(self, text: str) -> str:
        """Очистка текста от HTML тегов"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, 'lxml')
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_image(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Извлечение URL изображения из записи"""
        # Проверка media:content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('medium') == 'image' or media.get('type', '').startswith('image'):
                    return media.get('url')
        
        # Проверка enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image'):
                    return enclosure.get('href') or enclosure.get('url')
        
        # Проверка summary/content на наличие img тегов
        content_fields = ['content', 'summary', 'description']
        for field in content_fields:
            if hasattr(entry, field) and getattr(entry, field):
                soup = BeautifulSoup(getattr(entry, field)[0] if isinstance(getattr(entry, field), list) 
                                    else getattr(entry, field), 'lxml')
                img = soup.find('img')
                if img and img.get('src'):
                    return img['src']
        
        return None
    
    def _parse_date(self, entry: feedparser.FeedParserDict) -> datetime:
        """Парсинг даты публикации"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        else:
            return datetime.now()
    
    def _create_hash(self, title: str, content: str) -> str:
        """Создание хеша для проверки дубликатов"""
        content_preview = content[:500] if len(content) > 500 else content
        hash_string = f"{title}:{content_preview}"
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
