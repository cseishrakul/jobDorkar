from django.urls import path, include
from .views import CustomTokenObtainPairView 
from .views import AdminDashboardView
from .views import activate_account


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/create', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    # path('activate/<str:uidb64>/<str:token>/', activate_account, name='activate_account'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),


]
    