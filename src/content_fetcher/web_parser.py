"""
Парсер веб-сайтов для сбора контента
"""
import aiohttp
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
import hashlib

from ..utils.url_safety import is_safe_public_url


class WebParser:
    """Парсер веб-сайтов"""
    
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
    
    async def parse_website(self, 
                           url: str, 
                           selector: str,
                           content_selector: Optional[str] = None,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Парсинг веб-сайта
        
        Args:
            url: URL сайта
            selector: CSS селектор для заголовков статей
            content_selector: CSS селектор для содержимого (опционально)
            limit: Максимальное количество статей
            
        Returns:
            Список распарсенных статей
        """
        try:
            logger.info(f"Парсинг веб-сайта: {url}")

            if not is_safe_public_url(url):
                logger.warning(f"Небезопасный URL отклонён (SSRF guard): {url}")
                return []
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, proxy=self.proxy) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка при запросе {url}: {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    articles = []
                    
                    # Поиск элементов по селектору
                    elements = soup.select(selector)[:limit]
                    
                    for element in elements:
                        article = self._parse_element(element, url, content_selector)
                        if article:
                            articles.append(article)
                    
                    logger.success(f"Извлечено {len(articles)} статей из {url}")
                    return articles
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге сайта {url}: {e}")
            return []
    
    def _parse_element(self, 
                       element: BeautifulSoup.element, 
                       source_url: str,
                       content_selector: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Разбор отдельного элемента статьи
        
        Args:
            element: BeautifulSoup элемент
            source_url: URL источника
            content_selector: Селектор для содержимого
            
        Returns:
            Словарь с данными статьи или None
        """
        try:
            # Извлечение заголовка
            title_elem = element.find(['h1', 'h2', 'h3', 'a'], class_=True) or element.find('a')
            title = title_elem.get_text(strip=True) if title_elem else 'Без названия'
            
            # Извлечение ссылки
            link_elem = element.find('a')
            link = link_elem.get('href') if link_elem else source_url
            
            # Абсолютизация ссылки
            if link and not link.startswith('http'):
                from urllib.parse import urljoin
                link = urljoin(source_url, link)
            
            # Извлечение содержимого (если указан селектор)
            content = ''
            if content_selector:
                content_elem = element.select_one(content_selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
            
            # Извлечение изображения
            image_url = self._extract_image(element, source_url)
            
            # Создание хеша
            content_hash = self._create_hash(title, content)
            
            return {
                'title': title,
                'content': content,
                'link': link or source_url,
                'published': datetime.now(),
                'source': source_url,
                'image_url': image_url,
                'content_hash': content_hash,
                'type': 'website'
            }
            
        except Exception as e:
            logger.error(f"Ошибка при разборе элемента: {e}")
            return None
    
    def _extract_image(self, element: BeautifulSoup.element, source_url: str) -> Optional[str]:
        """Извлечение URL изображения"""
        img = element.find('img')
        if img and img.get('src'):
            src = img['src']
            if not src.startswith('http'):
                from urllib.parse import urljoin
                src = urljoin(source_url, src)
            return src
        return None
    
    def _create_hash(self, title: str, content: str) -> str:
        """Создание хеша для проверки дубликатов"""
        content_preview = content[:500] if len(content) > 500 else content
        hash_string = f"{title}:{content_preview}"
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
