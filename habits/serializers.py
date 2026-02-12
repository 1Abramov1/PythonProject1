from rest_framework import serializers
from .models import Habit, HabitCompletion
from .validators import (
    validate_habit_duration,
    validate_habit_frequency,
    validate_related_habit_and_reward,
    validate_pleasant_habit_constraints,
    validate_related_habit_is_pleasant,
    validate_not_self_reference,
)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    class Meta:
        model = Habit
        fields = [
            'id',
            'user',
            'place',
            'time',
            'action',
            'is_pleasant',
            'related_habit',
            'frequency',
            'reward',
            'duration',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_duration(self, value):
        """Валидация времени выполнения"""
        return validate_habit_duration(value)

    def validate_frequency(self, value):
        """Валидация периодичности"""
        return validate_habit_frequency(value)

    def validate(self, data):
        """Комплексная валидация привычки"""
        # Получаем текущий экземпляр если есть (для обновления)
        instance = self.instance

        # Валидация 1: связанная привычка и вознаграждение
        data = validate_related_habit_and_reward(data)

        # Валидация 3: приятная привычка не может иметь вознаграждение или связанную привычку
        data = validate_pleasant_habit_constraints(data)

        # Валидация 2: связанная привычка должна быть приятной
        related_habit = data.get('related_habit')
        if related_habit:
            validate_related_habit_is_pleasant(related_habit)

        # Валидация: привычка не может ссылаться на саму себя
        if instance and related_habit:
            validate_not_self_reference(instance, related_habit)

        return data

    def create(self, validated_data):
        """Автоматически устанавливаем текущего пользователя как создателя"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HabitListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка привычек"""

    class Meta:
        model = Habit
        fields = [
            'id',
            'action',
            'place',
            'time',
            'is_pleasant',
            'is_public',
            'created_at',
        ]


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только чтение)"""
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id',
            'user',
            'action',
            'place',
            'time',
            'frequency',
            'duration',
            'created_at',
        ]
        read_only_fields = fields


class HabitCompletionSerializer(serializers.ModelSerializer):
    """Сериализатор для отслеживания выполнения привычек"""

    class Meta:
        model = HabitCompletion
        fields = [
            'id',
            'habit',
            'completion_date',
            'is_completed',
            'completed_at',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        """Валидация выполнения привычки"""
        habit = data.get('habit')
        completion_date = data.get('completion_date')

        # Проверяем, что привычка принадлежит текущему пользователю
        request = self.context.get('request')
        if request and habit.user != request.user:
            raise serializers.ValidationError(
                'Вы можете отслеживать только свои привычки'
            )

        # Проверяем, что дата не в будущем
        from django.utils import timezone
        if completion_date > timezone.now().date():
            raise serializers.ValidationError(
                'Дата выполнения не может быть в будущем'
            )

        return data