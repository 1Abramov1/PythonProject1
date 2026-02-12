from django.urls import path, include

urlpatterns = [
    path('habits/', include('habits.urls')),
    path('users/', include('users.urls')),
]