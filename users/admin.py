from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_username', 'telegram_chat_id', 'notifications_enabled')
    list_filter = ('notifications_enabled',)
    search_fields = ('user__username', 'user__email', 'telegram_username')
    readonly_fields = ('created_at', 'updated_at')