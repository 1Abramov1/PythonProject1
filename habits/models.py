from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

User = get_user_model()


class Habit(models.Model):
    """Модель привычки по ТЗ"""

    # Пользователь — создатель привычки.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )

    # Место — место, в котором необходимо выполнять привычку.
    place = models.CharField(
        max_length=255,
        verbose_name='Место',
        help_text='Место, в котором необходимо выполнять привычку'
    )

    # Время — время, когда необходимо выполнять привычку.
    time = models.TimeField(
        verbose_name='Время выполнения',
        help_text='Время, когда необходимо выполнять привычку'
    )

    # Действие — действие, которое представляет собой привычка.
    action = models.CharField(
        max_length=255,
        verbose_name='Действие',
        help_text='Конкретное действие, которое нужно выполнить'
    )

    # Признак приятной привычки — привычка, которую можно привязать к выполнению полезной привычки.
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка',
        help_text='Является ли привычка приятной (вознаграждением)'
    )

    # Связанная привычка — привычка, которая связана с другой привычкой.
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_habits',
        verbose_name='Связанная привычка',
        help_text='Привычка, которая связана с другой привычкой (только для полезных привычек)'
    )

    # Периодичность (по умолчанию ежедневная) — периодичность выполнения привычки для напоминания в днях.
    frequency = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Периодичность (в днях)',
        help_text='Периодичность выполнения привычки для напоминания в днях (от 1 до 7)'
    )

    # Вознаграждение — чем пользователь должен себя вознаградить после выполнения.
    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Вознаграждение',
        help_text='Чем пользователь должен себя вознаградить после выполнения'
    )

    # Время на выполнение — время, которое предположительно потратит пользователь на выполнение привычки.
    duration = models.PositiveIntegerField(
        default=60,
        validators=[MaxValueValidator(120)],
        verbose_name='Время на выполнение (в секундах)',
        help_text='Время, которое предположительно потратит пользователь на выполнение привычки (не более 120 секунд)'
    )

    # Признак публичности — привычки можно публиковать в общий доступ.
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичная привычка',
        help_text='Привычки можно публиковать в общий доступ'
    )

    # Дата создания
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} в {self.time} ({self.place})"

    def clean(self):
        """Валидация на уровне модели"""

        # Валидация 1: Исключить одновременный выбор связанной привычки и указания вознаграждения
        if self.related_habit and self.reward:
            raise ValidationError('Нельзя одновременно указывать связанную привычку и вознаграждение'
            )

        # Валидация 2: В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and self.related_habit.id and not self.related_habit.is_pleasant:
            raise ValidationError(
                'В связанные привычки могут попадать только приятные привычки'
            )

        # Валидация 3: У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                'У приятной привычки не может быть вознаграждения или связанной привычки'
            )

        # Валидация 4: Нельзя ссылаться на себя
        if self.related_habit and self.related_habit.id == self.id:
            raise ValidationError('Привычка не может ссылаться на саму себя')

        # Валидация 5: Время выполнения не более 120 секунд
        if self.duration > 120:
            raise ValidationError('Время выполнения не должно превышать 120 секунд')

        # Валидация 6: Периодичность от 1 до 7 дней
        if self.frequency < 1 or self.frequency > 7:
            raise ValidationError('Периодичность должна быть от 1 до 7 дней')

        super().clean()

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова clean"""
        self.full_clean()
        super().save(*args, **kwargs)

# Класс HabitCompletion должен быть ОТДЕЛЬНО или использовать строковую ссылку
class HabitCompletion(models.Model):
    """Отслеживание выполнения привычек"""

    habit = models.ForeignKey(
        'Habit',  # Используем строковую ссылку вместо класса
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name='Привычка'
    )

    completion_date = models.DateField(
        verbose_name='Дата выполнения'
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name='Выполнено'
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время выполнения'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Выполнение привычки'
        verbose_name_plural = 'Выполнения привычек'
        unique_together = ['habit', 'completion_date']
        ordering = ['-completion_date']

    def __str__(self):
        status = "Выполнена" if self.is_completed else "Не выполнена"
        return f"{self.completion_date} - {status}"

    def save(self, *args, **kwargs):
        # Если отмечаем как выполненную, устанавливаем время выполнения
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None

        super().save(*args, **kwargs)