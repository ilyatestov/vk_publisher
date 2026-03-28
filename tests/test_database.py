"""
Тесты для модуля базы данных
"""
import pytest
import asyncio
import os
import tempfile
from datetime import datetime, timedelta

# Добавляем src в путь импорта
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db import Database


@pytest.fixture
def temp_db():
    """Создание временной базы данных для тестов"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
async def initialized_db(temp_db):
    """Инициализированная база данных"""
    db = Database(temp_db)
    await db.initialize()
    yield db


class TestDatabase:
    """Тесты для класса Database"""
    
    @pytest.mark.asyncio
    async def test_initialize_creates_tables(self, temp_db):
        """Тест создания таблиц при инициализации"""
        db = Database(temp_db)
        await db.initialize()
        
        # Проверяем, что файл БД создан
        assert os.path.exists(temp_db)
    
    @pytest.mark.asyncio
    async def test_add_content_hash(self, initialized_db):
        """Тест добавления хеша контента"""
        db = initialized_db
        
        result = await db.add_content_hash(
            content_hash='test_hash_123',
            title='Test Title',
            source='test_source'
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_duplicate_false(self, initialized_db):
        """Тест проверки на дубликат - дубликата нет"""
        db = initialized_db
        
        result = await db.check_duplicate('nonexistent_hash')
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_duplicate_true(self, initialized_db):
        """Тест проверки на дубликат - дубликат есть"""
        db = initialized_db
        
        # Добавляем хеш
        await db.add_content_hash(
            content_hash='duplicate_hash',
            title='Test',
            source='test'
        )
        
        # Проверяем
        result = await db.check_duplicate('duplicate_hash')
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_add_published_post(self, initialized_db):
        """Тест добавления опубликованного поста"""
        db = initialized_db
        
        # Сначала добавляем хеш
        await db.add_content_hash(
            content_hash='post_hash',
            title='Post Title',
            source='vk'
        )
        
        # Добавляем опубликованный пост
        result = await db.add_published_post(
            vk_post_id=12345,
            content_hash='post_hash',
            text='Test post text',
            sources=['https://example.com']
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_add_log(self, initialized_db):
        """Тест добавления записи в лог"""
        db = initialized_db
        
        result = await db.add_log(
            action='publish',
            source='vk',
            post_id=123,
            hash='test_hash',
            status='success'
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_recent_hashes(self, initialized_db):
        """Тест получения недавних хешей"""
        db = initialized_db
        
        # Добавляем несколько хешей
        await db.add_content_hash('hash1', 'Title1', 'source1')
        await db.add_content_hash('hash2', 'Title2', 'source2')
        
        hashes = await db.get_recent_hashes(days=30)
        
        assert len(hashes) >= 2
        assert 'hash1' in hashes
        assert 'hash2' in hashes
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, initialized_db):
        """Тест получения статистики"""
        db = initialized_db
        
        # Добавляем данные
        await db.add_content_hash('stat_hash1', 'Title1', 'source1')
        await db.add_content_hash('stat_hash2', 'Title2', 'source2')
        await db.add_published_post(111, 'stat_hash1', 'text', [])
        
        stats = await db.get_statistics()
        
        assert 'total_hashes' in stats
        assert 'published_count' in stats
        assert 'posts_count' in stats
        assert 'errors_24h' in stats
        assert stats['total_hashes'] >= 2
        assert stats['posts_count'] >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
