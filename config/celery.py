import os
from celery import Celery


# переменное окружение для Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('habit_tracker')

# Использование строки конфигурации из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически нахождение задачи в приложениях
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
