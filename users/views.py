from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Профиль текущего пользователя"""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class TelegramConnectView(APIView):
    """Привязка Telegram аккаунта"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Привязать Telegram аккаунт"""
        profile = request.user.profile
        telegram_chat_id = request.data.get('telegram_chat_id')
        telegram_username = request.data.get('telegram_username')

        if not telegram_chat_id:
            return Response({
                'status': 'error',
                'message': 'telegram_chat_id обязателен'
            }, status=status.HTTP_400_BAD_REQUEST)

        profile.telegram_chat_id = telegram_chat_id
        if telegram_username:
            profile.telegram_username = telegram_username
        profile.notifications_enabled = True
        profile.save()

        return Response({
            'status': 'success',
            'message': 'Telegram аккаунт привязан',
            'telegram_chat_id': profile.telegram_chat_id,
            'telegram_username': profile.telegram_username
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        """Отвязать Telegram аккаунт"""
        profile = request.user.profile
        profile.telegram_chat_id = None
        profile.telegram_username = None
        profile.notifications_enabled = False
        profile.save()

        return Response({
            'status': 'success',
            'message': 'Telegram аккаунт отвязан'
        }, status=status.HTTP_200_OK)
