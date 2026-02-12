from django.contrib import admin
from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'time', 'place', 'is_pleasant', 'is_public', 'created_at')
    list_filter = ('is_pleasant', 'is_public', 'created_at', 'user')
    search_fields = ('action', 'place', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
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


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'completion_date', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completion_date')
    search_fields = ('habit__action',)
    readonly_fields = ('created_at',)

