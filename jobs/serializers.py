from rest_framework import serializers
from .models import Job,JobApplication,JobCategory,Review
from accounts.models import User
        
class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name']

class JobSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'requirements', 'location', 'category', 'category_name', 'date_posted', 'company_name', 'company_logo']



class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    employer = serializers.CharField(source='job.posted_by.username', read_only=True)
    resume = serializers.FileField(write_only=True, required=False) 
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'employer', 'resume', 'resume_url', 'cover_letter', 'status', 'applied_at']

    def get_resume_url(self, obj):
        """Return Cloudinary URL for resume."""
        return obj.resume.url if obj.resume else None

    def update(self, instance, validated_data):
        """Ensure only employers can update status."""
        user = self.context['request'].user
        if user.role != 'employer':
            raise serializers.ValidationError("Only employers can update the status.")
        
        instance.status = validated_data.get('status', instance.status)
        if 'resume' in validated_data:
            instance.resume = validated_data['resume']

        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "role", "resume"]
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'job_seeker', 'employer', 'job', 'rating', 'comment', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value