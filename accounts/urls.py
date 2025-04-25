from django.urls import path, include
from .views import CustomTokenObtainPairView 
from .views import AdminDashboardView

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/create', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
]
    