from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import HttpResponse

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
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('login')  # Redirect to the login page after activation
        else:
            return HttpResponse('Invalid activation link.', status=400)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)
