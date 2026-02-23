from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .serializers_token import CustomTokenObtainPairView
from .views import UserRegistrationView, UserProfileView, TelegramConnectView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('telegram/connect/', TelegramConnectView.as_view(), name='telegram-connect'),
]