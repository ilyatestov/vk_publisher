"""
Конвейерная обработка постов через asyncio.Queue

Конвейер состоит из 4 воркеров:
1. Fetcher - сбор контента из источников
2. Processor - обработка ИИ (рерайт, суммаризация)
3. Moderation - модерация через Telegram бота
4. Publisher - публикация в VK
"""
import asyncio
from datetime import datetime
from typing import Optional

from ..core.logging import log
from ..core.config import settings
from ..domain.entities import SocialPost, PostStatus, ContentSource
from ..domain.interfaces import (
    ContentFetcherInterface,
    AIProcessorInterface,
    SocialPublisherInterface,
    StorageInterface,
    ModerationInterface
)


class PipelineWorker:
    """
    Конвейерный воркер для обработки постов
    
    Использует asyncio.Queue для передачи постов между этапами
    """

    def __init__(
        self,
        storage: StorageInterface,
        fetcher: Optional[ContentFetcherInterface] = None,
        processor: Optional[AIProcessorInterface] = None,
        publisher: Optional[SocialPublisherInterface] = None,
        moderator: Optional[ModerationInterface] = None,
        queue_size: int = 100
    ):
        self.storage = storage
        self.fetcher = fetcher
        self.processor = processor
        self.publisher = publisher
        self.moderator = moderator

        # Очереди для конвейера
        self.fetcher_queue = asyncio.Queue(maxsize=queue_size)
        self.processor_queue = asyncio.Queue(maxsize=queue_size)
        self.moderation_queue = asyncio.Queue(maxsize=queue_size)
        self.publisher_queue = asyncio.Queue(maxsize=queue_size)

        # Флаги остановки
        self._stop_event = asyncio.Event()

        # Аккаунт по умолчанию
        self._default_account = None

    def set_default_account(self, account):
        """Устанавливает аккаунт по умолчанию для публикации"""
        self._default_account = account

    async def fetcher_worker(self):
        """
        Воркер для сбора контента из источников
        
        Периодически опрашивает источники и добавляет посты в очередь
        """
        log.info("Fetcher worker запущен")
        
        while not self._stop_event.is_set():
            try:
                if not self.fetcher:
                    log.warning("Fetcher не настроен, пропускаем итерацию")
                    await asyncio.sleep(60)
                    continue

                log.info("Сбор контента из источников...")
                posts = await self.fetcher.fetch_content()
                log.info(f"Собрано {len(posts)} материалов")

                for post in posts:
                    # Проверка на дубликаты
                    if hasattr(self.storage, 'check_duplicate') and post.source_url:
                        import hashlib
                        content_hash = hashlib.sha256(post.content.encode()).hexdigest()
                        is_duplicate = await self.storage.check_duplicate(content_hash, days=30)
                        
                        if is_duplicate:
                            log.info(f"Пропущен дубликат: {post.title}")
                            continue

                    # Сохраняем пост в базу
                    saved_post = await self.storage.save_post(post)
                    log.info(f"Пост {saved_post.id} сохранен в БД")

                    # Добавляем в очередь на обработку
                    await self.processor_queue.put(saved_post)
                    log.debug(f"Пост {saved_post.id} добавлен в очередь processor")

                # Пауза между итерациями
                await asyncio.sleep(settings.scheduler.post_interval_minutes * 60)

            except asyncio.CancelledError:
                log.info("Fetcher worker остановлен")
                break
            except Exception as e:
                log.error(f"Ошибка в fetcher worker: {e}")
                await asyncio.sleep(60)

    async def processor_worker(self):
        """
        Воркер для обработки контента ИИ
        
        Выполняет рерайт текста и суммаризацию при необходимости
        """
        log.info("Processor worker запущен")
        
        while not self._stop_event.is_set():
            try:
                post = await asyncio.wait_for(
                    self.processor_queue.get(),
                    timeout=1.0
                )
                
                log.info(f"Обработка поста {post.id} через ИИ...")

                if self.processor:
                    # Переписываем контент через ИИ
                    processed_content = await self.processor.rewrite_content(
                        text=post.content,
                        title=post.title
                    )
                    post.content = processed_content
                
                post.status = PostStatus.PROCESSED
                await self.storage.save_post(post)

                # Добавляем в очередь модерации
                await self.moderation_queue.put(post)
                log.info(f"Пост {post.id} обработан и отправлен на модерацию")

                self.processor_queue.task_done()

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                log.info("Processor worker остановлен")
                break
            except Exception as e:
                log.error(f"Ошибка в processor worker: {e}")
                if 'post' in locals():
                    post.status = PostStatus.FAILED
                    await self.storage.save_post(post)
                await asyncio.sleep(5)

    async def moderation_worker(self):
        """
        Воркер для модерации постов
        
        Отправляет посты в Telegram бота и ждет решения
        """
        log.info("Moderation worker запущен")
        
        while not self._stop_event.is_set():
            try:
                post = await asyncio.wait_for(
                    self.moderation_queue.get(),
                    timeout=1.0
                )
                
                log.info(f"Модерация поста {post.id}...")

                if self.moderator:
                    # Отправляем на модерацию
                    moderation_id = await self.moderator.send_for_moderation(post)
                    
                    # Ждем решения (с таймаутом)
                    decision = await self.moderator.wait_for_decision(
                        moderation_id,
                        timeout_seconds=300  # 5 минут
                    )
                    
                    if decision and decision.value == 'approved':
                        post.status = PostStatus.MODERATED
                        log.info(f"Пост {post.id} одобрен модератором")
                    else:
                        post.status = PostStatus.REJECTED
                        log.info(f"Пост {post.id} отклонен модератором")
                        self.moderation_queue.task_done()
                        continue
                else:
                    # Если модератор не настроен, одобряем автоматически
                    post.status = PostStatus.MODERATED
                    log.warning(f"Модератор не настроен, пост {post.id} одобрен автоматически")

                await self.storage.save_post(post)

                # Добавляем в очередь публикации
                await self.publisher_queue.put(post)

                self.moderation_queue.task_done()

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                log.info("Moderation worker остановлен")
                break
            except Exception as e:
                log.error(f"Ошибка в moderation worker: {e}")
                if 'post' in locals():
                    post.status = PostStatus.FAILED
                    await self.storage.save_post(post)
                await asyncio.sleep(5)

    async def publisher_worker(self):
        """
        Воркер для публикации постов в VK
        
        Проверяет расписание и публикует посты
        """
        log.info("Publisher worker запущен")
        
        while not self._stop_event.is_set():
            try:
                post = await asyncio.wait_for(
                    self.publisher_queue.get(),
                    timeout=1.0
                )
                
                log.info(f"Публикация поста {post.id}...")

                # Проверяем, запланирован ли пост на будущее
                if post.scheduled_at and post.scheduled_at > datetime.utcnow():
                    log.info(f"Пост {post.id} запланирован на {post.scheduled_at}, возвращаем в очередь")
                    await asyncio.sleep(60)  # Проверяем каждую минуту
                    await self.publisher_queue.put(post)
                    self.publisher_queue.task_done()
                    continue

                if self.publisher and self._default_account:
                    # Публикуем пост
                    success = await self.publisher.publish_post(
                        post,
                        self._default_account
                    )
                    
                    if success:
                        post.status = PostStatus.PUBLISHED
                        log.success(f"Пост {post.id} успешно опубликован")
                        
                        # Увеличиваем счетчик постов
                        self._default_account.increment_post_count()
                    else:
                        post.status = PostStatus.FAILED
                        log.error(f"Ошибка публикации поста {post.id}")
                else:
                    log.warning("Publisher или аккаунт не настроены, пост не опубликован")
                    post.status = PostStatus.FAILED

                await self.storage.save_post(post)
                self.publisher_queue.task_done()

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                log.info("Publisher worker остановлен")
                break
            except Exception as e:
                log.error(f"Ошибка в publisher worker: {e}")
                if 'post' in locals():
                    post.status = PostStatus.FAILED
                    await self.storage.save_post(post)
                await asyncio.sleep(5)

    async def start_workers(self):
        """Запускает все воркеры конвейера"""
        log.info("Запуск всех воркеров конвейера...")
        
        tasks = [
            asyncio.create_task(self.fetcher_worker(), name="fetcher"),
            asyncio.create_task(self.processor_worker(), name="processor"),
            asyncio.create_task(self.moderation_worker(), name="moderation"),
            asyncio.create_task(self.publisher_worker(), name="publisher")
        ]
        
        log.info("Все воркеры запущены")
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            log.info("Конвейер остановлен")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Корректная остановка воркеров"""
        log.info("Остановка конвейера...")
        self._stop_event.set()
        
        # Ждем завершения очередей
        await asyncio.gather(
            self.processor_queue.join(),
            self.moderation_queue.join(),
            self.publisher_queue.join(),
            return_exceptions=True
        )
        
        log.info("Конвейер остановлен")
