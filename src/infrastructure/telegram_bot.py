"""
Telegram бот на aiogram 3.x для модерации постов
"""
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

try:
    from aiogram import Bot, Dispatcher, Router, F
    from aiogram.types import Update, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.filters import Command
    from aiogram.fsm.storage.memory import MemoryStorage
    AIOMGRAM_AVAILABLE = True
except ImportError:
    AIOMGRAM_AVAILABLE = False

from ..core.logging import log
from ..core.config import settings
from ..domain.entities import SocialPost, ModerationDecision
from ..domain.interfaces import ModerationInterface


class TelegramModeratorBot(ModerationInterface):
    """
    Telegram бот для модерации постов на aiogram 3.x
    
    Поддерживает:
    - Отправку постов на модерацию
    - Inline-кнопки для одобрения/отклонения
    - Хранение состояния модерации
    - Таймауты на решение
    """

    def __init__(self):
        if not AIOMGRAM_AVAILABLE:
            log.warning("aiogram не установлен. Модерация через Telegram недоступна.")
            self.bot = None
            self.dp = None
            self.router = None
            return

        self.bot_token = settings.telegram.token
        self.moderator_chat_id = settings.telegram.moderator_chat_id
        
        if not self.bot_token:
            log.warning("Telegram токен не настроен. Модерация недоступна.")
            self.bot = None
            self.dp = None
            self.router = None
            return

        # Инициализация бота и диспетчера
        storage = MemoryStorage()
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher(storage=storage)
        self.router = Router()
        self.dp.include_router(self.router)

        # Хранилище постов на модерации
        self.pending_moderations: Dict[str, Dict[str, Any]] = {}

        # Регистрация хендлеров
        self._register_handlers()

        log.info("Telegram бот инициализирован")

    def _register_handlers(self):
        """Регистрирует обработчики команд и callback"""
        
        @self.router.command_handler("start")
        async def cmd_start(message: Message):
            """Обработчик команды /start"""
            if message.from_user.id == self.moderator_chat_id:
                await message.reply(
                    "👋 <b>Бот модерации автопостинга ВК</b>\n\n"
                    "Я буду отправлять вам посты на проверку перед публикацией.\n"
                    "Используйте кнопки ✅/❌ для подтверждения или отклонения."
                )
            else:
                await message.reply("❌ Доступ запрещён")

        @self.router.callback_query(F.data.startswith("publish_"))
        async def callback_approve(callback: CallbackQuery):
            """Обработчик кнопки одобрения"""
            moderation_id = callback.data.split("_", 1)[1]
            
            if moderation_id in self.pending_moderations:
                self.pending_moderations[moderation_id]['decision'] = ModerationDecision.APPROVED
                self.pending_moderations[moderation_id]['decided_at'] = datetime.utcnow()
                
                await callback.answer("✅ Пост одобрен", show_alert=True)
                await callback.message.edit_text(
                    f"{callback.message.text}\n\n✅ <b>ОДОБРЕНО</b>",
                    parse_mode="HTML"
                )
                log.info(f"Пост {moderation_id} одобрен модератором")
            else:
                await callback.answer("⚠️ Пост уже обработан", show_alert=True)

        @self.router.callback_query(F.data.startswith("reject_"))
        async def callback_reject(callback: CallbackQuery):
            """Обработчик кнопки отклонения"""
            moderation_id = callback.data.split("_", 1)[1]
            
            if moderation_id in self.pending_moderations:
                self.pending_moderations[moderation_id]['decision'] = ModerationDecision.REJECTED
                self.pending_moderations[moderation_id]['decided_at'] = datetime.utcnow()
                
                await callback.answer("❌ Пост отклонён", show_alert=True)
                await callback.message.edit_text(
                    f"{callback.message.text}\n\n❌ <b>ОТКЛОНЕНО</b>",
                    parse_mode="HTML"
                )
                log.info(f"Пост {moderation_id} отклонён модератором")
            else:
                await callback.answer("⚠️ Пост уже обработан", show_alert=True)

    async def start_polling(self):
        """Запускает поллинг бота"""
        if self.dp:
            log.info("Запуск Telegram бота (polling)...")
            await self.dp.start_polling(self.bot)

    async def stop_polling(self):
        """Останавливает поллинг бота"""
        if self.dp:
            log.info("Остановка Telegram бота...")
            await self.dp.stop_polling(self.bot)
        
        if self.bot:
            await self.bot.session.close()

    async def send_for_moderation(self, post: SocialPost) -> str:
        """
        Отправляет пост на модерацию
        
        Args:
            post: Пост для модерации
            
        Returns:
            ID задачи модерации
        """
        import uuid
        
        if not self.bot or not AIOMGRAM_AVAILABLE:
            log.warning("Telegram не настроен, пропускаем модерацию")
            # Создаем фейковый ID и сразу одобряем
            moderation_id = str(uuid.uuid4())[:8]
            self.pending_moderations[moderation_id] = {
                'post': post,
                'decision': ModerationDecision.APPROVED,
                'sent_at': datetime.utcnow(),
                'decided_at': datetime.utcnow()
            }
            return moderation_id

        moderation_id = str(uuid.uuid4())[:8]

        # Сохраняем пост в ожидании
        self.pending_moderations[moderation_id] = {
            'post': post,
            'decision': ModerationDecision.PENDING,
            'sent_at': datetime.utcnow(),
            'decided_at': None
        }

        try:
            # Формирование сообщения
            text = post.content[:3000]  # Обрезаем до 3000 символов

            message = f"🔍 <b>Новый пост на модерацию</b>\n\n"
            message += f"<b>ID:</b> {moderation_id}\n"
            message += f"<b>Источник:</b> {post.source_type.value}\n"
            
            if post.title:
                message += f"<b>Заголовок:</b> {post.title}\n"
            
            message += f"\n{text}\n\n"

            if post.tags:
                message += f"<b>Теги:</b> #{' #'.join(post.tags)}\n\n"

            if post.scheduled_at:
                message += f"<b>Запланирован на:</b> {post.scheduled_at.strftime('%Y-%m-%d %H:%M')}\n"

            # Кнопки
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Опубликовать",
                            callback_data=f"publish_{moderation_id}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Отклонить",
                            callback_data=f"reject_{moderation_id}"
                        )
                    ]
                ]
            )

            # Отправка сообщения
            await self.bot.send_message(
                chat_id=self.moderator_chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=keyboard
            )

            log.info(f"Пост {moderation_id} отправлен на модерацию")
            return moderation_id

        except Exception as e:
            log.error(f"Ошибка при отправке на модерацию: {e}")
            # При ошибке создаем фейковое одобрение
            self.pending_moderations[moderation_id]['decision'] = ModerationDecision.APPROVED
            self.pending_moderations[moderation_id]['decided_at'] = datetime.utcnow()
            return moderation_id

    async def get_moderation_decision(
        self,
        moderation_id: str
    ) -> Optional[ModerationDecision]:
        """
        Получает решение модератора
        
        Args:
            moderation_id: ID задачи модерации
            
        Returns:
            Решение модератора или None если еще не принято
        """
        if moderation_id not in self.pending_moderations:
            return None

        moderation_data = self.pending_moderations[moderation_id]
        
        # Проверяем таймаут (5 минут)
        if moderation_data['decision'] == ModerationDecision.PENDING:
            elapsed = datetime.utcnow() - moderation_data['sent_at']
            if elapsed > timedelta(minutes=5):
                log.warning(f"Таймаут модерации для поста {moderation_id}")
                moderation_data['decision'] = ModerationDecision.REJECTED
                moderation_data['decided_at'] = datetime.utcnow()

        return moderation_data['decision']

    async def approve_post(self, moderation_id: str) -> bool:
        """
        Одобряет пост
        
        Args:
            moderation_id: ID задачи модерации
            
        Returns:
            True если одобрение успешно
        """
        if moderation_id in self.pending_moderations:
            self.pending_moderations[moderation_id]['decision'] = ModerationDecision.APPROVED
            self.pending_moderations[moderation_id]['decided_at'] = datetime.utcnow()
            log.info(f"Пост {moderation_id} одобрен программно")
            return True
        return False

    async def reject_post(self, moderation_id: str, reason: str = "") -> bool:
        """
        Отклоняет пост
        
        Args:
            moderation_id: ID задачи модерации
            reason: Причина отклонения
            
        Returns:
            True если отклонение успешно
        """
        if moderation_id in self.pending_moderations:
            self.pending_moderations[moderation_id]['decision'] = ModerationDecision.REJECTED
            self.pending_moderations[moderation_id]['decided_at'] = datetime.utcnow()
            if reason:
                self.pending_moderations[moderation_id]['reason'] = reason
            log.info(f"Пост {moderation_id} отклонен программно: {reason}")
            return True
        return False

    async def wait_for_decision(
        self,
        moderation_id: str,
        timeout_seconds: int = 300
    ) -> Optional[ModerationDecision]:
        """
        Ждет решения модератора с таймаутом
        
        Args:
            moderation_id: ID задачи модерации
            timeout_seconds: Максимальное время ожидания
            
        Returns:
            Решение модератора или None при таймауте
        """
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout_seconds:
            decision = await self.get_moderation_decision(moderation_id)
            
            if decision and decision != ModerationDecision.PENDING:
                return decision
            
            await asyncio.sleep(2)  # Проверяем каждые 2 секунды

        # Таймаут
        log.warning(f"Таймаут ожидания решения для поста {moderation_id}")
        return None
