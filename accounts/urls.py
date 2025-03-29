from django.urls import path
from .views import (
    UserRegistrationAPIView,
    VerifyEmailAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserProfileAPIView
)

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('verify-email/<str:token>/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
]