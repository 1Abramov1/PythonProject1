from rest_framework import serializers
from .models import Habit, HabitCompletion


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек с локальным временем"""

    local_time = serializers.SerializerMethodField()
    time_display = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'place', 'time', 'local_time', 'time_display', 'action', 'is_pleasant',
            'related_habit', 'frequency', 'reward', 'duration',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'local_time', 'time_display']

    def get_local_time(self, obj):
        """Возвращает время в локальном часовом поясе (MSK)"""
        return obj.get_local_time_str()

    def get_time_display(self, obj):
        """Возвращает время в формате для отображения"""
        local = obj.get_local_time()
        if local:
            return {
                'msk': f"{local.hour:02d}:{local.minute:02d}",
                'utc': f"{obj.time.hour:02d}:{obj.time.minute:02d}",
                'raw': obj.time
            }
        return None

    def validate(self, data):
        """Валидация привычки"""
        # ТЗ: нельзя одновременно указывать связанную привычку и вознаграждение
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError(
                'Нельзя одновременно указывать связанную привычку и вознаграждение'
            )

        # ТЗ: приятная привычка не может иметь вознаграждение или связанную привычку
        if data.get('is_pleasant') and (data.get('reward') or data.get('related_habit')):
            raise serializers.ValidationError(
                'У приятной привычки не может быть вознаграждения или связанной привычки'
            )

        # ТЗ: связанная привычка должна быть приятной
        if data.get('related_habit'):
            if not data['related_habit'].is_pleasant:
                raise serializers.ValidationError(
                    'Связанная привычка должна быть приятной'
                )

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только чтение)"""

    user = serializers.CharField(source='user.username', read_only=True)
    local_time = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = ['id', 'user', 'action', 'place', 'time', 'local_time', 'duration', 'created_at']
        read_only_fields = ['__all__']

    def get_local_time(self, obj):
        """Возвращает время в локальном часовом поясе (MSK)"""
        return obj.get_local_time_str()


class HabitCompletionSerializer(serializers.ModelSerializer):
    """Сериализатор для отслеживания выполнения привычек"""

    habit_action = serializers.CharField(source='habit.action', read_only=True)
    habit_time = serializers.SerializerMethodField()

    class Meta:
        model = HabitCompletion
        fields = [
            'id',
            'habit',
            'habit_action',
            'habit_time',
            'completion_date',
            'is_completed',
            'completed_at',
            'created_at',
        ]
        read_only_fields = ['created_at', 'habit_action', 'habit_time']

    def get_habit_time(self, obj):
        """Возвращает время привычки в локальном формате"""
        if obj.habit:
            return obj.habit.get_local_time_str()
        return None

    def validate(self, data):
        """Валидация выполнения привычки"""
        habit = data.get('habit')

        # Проверяем контекст запроса
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if habit.user != request.user:
                raise serializers.ValidationError(
                    'Вы можете отслеживать только свои привычки'
                )

        return data