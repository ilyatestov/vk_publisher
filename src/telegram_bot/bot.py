"""
Telegram бот для модерации постов перед публикацией
"""
from typing import Optional, Dict, Any
from loguru import logger

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("Telegram библиотека не установлена. Модерация через Telegram недоступна.")


class TelegramModerator:
    """Класс для отправки постов на модерацию через Telegram"""
    
    def __init__(self, bot_token: Optional[str], admin_id: Optional[int]):
        """
        Инициализация модератора
        
        Args:
            bot_token: Токен Telegram бота
            admin_id: ID администратора для отправки уведомлений
        """
        self.bot_token = bot_token
        self.admin_id = admin_id
        self.app = None
        self.pending_posts = {}  # Хранение постов на модерации
        
        if TELEGRAM_AVAILABLE and bot_token:
            self._initialize_bot()
        else:
            logger.warning("Telegram бот не инициализирован")
    
    def _initialize_bot(self):
        """Инициализация бота"""
        try:
            self.app = Application.builder().token(self.bot_token).build()
            
            # Регистрация хендлеров
            self.app.add_handler(CommandHandler("start", self.cmd_start))
            self.app.add_handler(CallbackQueryHandler(self.callback_moderation))
            
            logger.info("Telegram бот инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Telegram бота: {e}")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        if update.effective_user.id == self.admin_id:
            await update.message.reply_text(
                "👋 Бот модерации автопостинга ВК\n\n"
                "Я буду отправлять вам посты на проверку перед публикацией.\n"
                "Используйте кнопки ✅/❌ для подтверждения или отклонения."
            )
        else:
            await update.message.reply_text("❌ Доступ запрещён")
    
    async def callback_moderation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопок модерации"""
        query = update.callback_query
        await query.answer()
        
        action = query.data.split('_')[0]
        post_id = query.data.split('_')[1]
        
        if action == 'publish':
            self.pending_posts[post_id]['approved'] = True
            await query.edit_message_text(f"✅ Пост {post_id} одобрен для публикации")
            logger.info(f"Пост {post_id} одобрен администратором")
        
        elif action == 'reject':
            self.pending_posts[post_id]['approved'] = False
            await query.edit_message_text(f"❌ Пост {post_id} отклонён")
            logger.info(f"Пост {post_id} отклонён администратором")
    
    async def send_for_preview(self, post_data: Dict[str, Any]) -> bool:
        """
        Отправка поста на превью администратору
        
        Args:
            post_data: Данные поста
            
        Returns:
            True если одобрено, False если отклонено или таймаут
        """
        if not TELEGRAM_AVAILABLE or not self.bot_token or not self.admin_id:
            # Если Telegram не настроен, пропускаем модерацию
            logger.warning("Telegram не настроен, пропускаем модерацию")
            return True
        
        try:
            import uuid
            post_id = str(uuid.uuid4())[:8]
            
            # Сохраняем пост в ожидании
            self.pending_posts[post_id] = {
                'data': post_data,
                'approved': None  # Пока не решено
            }
            
            # Формирование сообщения
            text = post_data.get('text', '')[:3000]  # Обрезаем до 3000 символов
            
            message = f"🔍 <b>Новый пост на модерацию</b>\n\n"
            message += f"<b>ID:</b> {post_id}\n"
            message += f"<b>Источник:</b> {post_data.get('source', 'unknown')}\n\n"
            message += f"{text}\n\n"
            
            if post_data.get('sources'):
                message += "<b>Источники:</b>\n"
                for source in post_data['sources'][:3]:
                    message += f"• {source.get('title', '')}\n"
            
            # Кнопки
            keyboard = [
                [
                    InlineKeyboardButton("✅ Опубликовать", callback_data=f"publish_{post_id}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{post_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправка сообщения
            await self.app.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            logger.info(f"Пост {post_id} отправлен на модерацию")
            
            # Ждём решения (максимум 5 минут)
            import asyncio
            for _ in range(60):  # 60 попыток по 5 секунд = 5 минут
                await asyncio.sleep(5)
                
                if self.pending_posts[post_id]['approved'] is not None:
                    result = self.pending_posts[post_id]['approved']
                    del self.pending_posts[post_id]
                    return result
            
            # Таймаут
            logger.warning(f"Таймаут модерации для поста {post_id}")
            del self.pending_posts[post_id]
            return False  # По умолчанию отклоняем при таймауте
            
        except Exception as e:
            logger.error(f"Ошибка при отправке на модерацию: {e}")
            return True  # При ошибке пропускаем модерацию
    
    def run_bot(self):
        """Запуск бота (для отдельного процесса)"""
        if self.app:
            logger.info("Запуск Telegram бота...")
            self.app.run_polling(allowed_updates=Update.ALL_TYPES)
        else:
            logger.error("Telegram бот не инициализирован")
