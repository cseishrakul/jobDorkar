from djoser.serializers import UserCreateSerializer,UserSerializer
from rest_framework import serializers
from .models import User
from jobs.models import Job
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model


User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('id', 'username', 'email', 'role','is_staff')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_staff": user.is_staff,
        }
        return data


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'requirements', 'location', 'posted_by', 'date_posted']
        read_only_fields = ['posted_by', 'date_posted']


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
