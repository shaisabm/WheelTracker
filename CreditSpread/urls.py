from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditSpreadViewSet

router = DefaultRouter()
router.register(r'credit-spreads', CreditSpreadViewSet, basename='creditspread')

urlpatterns = [
    path('api/', include(router.urls)),
]