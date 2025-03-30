from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'role', 'is_staff', 'is_active', 'last_login')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        ("User Info", {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        ("Roles & Resume", {"fields": ("role", "resume")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        ("User Info", {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "resume", "is_staff", "is_active"),
        }),
    )

    search_fields = ("username", "email", "role")

    ordering = ("id",)

admin.site.register(User, CustomUserAdmin)
