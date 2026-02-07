from django.contrib import admin
from django.urls import path, include  # ← добавьте include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # ← добавьте эту строку
]
