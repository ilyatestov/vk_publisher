"""
База данных для хранения постов и проверки дубликатов
"""
import aiosqlite
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger


class Database:
    """Класс для работы с SQLite базой данных"""
    
    def __init__(self, db_path: str):
        """
        Инициализация базы данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
    
    async def initialize(self):
        """Инициализация таблиц базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица для хешей контента
            await db.execute('''
                CREATE TABLE IF NOT EXISTS content_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE NOT NULL,
                    title TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    post_id INTEGER,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Таблица для опубликованных постов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS published_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vk_post_id INTEGER,
                    content_hash TEXT,
                    text TEXT,
                    sources TEXT,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица для логов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action TEXT,
                    source TEXT,
                    post_id INTEGER,
                    hash TEXT,
                    status TEXT,
                    error TEXT
                )
            ''')
            
            # Индексы для ускорения поиска
            await db.execute('CREATE INDEX IF NOT EXISTS idx_hash ON content_hashes(hash)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_created ON content_hashes(created_at)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_status ON content_hashes(status)')
            
            await db.commit()
            logger.info(f"База данных инициализирована: {self.db_path}")
    
    async def check_duplicate(self, content_hash: str, days: int = 30) -> bool:
        """
        Проверка наличия дубликата
        
        Args:
            content_hash: Хеш контента
            days: Период проверки в днях
            
        Returns:
            True если дубликат найден, False иначе
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''
                SELECT id FROM content_hashes 
                WHERE hash = ? AND created_at > ?
                ''',
                (content_hash, datetime.now() - timedelta(days=days))
            )
            result = await cursor.fetchone()
            return result is not None
    
    async def add_content_hash(self, 
                               content_hash: str, 
                               title: str, 
                               source: str,
                               post_id: Optional[int] = None) -> bool:
        """
        Добавление хеша контента в базу
        
        Args:
            content_hash: Хеш контента
            title: Заголовок
            source: Источник
            post_id: ID поста в VK (опционально)
            
        Returns:
            True если успешно добавлено
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    '''
                    INSERT OR IGNORE INTO content_hashes (hash, title, source, post_id)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (content_hash, title, source, post_id)
                )
                await db.commit()
                logger.debug(f"Добавлен хеш контента: {content_hash[:16]}...")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении хеша: {e}")
            return False
    
    async def add_published_post(self, 
                                 vk_post_id: int,
                                 content_hash: str,
                                 text: str,
                                 sources: List[str]) -> bool:
        """
        Добавление информации об опубликованном посте
        
        Args:
            vk_post_id: ID поста в VK
            content_hash: Хеш контента
            text: Текст поста
            sources: Список источников
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    '''
                    INSERT INTO published_posts (vk_post_id, content_hash, text, sources)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (vk_post_id, content_hash, text, str(sources))
                )
                
                # Обновление статуса хеша
                await db.execute(
                    '''
                    UPDATE content_hashes 
                    SET status = 'published', post_id = ?
                    WHERE hash = ?
                    ''',
                    (vk_post_id, content_hash)
                )
                
                await db.commit()
                logger.success(f"Добавлен опубликованный пост: VK ID {vk_post_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении опубликованного поста: {e}")
            return False
    
    async def add_log(self, 
                      action: str,
                      source: str,
                      post_id: Optional[int],
                      hash: Optional[str],
                      status: str,
                      error: Optional[str] = None) -> bool:
        """
        Добавление записи в лог
        
        Args:
            action: Действие (fetch/rewrite/publish/error)
            source: Источник
            post_id: ID поста
            hash: Хеш контента
            status: Статус (success/failed/skipped)
            error: Сообщение об ошибке
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    '''
                    INSERT INTO logs (action, source, post_id, hash, status, error)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (action, source, post_id, hash, status, error)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении лога: {e}")
            return False
    
    async def get_recent_hashes(self, days: int = 30) -> List[str]:
        """
        Получение списка хешей за последние дни
        
        Args:
            days: Период в днях
            
        Returns:
            Список хешей
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''
                SELECT hash FROM content_hashes 
                WHERE created_at > ?
                ''',
                (datetime.now() - timedelta(days=days),)
            )
            results = await cursor.fetchall()
            return [row[0] for row in results]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по базе данных
        
        Returns:
            Словарь со статистикой
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Количество хешей
            cursor = await db.execute('SELECT COUNT(*) FROM content_hashes')
            total_hashes = (await cursor.fetchone())[0]
            
            # Количество опубликованных
            cursor = await db.execute("SELECT COUNT(*) FROM content_hashes WHERE status = 'published'")
            published_count = (await cursor.fetchone())[0]
            
            # Количество постов в таблице published_posts
            cursor = await db.execute('SELECT COUNT(*) FROM published_posts')
            posts_count = (await cursor.fetchone())[0]
            
            # Количество ошибок за последние 24 часа
            cursor = await db.execute(
                "SELECT COUNT(*) FROM logs WHERE status = 'failed' AND timestamp > ?",
                (datetime.now() - timedelta(hours=24),)
            )
            errors_24h = (await cursor.fetchone())[0]
            
            return {
                'total_hashes': total_hashes,
                'published_count': published_count,
                'posts_count': posts_count,
                'errors_24h': errors_24h
            }
