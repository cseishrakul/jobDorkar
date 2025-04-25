from djoser.serializers import UserCreateSerializer,UserSerializer
from rest_framework import serializers
from .models import User
from jobs.models import Job
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
            "is_staff": user.is_staff
        }
        return data


        

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'requirements', 'location', 'posted_by', 'date_posted']
        read_only_fields = ['posted_by', 'date_posted']



# Email activation
# class CustomActivationEmailSerializer(DjoserSerializers.UserCreateSerializer):
#     def get_activation_url(self, user, request):
#         """
#         Get full activation URL including the scheme (http or https) and domain.
#         """
#         domain = get_current_site(request).domain
#         protocol = 'https' if request.is_secure() else 'http'
#         uid = urlsafe_base64_encode(str(user.pk).encode()).decode()
#         token = default_token_generator.make_token(user)

#         return f"{protocol}://{domain}/activate/{uid}/{token}/"