from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'user_type']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        user.is_verified = False
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField(required=False)

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])  # Ensure 'username' field is used correctly
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials!")

        user = authenticate(username=data['username'], password=data['password'])  # Authenticate by username
        if not user:
            raise serializers.ValidationError("Invalid credentials!")

        if not user.is_verified:
            raise serializers.ValidationError("Email not verified!")

        if data.get('user_type') and data['user_type'] != user.user_type:
            raise serializers.ValidationError("User type mismatch!")

        return user