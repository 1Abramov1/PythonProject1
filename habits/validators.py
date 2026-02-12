from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_habit_duration(value):
    """Валидация времени выполнения привычки (не более 120 секунд)"""
    if value > 120:
        raise ValidationError('Время выполнения не должно превышать 120 секунд')
    return value


def validate_habit_frequency(value):
    """Валидация периодичности привычки (от 1 до 7 дней)"""
    if value < 1 or value > 7:
        raise ValidationError('Периодичность должна быть от 1 до 7 дней')
    return value


def validate_related_habit_and_reward(data):
    """
    Валидация 1 из ТЗ:
    Исключить одновременный выбор связанной привычки и указания вознаграждения
    """
    related_habit = data.get('related_habit')
    reward = data.get('reward')

    if related_habit and reward:
        raise ValidationError(
            'Нельзя одновременно указывать связанную привычку и вознаграждение'
        )
    return data


def validate_pleasant_habit_constraints(data):
    """
    Валидация 3 из ТЗ:
    У приятной привычки не может быть вознаграждения или связанной привычки
    """
    is_pleasant = data.get('is_pleasant', False)
    reward = data.get('reward')
    related_habit = data.get('related_habit')

    if is_pleasant and (reward or related_habit):
        raise ValidationError(
            'У приятной привычки не может быть вознаграждения или связанной привычки'
        )
    return data


def validate_related_habit_is_pleasant(related_habit):
    """
    Валидация 2 из ТЗ:
    В связанные привычки могут попадать только привычки с признаком приятной привычки
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            'В связанные привычки могут попадать только приятные привычки'
        )
    return related_habit


def validate_not_self_reference(habit, related_habit):
    """Привычка не может ссылаться на саму себя"""
    if related_habit and habit and related_habit.id == habit.id:
        raise ValidationError('Привычка не может ссылаться на саму себя')
    return related_habit