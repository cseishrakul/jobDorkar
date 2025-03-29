from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    EMPLOYER = 'employer'
    JOB_SEEKER = 'job_seeker'
    
    ROLE_CHOICES = [
        (EMPLOYER, 'Employer'),
        (JOB_SEEKER, 'Job Seeker'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def generate_verification_token(self):
        self.email_verification_token = str(uuid.uuid4())
        self.token_created_at = timezone.now()
        self.save()
        return self.email_verification_token
    
    def is_token_valid(self, token):
        return (self.email_verification_token == token and 
                (timezone.now() - self.token_created_at).days < 1)