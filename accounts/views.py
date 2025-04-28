from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .serializers import CustomUserDetailSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:  # Check if the user is a superadmin
            users = User.objects.all()
            return Response({"users": [user.username for user in users]})
        else:
            return Response({"error": "You are not authorized to view this page"}, status=403)
        



class UserDetailByIdView(generics.GenericAPIView):
    serializer_class = CustomUserDetailSerializer

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
