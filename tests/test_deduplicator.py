"""
Тесты для модуля дедупликации
"""
import pytest
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processor.deduplicator import Deduplicator


class MockDatabase:
    """Мокированный класс базы данных для тестов"""
    
    def __init__(self):
        self.hashes = set()
        self.check_duplicate_calls = 0
    
    async def check_duplicate(self, content_hash, days=30):
        self.check_duplicate_calls += 1
        return content_hash in self.hashes
    
    async def add_content_hash(self, content_hash, title, source, post_id=None):
        self.hashes.add(content_hash)
        return True


@pytest.fixture
def mock_db():
    return MockDatabase()


@pytest.fixture
def deduplicator(mock_db):
    return Deduplicator(database=mock_db)


class TestDeduplicator:
    """Тесты для класса Deduplicator"""
    
    @pytest.mark.asyncio
    async def test_filter_duplicates_no_duplicates(self, deduplicator):
        """Тест фильтрации - дубликатов нет"""
        content_list = [
            {'content_hash': 'hash1', 'title': 'Article 1'},
            {'content_hash': 'hash2', 'title': 'Article 2'},
            {'content_hash': 'hash3', 'title': 'Article 3'}
        ]
        
        result = await deduplicator.filter_duplicates(content_list)
        
        assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_filter_duplicates_with_duplicates(self, deduplicator, mock_db):
        """Тест фильтрации - есть дубликаты"""
        # Добавляем хеш в базу как существующий
        mock_db.hashes.add('hash2')
        
        content_list = [
            {'content_hash': 'hash1', 'title': 'Article 1'},
            {'content_hash': 'hash2', 'title': 'Article 2'},
            {'content_hash': 'hash3', 'title': 'Article 3'}
        ]
        
        result = await deduplicator.filter_duplicates(content_list)
        
        assert len(result) == 2
        assert result[0]['content_hash'] == 'hash1'
        assert result[1]['content_hash'] == 'hash3'

    @pytest.mark.asyncio
    async def test_filter_duplicates_within_same_batch(self, deduplicator):
        """Тест фильтрации дубликатов в пределах одного входного батча"""
        content_list = [
            {'content_hash': 'hash1', 'title': 'Article 1'},
            {'content_hash': 'hash1', 'title': 'Article 1 duplicate in batch'},
            {'content_hash': 'hash2', 'title': 'Article 2'}
        ]

        result = await deduplicator.filter_duplicates(content_list)

        assert len(result) == 2
        assert result[0]['content_hash'] == 'hash1'
        assert result[1]['content_hash'] == 'hash2'

    
    @pytest.mark.asyncio
    async def test_filter_duplicates_no_hash(self, deduplicator):
        """Тест фильтрации - нет хеша"""
        content_list = [
            {'content_hash': 'hash1', 'title': 'Article 1'},
            {'title': 'Article without hash'},
            {'content_hash': 'hash3', 'title': 'Article 3'}
        ]
        
        result = await deduplicator.filter_duplicates(content_list)
        
        assert len(result) == 2
    
    def test_group_similar_articles(self, deduplicator):
        """Тест группировки статей по темам"""
        content_list = [
            {'topic': 'technology', 'title': 'Tech News 1'},
            {'topic': 'technology', 'title': 'Tech News 2'},
            {'topic': 'sports', 'title': 'Sports News 1'},
            {'topic': 'general', 'title': 'General News 1'}
        ]
        
        grouped = deduplicator.group_similar_articles(content_list)
        
        assert len(grouped) == 3
        assert len(grouped['technology']) == 2
        assert len(grouped['sports']) == 1
        assert len(grouped['general']) == 1
    
    def test_group_similar_articles_empty(self, deduplicator):
        """Тест группировки - пустой список"""
        content_list = []
        
        grouped = deduplicator.group_similar_articles(content_list)
        
        assert grouped == {}
    
    @pytest.mark.asyncio
    async def test_merge_articles_single(self, deduplicator):
        """Тест объединения - одна статья"""
        articles = [
            {'title': 'Single Article', 'link': 'https://example.com', 'source': 'rss'}
        ]
        
        result = await deduplicator.merge_articles(articles)
        
        assert result['title'] == 'Single Article'
    
    @pytest.mark.asyncio
    async def test_merge_articles_multiple(self, deduplicator):
        """Тест объединения - несколько статей"""
        articles = [
            {'title': 'Article 1', 'link': 'https://example.com/1', 'source': 'rss', 'topic': 'tech'},
            {'title': 'Article 2', 'link': 'https://example.com/2', 'source': 'vk', 'topic': 'tech'}
        ]
        
        result = await deduplicator.merge_articles(articles)
        
        assert result['type'] == 'merged'
        assert result['needs_rewrite'] is True
        assert len(result['sources']) == 2
        assert len(result['articles']) == 2
    
    @pytest.mark.asyncio
    async def test_merge_articles_empty(self, deduplicator):
        """Тест объединения - пустой список"""
        articles = []
        
        result = await deduplicator.merge_articles(articles)
        
        assert result == {}
    
    def test_select_best_media_with_image(self, deduplicator):
        """Тест выбора изображения - изображение есть"""
        articles = [
            {'title': 'Article 1', 'image_url': None},
            {'title': 'Article 2', 'image_url': 'https://example.com/image.jpg'},
            {'title': 'Article 3', 'image_url': 'https://example.com/image2.jpg'}
        ]
        
        result = deduplicator._select_best_media(articles)
        
        assert result == 'https://example.com/image.jpg'
    
    def test_select_best_media_no_image(self, deduplicator):
        """Тест выбора изображения - изображений нет"""
        articles = [
            {'title': 'Article 1', 'image_url': None},
            {'title': 'Article 2', 'image_url': None}
        ]
        
        result = deduplicator._select_best_media(articles)
        
        assert result is None
    
    def test_generate_merged_title_multiple(self, deduplicator):
        """Тест генерации заголовка - несколько статей"""
        articles = [
            {'title': 'Article 1', 'topic': 'technology'},
            {'title': 'Article 2', 'topic': 'technology'}
        ]
        
        result = deduplicator._generate_merged_title(articles)
        
        assert 'Обзор по теме' in result
        assert '2 источников' in result
    
    def test_generate_merged_title_empty(self, deduplicator):
        """Тест генерации заголовка - пустой список"""
        articles = []
        
        result = deduplicator._generate_merged_title(articles)
        
        assert result == "Обзор новостей"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
