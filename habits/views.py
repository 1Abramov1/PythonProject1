from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Habit, HabitCompletion
from .serializers import (
    HabitSerializer,
    PublicHabitSerializer,
    HabitCompletionSerializer
)


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек текущего пользователя"""

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращаем только привычки текущего пользователя.
        Для Swagger генерации возвращаем пустой queryset.
        """
        # Добавляем проверку для Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Habit.objects.none()

        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя при создании"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Список публичных привычек - доступно без авторизации"""
        public_habits = Habit.objects.filter(is_public=True)

        # Пагинация
        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = PublicHabitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PublicHabitSerializer(public_habits, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Отметить привычку как выполненную"""
        try:
            habit = self.get_object()
        except:
            return Response(
                {'error': 'Привычка не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        if habit.user != request.user:
            return Response(
                {'error': 'Вы не можете отмечать чужие привычки'},
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.now().date()
        completion, created = HabitCompletion.objects.get_or_create(
            habit=habit,
            completion_date=today,
            defaults={'is_completed': True}
        )

        if not created:
            completion.is_completed = True
            completion.save()

        serializer = HabitCompletionSerializer(completion)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def completions(self, request, pk=None):
        """Получить историю выполнения привычки"""
        try:
            habit = self.get_object()
        except:
            return Response(
                {'error': 'Привычка не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        if habit.user != request.user:
            return Response(
                {'error': 'Вы не можете просматривать чужие привычки'},
                status=status.HTTP_403_FORBIDDEN
            )

        completions = habit.completions.all()

        page = self.paginate_queryset(completions)
        if page is not None:
            serializer = HabitCompletionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HabitCompletionSerializer(completions, many=True)
        return Response(serializer.data)


class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек - доступно без авторизации"""

    serializer_class = PublicHabitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)


class HabitCompletionViewSet(viewsets.ModelViewSet):
    """ViewSet для отслеживания выполнения привычек"""

    serializer_class = HabitCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Для Swagger возвращаем пустой queryset"""
        if getattr(self, 'swagger_fake_view', False):
            return HabitCompletion.objects.none()

        return HabitCompletion.objects.filter(habit__user=self.request.user)

    def perform_create(self, serializer):
        habit = serializer.validated_data['habit']
        if habit.user != self.request.user:
            raise permissions.PermissionDenied(
                'Вы можете отслеживать только свои привычки'
            )
        serializer.save()
