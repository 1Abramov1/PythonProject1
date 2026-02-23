from django.core.management.base import BaseCommand
import subprocess
import sys


class Command(BaseCommand):
    help = 'Запуск Celery worker и beat'

    def add_arguments(self, parser):
        parser.add_argument(
            '--beat',
            action='store_true',
            help='Запустить Celery Beat',
        )
        parser.add_argument(
            '--worker',
            action='store_true',
            help='Запустить Celery Worker',
        )

    def handle(self, *args, **options):
        if not options['worker'] and not options['beat']:
            # По умолчанию запускаем и worker и beat
            options['worker'] = True
            options['beat'] = True

        commands = []

        if options['worker']:
            commands.append([
                sys.executable, '-m', 'celery', '-A', 'config', 'worker',
                '--loglevel=info', '--pool=solo'
            ])

        if options['beat']:
            commands.append([
                sys.executable, '-m', 'celery', '-A', 'config', 'beat','--loglevel=info', '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler'
            ])

        processes = []
        try:
            for cmd in commands:
                self.stdout.write(self.style.SUCCESS(f'Запуск: {" ".join(cmd)}'))
                processes.append(subprocess.Popen(cmd))

            for p in processes:
                p.wait()

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n🛑 Celery остановлен'))
            for p in processes:
                p.terminate()
