from celery import shared_task
from django.utils import timezone
from django.conf import settings
from habits.models import Habit
import asyncio
from telegram import Bot
import logging
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminders():
    """
    Отправка напоминаний о привычках.
    Ищет привычки, которые должны быть выполнены в ближайшие 5 минут.
    """
    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)

    logger.info(f"🕐 Celery запущен в {now_local.strftime('%H:%M')} MSK (UTC: {now_utc.strftime('%H:%M')})")

    # ОТЛАДКА: посмотрим все привычки testuser с временем
    test_habits = Habit.objects.filter(user__username='testuser')
    logger.info(f"📊 Все привычки testuser в БД (UTC):")
    for h in test_habits:
        logger.info(f"   - {h.action}: {h.time.hour}:{h.time.minute:02d} UTC (ID: {h.id})")

    # Ищем привычки, которые нужно выполнить в ближайшие 5 минут
    time_min = now_utc.time()
    time_max = (now_utc + timedelta(minutes=1)).time()

    logger.info(
        f"🔍 Поиск привычек с временем от {time_min.hour}:{time_min.minute:02d} до {time_max.hour}:{time_max.minute:02d} UTC")

    habits = Habit.objects.filter(
        time__gte=time_min,
        time__lte=time_max,
        is_pleasant=False,
        user__profile__notifications_enabled=True,
        user__profile__telegram_chat_id__isnull=False
    ).select_related('user__profile')

    logger.info(f"📋 Найдено привычек для отправки: {habits.count()}")

    if not habits:
        return f"Нет привычек для отправки в ближайшие 5 минут (сейчас {now_local.strftime('%H:%M')} MSK)"

    # Отправка сообщений
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    sent_count = 0

    for habit in habits:
        chat_id = habit.user.profile.telegram_chat_id

        # Конвертация времени привычки в локальное
        habit_utc = timezone.now().replace(
            hour=habit.time.hour,
            minute=habit.time.minute,
            second=0,
            microsecond=0
        )

        # Если время привычки уже прошло сегодня, значит на завтра
        if habit_utc < now_utc:
            habit_utc += timedelta(days=1)

        habit_local = timezone.localtime(habit_utc)

        logger.info(f"📨 Отправка {habit.user.username} на время {habit_local.strftime('%H:%M')} MSK")

        message = (
            f"⏰ *Напоминание о привычке!*\n\n"
            f"📍 *Место:* {habit.place}\n"
            f"🕐 *Время:* {habit_local.strftime('%H:%M')} (по Москве)\n"
            f"📌 *Действие:* {habit.action}\n"
            f"⏱️ *Длительность:* {habit.duration} сек.\n\n"
            f"✅ Отметь выполнение в приложении!"
        )

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            )
            loop.close()
            sent_count += 1
            logger.info(f"✅ Отправлено успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки: {e}")

    return f"Отправлено напоминаний: {sent_count}"