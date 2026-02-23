from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'telegram_chat_id',
            'telegram_username',
            'notifications_enabled',
            'daily_notification_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_telegram_chat_id(self, value):
        """Валидация Telegram Chat ID"""
        if value and value < 0:
            raise serializers.ValidationError('Telegram Chat ID должен быть положительным числом')
        return value
