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
from typing import Optional, Set
import hashlib

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

        # Ограничение параллелизма модерации
        self._moderation_semaphore = asyncio.Semaphore(5)
        self._moderation_tasks: Set[asyncio.Task] = set()

        # Границы адаптивного polling fetcher
        self._fetcher_sleep_min = 10
        self._fetcher_sleep_max = max(settings.scheduler.post_interval_minutes * 60, 30)

    def set_default_account(self, account):
        """Устанавливает аккаунт по умолчанию для публикации"""
        self._default_account = account

    def _compute_fetcher_sleep_seconds(self) -> int:
        """Адаптивный интервал опроса на основе backlog очередей."""
        base = settings.scheduler.post_interval_minutes * 60
        backlog = (
            self.processor_queue.qsize()
            + self.moderation_queue.qsize()
            + self.publisher_queue.qsize()
        )

        if backlog > 100:
            return min(self._fetcher_sleep_max, max(base * 3, self._fetcher_sleep_min))
        if backlog > 50:
            return min(self._fetcher_sleep_max, max(base * 2, self._fetcher_sleep_min))
        if backlog > 20:
            return min(self._fetcher_sleep_max, max(int(base * 1.5), self._fetcher_sleep_min))

        return max(self._fetcher_sleep_min, min(base, self._fetcher_sleep_max))

    @staticmethod
    def _build_idempotency_key(post: SocialPost) -> str:
        """Строит idempotency key для публикации поста."""
        scheduled = post.scheduled_at.isoformat() if post.scheduled_at else ""
        raw = f"{post.title}|{post.content}|{post.source_url or ''}|{scheduled}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def _handle_moderation(self, post):
        """Обработка модерации одного поста в отдельной задаче."""
        async with self._moderation_semaphore:
            if self._stop_event.is_set():
                return

            try:
                if self.moderator:
                    moderation_id = await self.moderator.send_for_moderation(post)
                    decision = await self.moderator.wait_for_decision(
                        moderation_id,
                        timeout_seconds=300
                    )

                    if decision and decision.value == 'approved':
                        post.status = PostStatus.MODERATED
                        log.info(f"Пост {post.id} одобрен модератором")
                    else:
                        post.status = PostStatus.REJECTED
                        log.info(f"Пост {post.id} отклонен модератором")
                        await self.storage.save_post(post)
                        return
                else:
                    post.status = PostStatus.MODERATED
                    log.warning(f"Модератор не настроен, пост {post.id} одобрен автоматически")

                await self.storage.save_post(post)
                await self.publisher_queue.put(post)
            except Exception as e:
                log.error(f"Ошибка в задаче модерации поста {getattr(post, 'id', 'unknown')}: {e}")
                post.status = PostStatus.FAILED
                await self.storage.save_post(post)

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

                sleep_seconds = self._compute_fetcher_sleep_seconds()
                log.debug(f"Fetcher sleep: {sleep_seconds}s")
                await asyncio.sleep(sleep_seconds)

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
        
        Отправляет посты в Telegram бота неблокирующе:
        каждый пост обрабатывается в отдельной ограниченной задаче.
        """
        log.info("Moderation worker запущен")
        
        while not self._stop_event.is_set():
            try:
                post = await asyncio.wait_for(
                    self.moderation_queue.get(),
                    timeout=1.0
                )
                
                log.info(f"Модерация поста {post.id}...")

                task = asyncio.create_task(self._handle_moderation(post), name=f"moderation-{post.id}")
                self._moderation_tasks.add(task)
                task.add_done_callback(self._moderation_tasks.discard)

                self.moderation_queue.task_done()

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                log.info("Moderation worker остановлен")
                break
            except Exception as e:
                log.error(f"Ошибка в moderation worker: {e}")
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
                    idempotency_key = self._build_idempotency_key(post)
                    if hasattr(self.storage, "is_publication_key_used"):
                        already_published = await self.storage.is_publication_key_used(idempotency_key)
                        if already_published:
                            log.warning(f"Пропуск повторной публикации поста {post.id} по idempotency key")
                            post.status = PostStatus.PUBLISHED
                            await self.storage.save_post(post)
                            self.publisher_queue.task_done()
                            continue

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

                        if hasattr(self.storage, "register_publication_key"):
                            await self.storage.register_publication_key(
                                idempotency_key=idempotency_key,
                                text=post.content,
                            )
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

        if self._moderation_tasks:
            await asyncio.gather(*self._moderation_tasks, return_exceptions=True)
        
        log.info("Конвейер остановлен")
