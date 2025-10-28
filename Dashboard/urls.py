from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PositionViewSet

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')

urlpatterns = [
    path('api/', include(router.urls)),
]
