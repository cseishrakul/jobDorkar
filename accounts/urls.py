from django.urls import path
from .views import UserRegisterView,verify_email,LoginView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
     path('verify/<str:token>/', verify_email, name='verify-email'),
     path('login/', LoginView.as_view(), name='login'),
]
