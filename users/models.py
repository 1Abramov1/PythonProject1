from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class UserProfile(models.Model):
    """Профиль пользователя для хранения Telegram данных"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )

    # Telegram данные
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name='ID чата в Telegram',
        help_text='ID чата пользователя в Telegram для отправки уведомлений'
    )

    telegram_username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Имя пользователя в Telegram'
    )

    # Настройки уведомлений
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name='Уведомления включены',
        help_text='Включены ли уведомления о привычках'
    )

    # Время для ежедневных уведомлений
    daily_notification_time = models.TimeField(default='09:00',
        verbose_name='Время ежедневных уведомлений'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username if self.user.username else self.user.email}"

    @property
    def has_telegram(self):
        """Есть ли привязанный Telegram аккаунт"""
        return bool(self.telegram_chat_id)


# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()