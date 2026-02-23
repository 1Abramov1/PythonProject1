from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from users.models import UserProfile
from habits.models import Habit
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@sync_to_async
def _connect_telegram_account_sync(token, chat_id, telegram_username):
    """Синхронная функция для привязки Telegram"""
    try:
        # Декодируем токен и получаем пользователя
        access_token = AccessToken(token)
        user_id = access_token['user_id']

        user = User.objects.get(id=user_id)

        # Обновляем профиль
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.telegram_chat_id = chat_id
        profile.telegram_username = telegram_username
        profile.notifications_enabled = True
        profile.save()

        logger.info(f"Telegram аккаунт {telegram_username} привязан к пользователю {user.username}")
        return True, "Аккаунт успешно привязан"

    except Exception as e:
        logger.error(f"Ошибка привязки Telegram: {e}")
        return False, f"Ошибка: {str(e)}"


async def connect_telegram_account(token, chat_id, telegram_username):
    """Асинхронная обертка для привязки Telegram"""
    return await _connect_telegram_account_sync(token, chat_id, telegram_username)


@sync_to_async
def _get_today_habits_sync(chat_id):
    """Синхронная функция для получения привычек"""
    try:
        profile = UserProfile.objects.get(telegram_chat_id=chat_id)
        user = profile.user

        now = timezone.now()
        current_time = now.time()

        habits = Habit.objects.filter(
            user=user,
            is_pleasant=False,
            time__gte=current_time
        ).order_by('time')[:10]

        return [
            {
                'id': h.id,
                'action': h.action,
                'time': h.time.strftime('%H:%M'),
                'place': h.place,
                'duration': h.duration
            }
            for h in habits
        ]
    except UserProfile.DoesNotExist:
        return []
    except Exception as e:
        logger.error(f"Error getting habits: {e}")
        return []


async def get_today_habits(chat_id):
    """Асинхронная обертка для получения привычек"""
    return await _get_today_habits_sync(chat_id)