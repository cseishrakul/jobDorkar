from django.urls import path, include
from .views import CustomTokenObtainPairView 
from .views import AdminDashboardView
# from .views import ActivateUserView


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/create', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    # path('activate/<uid>/<token>/', ActivateUserView.as_view(), name='activate_user'),


]
    