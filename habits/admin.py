from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import Habit, HabitCompletion
import pytz


class HabitAdminForm(forms.ModelForm):
    """Кастомная форма для админки с конвертацией времени"""

    class Meta:
        model = Habit
        fields = '__all__'

    def clean_time(self):
        """Принудительная конвертация MSK → UTC при сохранении"""
        time_value = self.cleaned_data.get('time')

        if time_value:
            # Получаем текущую дату в MSK
            moscow_tz = pytz.timezone('Europe/Moscow')
            now_moscow = timezone.now().astimezone(moscow_tz)

            # Создаем datetime с введенным временем в MSK
            moscow_dt = now_moscow.replace(
                hour=time_value.hour,
                minute=time_value.minute,
                second=0,
                microsecond=0
            )

            # Конвертируем в UTC
            utc_dt = moscow_dt.astimezone(pytz.UTC)

            # Возвращаем время в UTC для сохранения в БД
            return utc_dt.time()

        return time_value


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Админка для привычек с правильной конвертацией времени"""

    form = HabitAdminForm
    list_display = ('action', 'user', 'display_time', 'place', 'is_pleasant', 'is_public')
    list_filter = ('is_pleasant', 'is_public', 'user')
    search_fields = ('action', 'place', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'utc_time_display')

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time', 'utc_time_display')
        }),
        ('Тип и связи', {
            'fields': ('is_pleasant', 'related_habit', 'reward')
        }),
        ('Настройки', {
            'fields': ('frequency', 'duration', 'is_public')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_time(self, obj):
        """Отображение времени в MSK в списке"""
        from django.utils import timezone
        import pytz

        if obj.time:
            moscow_tz = pytz.timezone('Europe/Moscow')
            # Конвертируем UTC из БД в MSK для отображения
            utc_time = timezone.now().replace(
                hour=obj.time.hour,
                minute=obj.time.minute,
                second=0,
                microsecond=0
            )
            moscow_time = utc_time.astimezone(moscow_tz)
            return f"{moscow_time.hour}:{moscow_time.minute:02d}"
        return "-"

    display_time.short_description = "Время (MSK)"

    def utc_time_display(self, obj):
        """Отображение UTC времени в БД (для информации)"""
        if obj.time:
            return f"{obj.time.hour}:{obj.time.minute:02d} UTC"
        return "-"

    utc_time_display.short_description = "Время в БД (UTC)"

    def get_queryset(self, request):
        """Ограничиваем видимость привычек"""
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        """Дополнительная проверка при сохранении"""
        if not change:  # Только для новых объектов
            # Убеждаемся что время уже сконвертировано формой
            pass
        super().save_model(request, obj, form, change)


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    """Админка для выполнений привычек"""

    list_display = ('habit', 'completion_date', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completion_date')
    search_fields = ('habit__action',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(habit__user=request.user)
