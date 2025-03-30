from django.contrib import admin
from .models import Job,JobApplication,JobCategory,Review

# Register your models here.
admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(JobCategory)
admin.site.register(Review)
