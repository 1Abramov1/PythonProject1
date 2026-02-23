from django.test import TestCase
from django.contrib.auth import get_user_model
from habits.models import Habit
from users.models import UserProfile
from telegram_bot.services import connect_telegram_account, get_today_habits
from telegram_bot.tasks import send_habit_reminders
from datetime import time
from unittest.mock import patch, AsyncMock, MagicMock
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TelegramServicesTest(TestCase):
    """Тесты для сервисов Telegram бота"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.get(user=self.user)

    def test_connect_telegram_account_success(self):
        """Тест успешной привязки Telegram аккаунта"""
        refresh = RefreshToken.for_user(self.user)
        token = str(refresh.access_token)

        success, message = async_to_sync(connect_telegram_account)(
            token, 123456789, 'test_tg_user'
        )

        self.assertTrue(success)
        self.assertEqual(message, "Аккаунт успешно привязан")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.telegram_chat_id, 123456789)
        self.assertEqual(self.profile.telegram_username, 'test_tg_user')

    def test_connect_telegram_account_invalid_token(self):
        """Тест привязки с невалидным токеном"""
        success, message = async_to_sync(connect_telegram_account)(
            'invalid_token', 123456789, 'test_tg_user'
        )

        self.assertFalse(success)
        self.assertIn('Ошибка', message)

    @patch('telegram_bot.services.Habit.objects.filter')
    def test_get_today_habits_success(self, mock_filter):
        """Тест получения привычек на сегодня с моками"""
        self.profile.telegram_chat_id = 123456789
        self.profile.save()

        # Создаем моки для привычек
        mock_habit1 = MagicMock()
        mock_habit1.action = 'Пить воду'
        mock_habit1.place = 'Дом'
        mock_habit1.get_local_time.return_value = time(7, 0)
        mock_habit1.duration = 60

        mock_habit2 = MagicMock()
        mock_habit2.action = 'Пробежка'
        mock_habit2.place = 'Парк'
        mock_habit2.get_local_time.return_value = time(8, 30)
        mock_habit2.duration = 120

        # Настраиваем mock_filter
        mock_filter.return_value.order_by.return_value = [mock_habit1, mock_habit2]

        habits = async_to_sync(get_today_habits)(123456789)

        self.assertEqual(len(habits), 2)
        self.assertEqual(habits[0]['action'], 'Пить воду')

    def test_get_today_habits_no_profile(self):
        """Тест получения привычек без профиля"""
        habits = async_to_sync(get_today_habits)(999999999)
        self.assertEqual(len(habits), 0)


class TelegramTasksTest(TestCase):
    """Тесты для задач Celery"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.telegram_chat_id = 123456789
        self.profile.notifications_enabled = True
        self.profile.save()

    def test_send_habit_reminders_no_habits(self):
        """Тест отправки напоминаний когда нет привычек"""
        result = send_habit_reminders()
        self.assertIn('Нет привычек', result)


class TelegramBotCommandsTest(TestCase):
    """Тесты для команд Telegram бота"""

    def setUp(self):
        from telegram_bot.bot import HabitBot
        self.bot = HabitBot(token='test_token')
        self.update = MagicMock()
        self.context = MagicMock()

        # ✅ ВАЖНО: используем AsyncMock для асинхронных методов
        self.update.message = MagicMock()
        self.update.message.reply_text = AsyncMock()
        self.update.effective_user = MagicMock()
        self.update.effective_user.first_name = 'Test'
        self.update.effective_chat = MagicMock()
        self.update.effective_chat.id = 123456789

    def test_start_command(self):
        """Тест команды /start"""
        async_to_sync(self.bot.start_command)(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    def test_help_command(self):
        """Тест команды /help"""
        async_to_sync(self.bot.help_command)(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    @patch('telegram_bot.services.get_today_habits')
    def test_habits_command_with_habits(self, mock_get_habits):
        """Тест команды /habits когда есть привычки"""
        mock_get_habits.return_value = [
            {'action': 'Пить воду', 'time': '07:00', 'place': 'Дом'},
            {'action': 'Пробежка', 'time': '08:30', 'place': 'Парк'}
        ]

        async_to_sync(self.bot.habits_command)(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    @patch('telegram_bot.services.get_today_habits')
    def test_habits_command_no_habits(self, mock_get_habits):
        """Тест команды /habits когда нет привычек"""
        mock_get_habits.return_value = []

        async_to_sync(self.bot.habits_command)(self.update, self.context)
        self.update.message.reply_text.assert_called_once()

    def test_connect_command(self):
        """Тест команды /connect"""
        result = async_to_sync(self.bot.connect_command)(self.update, self.context)
        self.assertEqual(result, 1)
        self.update.message.reply_text.assert_called_once()

    @patch('telegram_bot.services.connect_telegram_account')
    def test_handle_token_success(self, mock_connect):
        """Тест успешной обработки токена"""
        mock_connect.return_value = (True, "Аккаунт успешно привязан")
        self.update.message.text = "valid_token"
        self.update.effective_user.username = "testuser"

        result = async_to_sync(self.bot.handle_token)(self.update, self.context)

        self.assertEqual(result, -1)
        self.update.message.reply_text.assert_called_once()

    @patch('telegram_bot.services.connect_telegram_account')
    def test_handle_token_failure(self, mock_connect):
        """Тест ошибки при обработке токена"""
        mock_connect.return_value = (False, "Неверный токен")
        self.update.message.text = "invalid_token"

        result = async_to_sync(self.bot.handle_token)(self.update, self.context)

        self.assertEqual(result, -1)
        self.update.message.reply_text.assert_called_once()

    def test_cancel_command(self):
        """Тест команды отмены"""
        result = async_to_sync(self.bot.cancel)(self.update, self.context)
        self.assertEqual(result, -1)
        self.update.message.reply_text.assert_called_once()