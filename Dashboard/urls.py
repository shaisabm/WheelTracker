from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PositionViewSet, FeedbackViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('api/', include(router.urls)),
]
