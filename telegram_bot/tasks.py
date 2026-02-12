from celery import shared_task
from django.utils import timezone
from habits.models import Habit
from users.models import UserProfile
from .bot import HabitBot
import asyncio


@shared_task
def send_habit_reminders():
    """Отправка напоминаний о привычках"""
    now = timezone.now()
    current_time = now.time()

    # Находим привычки, которые нужно выполнить сейчас (в течение часа)
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute__lte=current_time.minute + 30,
        is_pleasant=False,
        user__profile__notifications_enabled=True,
        user__profile__telegram_chat_id__isnull=False
    ).select_related('user__profile')

    bot = HabitBot()

    for habit in habits:
        chat_id = habit.user.profile.telegram_chat_id
        message = (
            f"⏰ **Напоминание о привычке!**\n\n"
            f"📍 {habit.place}\n"
            f"🕐 {habit.time.strftime('%H:%M')}\n"
            f"📌 {habit.action}\n"
            f"⏱️ {habit.duration} секунд\n\n"
            f"Не забудь выполнить и отметить в приложении! ✅"
        )

        # Отправляем сообщение
        try:
            asyncio.run(bot.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown'))
        except Exception as e:
            print(f"Error sending message to {chat_id}: {e}")

    return f"Sent reminders to {habits.count()} users"
