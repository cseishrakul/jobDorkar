from django.urls import path, include
from .views import CustomTokenObtainPairView ,AdminDashboardView,UserDetailByIdView
# from .views import ActivateUserView


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/create', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    # path('activate/<uid>/<token>/', ActivateUserView.as_view(), name='activate_user'),
    path('user/<int:user_id>/', UserDetailByIdView.as_view(), name='user-detail-by-id'),


]
    