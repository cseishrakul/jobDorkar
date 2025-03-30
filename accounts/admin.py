from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

admin.site.register(User, CustomUserAdmin)
