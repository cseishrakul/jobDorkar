from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
import requests
from django.shortcuts import redirect
from django.views import View


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


# Custom email varification
class ActivateUserView(View):
    def get(self, request, uid, token):
        backend_url = 'https://job-dorkar.vercel.app/auth/users/activation/'
        response = requests.post(backend_url, json={'uid': uid, 'token': token})

        if response.status_code == 204:
            # Activation successful
            return redirect('https://localhost:5173/login')
        else:
            # Activation failed
            return redirect('https://localhost:5173/activation-failed')
