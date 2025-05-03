from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer,UserSerializer, JobSerializer, JobCategorySerializer, JobApplicationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .serializers import CustomUserDetailSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Job, JobCategory, JobApplication


User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:  # Only for superadmin
            users = User.objects.all()
            jobs = Job.objects.all()
            categories = JobCategory.objects.all()
            applications = JobApplication.objects.all()

            users_data = UserSerializer(users, many=True).data
            jobs_data = JobSerializer(jobs, many=True).data
            categories_data = JobCategorySerializer(categories, many=True).data
            applications_data = JobApplicationSerializer(applications, many=True).data

            return Response({
                "users": users_data,
                "jobs": jobs_data,
                "categories": categories_data,
                "applications": applications_data
            })
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
