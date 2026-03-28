"""
Асинхронный слой работы с базой данных на SQLAlchemy
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Boolean, ForeignKey, select, func
from sqlalchemy.sql import functions

from ..core.logging import log
from ..core.config import settings
from ..core.exceptions import DatabaseError
from ..domain.entities import SocialPost, PostStatus, ContentSource, VKAccount
from ..domain.interfaces import StorageInterface


class Base(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy"""
    pass


class SocialPostModel(Base):
    """Модель поста в базе данных"""
    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    image_urls: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)  # JSON string
    tags: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # JSON string
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[PostStatus] = mapped_column(
        SQLEnum(PostStatus),
        default=PostStatus.NEW,
        nullable=False
    )
    source_type: Mapped[ContentSource] = mapped_column(
        SQLEnum(ContentSource),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string

    def to_entity(self) -> SocialPost:
        """Конвертирует модель в сущность"""
        import json
        
        return SocialPost(
            id=self.id,
            title=self.title,
            content=self.content,
            source_url=self.source_url,
            image_urls=json.loads(self.image_urls) if self.image_urls else [],
            tags=json.loads(self.tags) if self.tags else [],
            scheduled_at=self.scheduled_at,
            status=self.status,
            source_type=self.source_type,
            created_at=self.created_at,
            updated_at=self.updated_at or self.created_at,
            metadata=json.loads(self.metadata_json) if self.metadata_json else {}
        )

    @classmethod
    def from_entity(cls, entity: SocialPost) -> "SocialPostModel":
        """Создает модель из сущности"""
        import json
        
        return cls(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            source_url=entity.source_url,
            image_urls=json.dumps(entity.image_urls) if entity.image_urls else None,
            tags=json.dumps(entity.tags) if entity.tags else None,
            scheduled_at=entity.scheduled_at,
            status=entity.status,
            source_type=entity.source_type,
            metadata_json=json.dumps(entity.metadata) if entity.metadata else None
        )


class ContentHashModel(Base):
    """Модель для хранения хешей контента (дедупликация)"""
    __tablename__ = "content_hashes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    post_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='pending')


class PublishedPostModel(Base):
    """Модель опубликованных постов"""
    __tablename__ = "published_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vk_post_id: Mapped[int] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    sources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)


class DatabaseStorage(StorageInterface):
    """
    Асинхронное хранилище данных на SQLAlchemy
    
    Поддерживает:
    - SQLite (aiosqlite) для разработки
    - PostgreSQL (asyncpg) для production
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or settings.database.url
        self.engine: Optional[AsyncEngine] = None
        self.SessionLocal: Optional[async_sessionmaker] = None

    async def initialize(self):
        """Инициализирует базу данных и создает таблицы"""
        try:
            self.engine = create_async_engine(
                self.db_url,
                echo=settings.database.echo,
                future=True
            )
            
            self.SessionLocal = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Создаем таблицы
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            log.info(f"База данных инициализирована: {self.db_url}")
            
        except Exception as e:
            log.error(f"Ошибка инициализации базы данных: {e}")
            raise DatabaseError(f"Failed to initialize database: {e}")

    async def close(self):
        """Закрывает соединение с базой данных"""
        if self.engine:
            await self.engine.dispose()
            log.info("Соединение с базой данных закрыто")

    async def save_post(self, post: SocialPost) -> SocialPost:
        """Сохраняет пост в базе данных"""
        async with self.SessionLocal() as session:
            try:
                if post.id:
                    # Обновление существующего поста
                    result = await session.execute(
                        select(SocialPostModel).where(SocialPostModel.id == post.id)
                    )
                    db_post = result.scalar_one_or_none()
                    
                    if db_post:
                        db_post.title = post.title
                        db_post.content = post.content
                        db_post.source_url = post.source_url
                        db_post.image_urls = str(post.image_urls) if post.image_urls else None
                        db_post.tags = str(post.tags) if post.tags else None
                        db_post.scheduled_at = post.scheduled_at
                        db_post.status = post.status
                        db_post.source_type = post.source_type
                        db_post.updated_at = datetime.utcnow()
                        if post.metadata:
                            import json
                            db_post.metadata_json = json.dumps(post.metadata)
                    else:
                        raise DatabaseError(f"Post with id {post.id} not found")
                else:
                    # Создание нового поста
                    db_post = SocialPostModel.from_entity(post)
                    session.add(db_post)

                await session.commit()
                await session.refresh(db_post)

                # Обновляем ID возвращаемого объекта
                post.id = db_post.id
                post.updated_at = db_post.updated_at or post.created_at

                log.info(f"Пост сохранен в базе данных с ID: {db_post.id}")
                return post

            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка сохранения поста: {e}")
                raise DatabaseError(f"Failed to save post: {e}")

    async def get_post(self, post_id: int) -> Optional[SocialPost]:
        """Получает пост по ID"""
        async with self.SessionLocal() as session:
            try:
                result = await session.get(SocialPostModel, post_id)
                
                if result:
                    return result.to_entity()
                return None

            except Exception as e:
                log.error(f"Ошибка получения поста: {e}")
                raise DatabaseError(f"Failed to get post: {e}")

    async def update_post_status(self, post_id: int, status: str) -> bool:
        """Обновляет статус поста"""
        async with self.SessionLocal() as session:
            try:
                result = await session.get(SocialPostModel, post_id)
                
                if result:
                    result.status = PostStatus(status)
                    result.updated_at = datetime.utcnow()
                    await session.commit()
                    log.info(f"Статус поста {post_id} обновлен на {status}")
                    return True
                return False

            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка обновления статуса поста: {e}")
                raise DatabaseError(f"Failed to update post status: {e}")

    async def get_pending_posts(self, limit: int = 100) -> List[SocialPost]:
        """Получает посты в ожидании обработки"""
        async with self.SessionLocal() as session:
            try:
                stmt = select(SocialPostModel).where(
                    SocialPostModel.status.in_([
                        PostStatus.NEW,
                        PostStatus.FETCHED,
                        PostStatus.PROCESSED,
                        PostStatus.MODERATED,
                        PostStatus.SCHEDULED
                    ])
                ).limit(limit)
                
                result = await session.execute(stmt)
                db_posts = result.scalars().all()

                posts = [post.to_entity() for post in db_posts]
                log.info(f"Получено {len(posts)} постов в ожидании обработки")
                return posts

            except Exception as e:
                log.error(f"Ошибка получения pending постов: {e}")
                raise DatabaseError(f"Failed to get pending posts: {e}")

    async def get_posts_by_status(self, status: str, limit: int = 100) -> List[SocialPost]:
        """Получает посты по статусу"""
        async with self.SessionLocal() as session:
            try:
                stmt = select(SocialPostModel).where(
                    SocialPostModel.status == PostStatus(status)
                ).limit(limit)
                
                result = await session.execute(stmt)
                db_posts = result.scalars().all()

                posts = [post.to_entity() for post in db_posts]
                log.info(f"Получено {len(posts)} постов со статусом {status}")
                return posts

            except Exception as e:
                log.error(f"Ошибка получения постов по статусу: {e}")
                raise DatabaseError(f"Failed to get posts by status: {e}")

    async def delete_post(self, post_id: int) -> bool:
        """Удаляет пост из хранилища"""
        async with self.SessionLocal() as session:
            try:
                result = await session.get(SocialPostModel, post_id)
                
                if result:
                    await session.delete(result)
                    await session.commit()
                    log.info(f"Пост {post_id} удален")
                    return True
                return False

            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка удаления поста: {e}")
                raise DatabaseError(f"Failed to delete post: {e}")

    async def add_content_hash(
        self,
        content_hash: str,
        title: str,
        source: str,
        post_id: Optional[int] = None
    ) -> bool:
        """Добавляет хеш контента в базу"""
        async with self.SessionLocal() as session:
            try:
                db_hash = ContentHashModel(
                    hash=content_hash,
                    title=title,
                    source=source,
                    post_id=post_id
                )
                session.add(db_hash)
                await session.commit()
                log.debug(f"Добавлен хеш контента: {content_hash[:16]}...")
                return True

            except Exception as e:
                await session.rollback()
                # Игнорируем дубликаты
                if "UNIQUE constraint" not in str(e):
                    log.error(f"Ошибка добавления хеша: {e}")
                return False

    async def check_duplicate(self, content_hash: str, days: int = 30) -> bool:
        """Проверяет наличие дубликата"""
        async with self.SessionLocal() as session:
            try:
                from datetime import timedelta
                
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                stmt = select(ContentHashModel).where(
                    ContentHashModel.hash == content_hash,
                    ContentHashModel.created_at > cutoff_date
                )
                
                result = await session.execute(stmt)
                exists = result.scalar_one_or_none() is not None
                
                return exists

            except Exception as e:
                log.error(f"Ошибка проверки дубликата: {e}")
                raise DatabaseError(f"Failed to check duplicate: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Получает статистику по базе данных"""
        async with self.SessionLocal() as session:
            try:
                # Количество хешей
                total_hashes_stmt = select(func.count()).select_from(ContentHashModel)
                total_hashes = (await session.execute(total_hashes_stmt)).scalar()

                # Количество опубликованных
                published_count_stmt = select(func.count()).select_from(ContentHashModel).where(
                    ContentHashModel.status == 'published'
                )
                published_count = (await session.execute(published_count_stmt)).scalar()

                # Количество постов
                posts_count_stmt = select(func.count()).select_from(SocialPostModel)
                posts_count = (await session.execute(posts_count_stmt)).scalar()

                # Количество ошибок за последние 24 часа
                from datetime import timedelta
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                errors_24h_stmt = select(func.count()).select_from(SocialPostModel).where(
                    SocialPostModel.status == PostStatus.FAILED,
                    SocialPostModel.updated_at > cutoff_time
                )
                errors_24h = (await session.execute(errors_24h_stmt)).scalar()

                return {
                    'total_hashes': total_hashes or 0,
                    'published_count': published_count or 0,
                    'posts_count': posts_count or 0,
                    'errors_24h': errors_24h or 0
                }

            except Exception as e:
                log.error(f"Ошибка получения статистики: {e}")
                raise DatabaseError(f"Failed to get statistics: {e}")
