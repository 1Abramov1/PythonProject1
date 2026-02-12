from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавляем кастомные claims
        token['username'] = user.username
        token['email'] = user.email

        return token

    def validate(self, attrs):
        # Принудительно преобразуем в строки
        attrs['username'] = str(attrs.get('username', ''))
        attrs['password'] = str(attrs.get('password', ''))

        try:
            data = super().validate(attrs)
            return data
        except Exception as e:
            raise serializers.ValidationError(
                {'detail': 'Неверное имя пользователя или пароль'}
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer