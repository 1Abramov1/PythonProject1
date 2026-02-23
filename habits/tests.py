from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from habits.models import Habit, HabitCompletion
from datetime import time

User = get_user_model()


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Пить воду',
            frequency=1,
            duration=60,
            is_public=True
        )

    def test_habit_creation(self):
        """Тест создания привычки"""
        self.assertEqual(self.habit.action, 'Пить воду')
        self.assertEqual(self.habit.place, 'Дом')
        self.assertEqual(self.habit.frequency, 1)
        self.assertTrue(self.habit.is_public)

    def test_habit_str(self):
        """Тест строкового представления"""
        expected = f"{self.habit.action} в {self.habit.time} ({self.habit.place})"
        self.assertEqual(str(self.habit), expected)

    def test_get_local_time(self):
        """Тест конвертации времени в локальное"""
        local_time = self.habit.get_local_time()
        self.assertIsNotNone(local_time)


class HabitCompletionModelTest(TestCase):
    """Тесты для модели HabitCompletion"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Пить воду',
            frequency=1,
            duration=60
        )
        self.completion = HabitCompletion.objects.create(
            habit=self.habit,
            completion_date=timezone.now().date(),
            is_completed=True
        )

    def test_completion_creation(self):
        """Тест создания выполнения"""
        self.assertTrue(self.completion.is_completed)
        self.assertEqual(self.completion.habit, self.habit)

    def test_completion_str(self):
        """Тест строкового представления"""
        self.assertIn(self.habit.action, str(self.completion))


class HabitAPITestCase(APITestCase):
    """Тесты для API привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )

        # Создаем привычки для testuser
        self.habit1 = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Пить воду',
            frequency=1,
            duration=60,
            is_public=True
        )
        self.habit2 = Habit.objects.create(
            user=self.user,
            place='Парк',
            time=time(8, 0),
            action='Пробежка',
            frequency=2,
            duration=120,
            is_public=False
        )

        # Создаем привычку для other_user
        self.other_habit = Habit.objects.create(
            user=self.other_user,
            place='Работа',
            time=time(9, 0),
            action='Чужое дело',
            frequency=1,
            duration=60,
            is_public=True
        )

        # Аутентифицируем пользователя
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_my_habits(self):
        """Тест получения своих привычек"""
        url = reverse('my-habits-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем что в ответе есть пагинация
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_public_habits(self):
        """Тест получения публичных привычек"""
        url = reverse('public-habits')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_habit(self):
        """Тест создания привычки"""
        url = reverse('my-habits-list')
        data = {
            'place': 'Спортзал',
            'time': '18:00:00',
            'action': 'Тренировка',
            'frequency': 3,
            'duration': 90,
            'is_public': True
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)

    def test_update_own_habit(self):
        """Тест обновления своей привычки"""
        url = reverse('my-habits-detail', args=[self.habit1.id])
        data = {'action': 'Пить 2 стакана воды'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.action, 'Пить 2 стакана воды')

    def test_cannot_update_others_habit(self):
        """Тест невозможности обновить чужую привычку"""
        url = reverse('my-habits-detail', args=[self.other_habit.id])
        data = {'action': 'Попытка взлома'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_habit(self):
        """Тест удаления своей привычки"""
        url = reverse('my-habits-detail', args=[self.habit1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=self.habit1.id).count(), 0)

    def test_complete_habit(self):
        """Тест отметки выполнения привычки"""
        url = reverse('my-habits-complete', args=[self.habit1.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем что создалась запись о выполнении
        completion = HabitCompletion.objects.filter(
            habit=self.habit1,
            completion_date=timezone.now().date()
        ).first()
        self.assertIsNotNone(completion)
        self.assertTrue(completion.is_completed)


class HabitValidationTest(APITestCase):
    """Тесты валидации привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(20, 0),
            action='Принять ванну',
            is_pleasant=True,
            frequency=1,
            duration=60
        )
        self.client.force_authenticate(user=self.user)

    def test_cannot_have_both_reward_and_related(self):
        """Тест: нельзя одновременно указывать награду и связанную привычку"""
        url = reverse('my-habits-list')
        data = {
            'place': 'Дом',
            'time': '07:00:00',
            'action': 'Зарядка',
            'frequency': 1,
            'duration': 60,
            'reward': 'Кофе',
            'related_habit': self.pleasant_habit.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_habit_must_be_pleasant(self):
        """Тест: связанная привычка должна быть приятной"""
        useful_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time=time(7, 0),
            action='Полезная',
            is_pleasant=False,
            frequency=1,
            duration=60
        )

        url = reverse('my-habits-list')
        data = {
            'place': 'Дом',
            'time': '07:00:00',
            'action': 'Новая привычка',
            'frequency': 1,
            'duration': 60,
            'related_habit': useful_habit.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_habit_cannot_have_reward(self):
        """Тест: приятная привычка не может иметь награду"""
        url = reverse('my-habits-list')
        data = {
            'place': 'Дом',
            'time': '20:00:00',
            'action': 'Приятная',
            'is_pleasant': True,
            'frequency': 1,
            'duration': 60,
            'reward': 'Шоколадка'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duration_max_120(self):
        """Тест: длительность не более 120 секунд"""
        url = reverse('my-habits-list')
        data = {
            'place': 'Дом',
            'time': '07:00:00',
            'action': 'Зарядка',
            'frequency': 1,
            'duration': 121,
            'is_public': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_frequency_between_1_and_7(self):
        """Тест: периодичность от 1 до 7 дней"""
        url = reverse('my-habits-list')
        data = {
            'place': 'Дом',
            'time': '07:00:00',
            'action': 'Зарядка',
            'frequency': 8,
            'duration': 60,
            'is_public': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserAPITest(APITestCase):
    """Тесты для API пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_user_registration(self):
        """Тест регистрации нового пользователя"""
        url = reverse('user_register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_profile(self):
        """Тест получения профиля пользователя"""
        url = reverse('user_profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_telegram_connect(self):
        """Тест привязки Telegram"""
        url = reverse('telegram-connect')
        data = {
            'telegram_chat_id': 123456789,
            'telegram_username': 'test_tg_user'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.telegram_chat_id, 123456789)

    def test_token_obtain(self):
        """Тест получения JWT токена"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
