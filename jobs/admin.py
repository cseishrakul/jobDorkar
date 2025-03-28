from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'salary', 'location', 'created_at']
    search_fields = ['title', 'company']