from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitListView

router = DefaultRouter()
router.register(r'my', HabitViewSet, basename='my-habits')

urlpatterns = [
    path('', include(router.urls)),
    path('public/', PublicHabitListView.as_view(), name='public-habits'),
]