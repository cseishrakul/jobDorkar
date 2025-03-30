from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    EMPLOYER = 'employer'
    JOB_SEEKER = 'job_seeker'
    
    ROLE_CHOICES = [
        (EMPLOYER, 'Employer'),
        (JOB_SEEKER, 'Job Seeker'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=JOB_SEEKER)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True) 
    
    def __str__(self):
        return self.username
    


