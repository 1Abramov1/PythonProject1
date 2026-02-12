from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение только для владельца объекта"""

    def has_object_permission(self, request, view, obj):
        # Проверяем что объект имеет поле user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Для HabitCompletion проверяем через habit
        elif hasattr(obj, 'habit'):
            return obj.habit.user == request.user
        return False