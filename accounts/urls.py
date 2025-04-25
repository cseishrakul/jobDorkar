from django.urls import path, include
from .views import CustomTokenObtainPairView 

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/create', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
    