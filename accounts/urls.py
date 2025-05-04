from django.urls import path, include
from .views import CustomTokenObtainPairView ,AdminDashboardView,UserDetailByIdView

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/create', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('user/<int:user_id>/', UserDetailByIdView.as_view(), name='user-detail-by-id'),
]
    