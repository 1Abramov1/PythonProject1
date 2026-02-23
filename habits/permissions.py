from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение только для владельца объекта"""

    def has_object_permission(self, request, view, obj):
        # Проверяем что объект принадлежит текущему пользователю
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'habit'):
            return obj.habit.user == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение:
    - Безопасные методы (GET, HEAD, OPTIONS) - для всех авторизованных
    - Изменение/удаление - только для владельца
    """

    def has_object_permission(self, request, view, obj):
        # Безопасные методы разрешаем всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменение/удаление только для владельца
        return obj.user == request.user