📱# Habit Tracker

📋 О проекте

Веб-приложение для отслеживания привычек с автоматическими напоминаниями в Telegram. 
Позволяет создавать полезные и приятные привычки, отслеживать их выполнение и получать уведомления.

🚀 Технологии

· Backend: Django 4.2, Django REST Framework
· База данных: PostgreSQL / SQLite (для разработки)
· Аутентификация: JWT (djangorestframework-simplejwt)
· Очереди: Celery + Redis
· Telegram Bot: python-telegram-bot
· Документация: Swagger (drf-yasg)
· Тестирование: pytest, coverage (~80%)
· Контейнеризация: Docker, Docker Compose
· Облачный хостинг: Yandex Cloud

✨ Функциональность

· ✅ Регистрация и JWT аутентификация
· ✅ CRUD для привычек (только свои)
· ✅ Публичные привычки (только чтение)
· ✅ Пагинация (5 привычек на страницу)
· ✅ Валидация по ТЗ (длительность ≤ 120с, периодичность 1-7 дней)
· ✅ Telegram бот с командами /start, /habits, /connect
· ✅ Автоматические напоминания за 5 минут до времени привычки
· ✅ Ежедневная сводка в 9:00
· ✅ Поддержка часовых поясов (MSK)

🏗 Установка и запуск

Предварительные требования

· Python 3.13+
· PostgreSQL (опционально)
· Redis

1. Клонирование
git clone https://github.com/New_Alexs/PythonProject1.git
cd PythonProject1

2. Виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Зависимости
pip install -r requirements.txt

4. Настройка окружения

Создайте файл .env в корне проекта:
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite для разработки)
DATABASE_URL=sqlite:///db.sqlite3

# Telegram Bot (получить у @BotFather)
TELEGRAM_BOT_TOKEN=your-bot-token

# Redis
REDIS_URL=redis://localhost:6379/0

5. База данных
python manage.py migrate
python manage.py createsuperuser

6. Запуск (3 терминала)

Терминал 1 - Django сервер:
python manage.py runserver

Терминал 2 - Telegram бот:
python manage.py runbot

Терминал 3 - Celery:
python manage.py run_celery

📱 Telegram Bot

Команды:

· /start - приветствие
· /help - справка
· /habits - привычки на сегодня
· /connect - привязать аккаунт (по JWT токену)

📚 API Документация

После запуска сервера доступна по адресу:

· Swagger UI: http://127.0.0.1:8000/swagger/
· ReDoc: http://127.0.0.1:8000/redoc/

🧪 Тестирование
# Запуск тестов
python manage.py test

# С покрытием
coverage run --source='.' manage.py test
coverage report
coverage html

📁 Структура проекта
PythonProject1/
├── config/              # Настройки Django
├── habits/              # Приложение привычек
├── users/               # Пользователи и профили
├── api/                 # API эндпоинты
├── telegram_bot/        # Telegram интеграция
├── manage.py
├── requirements.txt
└── .env

## 🐳 Запуск через Docker

### Предварительные требования
- Установите [Docker](https://www.docker.com/products/docker-desktop/)
- Установите [Docker Compose](https://docs.docker.com/compose/install/)

### Шаги для запуска

1. Клонируйте репозиторий
   ```bash
   git clone https://github.com/New_Alexs/PythonProject1.git
   cd PythonProject1
   
1.1 Создайте файл .env из шаблона
  
   cp .env.example .env
   
   Отредактируйте .env, указав свои значения (особенно TELEGRAM_BOT_TOKEN)
2.1 Запустите все сервисы
  
   docker-compose up -d
   
3.1 Примените миграции (если не применились автоматически)
  
   docker-compose exec backend python manage.py migrate
   
4.1 Создайте суперпользователя
  
   docker-compose exec backend python manage.py createsuperuser
   
Проверка работоспособности сервисов

Сервис URL / Команда Описание
Backend http://localhost:8000 Django сервер
Admin http://localhost:8000/admin Админ-панель
API Docs http://localhost:8000/swagger/ Swagger документация
PostgreSQL docker-compose exec db psql -U habits_user -d habits_db Подключение к БД
Redis docker-compose exec redis redis-cli ping Должен ответить PONG
Celery Worker docker-compose logs celery_worker Просмотр логов

🚀 Автоматический деплой (CI/CD)

Проект настроен на автоматическое обновление при пуше в ветку develop.

Как это работает:

1. Вы пушите изменения в GitHub
2. GitHub Actions подключается к серверу по SSH
3. Выполняется git pull, пересборка и перезапуск контейнеров
4. Обновлённая версия становится доступна по адресу http://158.160.227.111

Работающий сервер:
🌐 http://158.160.227.111
🔑 Админка: http://158.160.227.111/admin

📄 Лицензия

Этот проект распространяется под лицензией MIT.

👨‍💻 Автор

Александр Абрамов

🙏 Благодарности

· Команда Django за отличный фреймворк
· Сообщество Django REST Framework
· Yandex Cloud за надёжный хостинг
· Все контрибьюторы проекта

⭐️ Не забудьте поставить звезду, если проект был полезен!
