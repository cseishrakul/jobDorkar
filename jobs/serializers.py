from rest_framework import serializers
from .models import Job, JobApplication,Resume,JobCategory,Review
from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name']

class JobSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(), many=True)
    class Meta:
        model = Job
        fields = '__all__'

class JobApplicationSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        
        
class JobSeekerResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']

class EmployerJobApplicationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    resume = serializers.FileField()

    class Meta:
        model = JobApplication
        fields = ['user', 'resume', 'cover_letter', 'applied_at']


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'resume_file', 'cover_letter', 'updated_at', 'user']
        read_only_fields = ['id', 'updated_at', 'user']
        
    def validate_resume_file(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 5MB.")
        if not value.name.endswith(('.pdf', '.doc', '.docx')):
            raise serializers.ValidationError("Only .pdf, .doc, .docx files are allowed.")
        return value
    
class JobApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['id', 'status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'job_seeker', 'employer', 'rating', 'comment', 'created_at']