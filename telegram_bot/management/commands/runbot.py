from django.core.management.base import BaseCommand
from telegram_bot.bot import HabitBot


class Command(BaseCommand):
    help = 'Запуск Telegram бота для трекера привычек'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Запуск Telegram бота...')
        )

        bot = HabitBot()
        bot.run()