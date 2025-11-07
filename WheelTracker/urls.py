"""
URL configuration for WheelTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from Dashboard.auth_views import register, current_user
from Dashboard.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name='health_check'),
    path("api/auth/login/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path("api/auth/register/", register, name='register'),
    path("api/auth/user/", current_user, name='current_user'),
    path("", include("Dashboard.urls")),
    path("", include("CreditSpread.urls")),
]
