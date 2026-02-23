import asyncio
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.ext import ContextTypes
import logging

# Состояния для ConversationHandler
SELECTING_ACTION, AWAITING_TOKEN = range(2)

logger = logging.getLogger(__name__)


class HabitBot:
    """Telegram бот для трекера привычек"""

    def __init__(self, token=None):
        self.token = token or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not self.token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN не найден! "
                "Добавь его в .env файл и настройки Django."
            )
        self.application = None
        self.setup_handlers()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        welcome_message = (
            f"👋 Привет, {user.first_name}!\n\n"
            "Я бот для трекера привычек. Помогу тебе не забывать о важных делах!\n\n"
            "📌 **Доступные команды:**\n"
            "/start - показать это меню\n"
            "/connect - привязать аккаунт\n"
            "/habits - список привычек на сегодня\n"
            "/help - помощь\n\n"
            "Чтобы начать, привяжи свой аккаунт командой /connect"
        )

        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def connect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Привязка аккаунта по токену"""
        chat_id = update.effective_chat.id

        message = (
            "🔐 **Привязка аккаунта**\n\n"
            "1. Открой веб-версию трекера привычек\n"
            "2. В профиле нажми 'Подключить Telegram'\n"
            "3. Скопируй код и отправь его сюда\n\n"
            "Или просто отправь мне свой JWT токен:"
        )

        context.user_data['telegram_chat_id'] = chat_id

        await update.message.reply_text(message, parse_mode='Markdown')
        return AWAITING_TOKEN

    async def handle_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка полученного токена"""
        token = update.message.text.strip()
        chat_id = update.effective_chat.id
        telegram_username = update.effective_user.username

        from .services import connect_telegram_account

        success, message = await connect_telegram_account(token, chat_id, telegram_username)

        if success:
            await update.message.reply_text(
                "✅ **Аккаунт успешно привязан!**\n\n"
                "Теперь я буду присылать тебе напоминания о привычках.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Ошибка привязки**\n\n{message}\n\n"
                "Попробуй еще раз командой /connect",
                parse_mode='Markdown'
            )

        return ConversationHandler.END

    async def habits_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать привычки на сегодня"""
        chat_id = update.effective_chat.id

        from .services import get_today_habits
        habits = await get_today_habits(chat_id)

        if not habits:
            await update.message.reply_text(
                "📝 На сегодня у тебя нет запланированных привычек.\n"
                "Отдохни или добавь новые в веб-версии!",
                parse_mode='Markdown'
            )
            return

        message = "📋 **Твои привычки на сегодня:**\n\n"
        for i, habit in enumerate(habits, 1):
            message += f"{i}. {habit['action']} в {habit['time']}\n"
            message += f"   📍 {habit['place']}\n\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Помощь"""
        help_text = (
            "❓ **Помощь**\n\n"
            "📌 **Команды:**\n"
            "/start - начать работу\n"
            "/connect - привязать аккаунт\n"
            "/habits - привычки на сегодня\n"
            "/help - это сообщение\n\n"
            "📱 **Веб-версия:**\n"
            "http://localhost:8000\n\n"
            "📧 **Поддержка:**\n"
            "По всем вопросам пиши на support@example.com"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена текущего действия"""
        await update.message.reply_text(
            "❌ Действие отменено.\n"
            "Можешь воспользоваться другими командами."
        )
        return ConversationHandler.END

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application = Application.builder().token(self.token).build()

        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("habits", self.habits_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("connect", self.connect_command)],
            states={
                AWAITING_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_token)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        self.application.add_handler(conv_handler)

    def run(self):
        """Запуск бота в режиме polling"""
        print("🤖 Telegram бот запущен...")
        self.application.run_polling()
