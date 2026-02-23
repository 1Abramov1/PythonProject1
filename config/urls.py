from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка Swagger с Bearer авторизацией
schema_view = get_schema_view(
    openapi.Info(
        title="Habit Tracker API",
        default_version='v1',
        description="API для трекера привычек",
        contact=openapi.Contact(email="contact@habits.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],  # Убираем базовую аутентификацию из сваггера
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger с Bearer токеном
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)