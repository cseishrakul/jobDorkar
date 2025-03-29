from rest_framework import viewsets, permissions,generics,status,serializers
from .models import Job, JobApplication,Resume,Job, JobCategory
from .serializers import JobSerializer, JobApplicationSerializer,JobCategorySerializer,ResumeSerializer,JobApplicationStatusSerializer,ReviewSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from .models import Review



class UserRegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if get_user_model().objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_user_model().objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()

            return Response({"message": "User registered. Verification email sent."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def perform_create(self, serializer):
        job_application = serializer.save(user=self.request.user)
        subject = "Application Received"
        message = f"Dear {job_application.user.username},\n\nYou have successfully applied for the job '{job_application.job.title}'. Good luck with your application!"
        recipient_list = [job_application.user.email]
        if job_application.user.email:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

        employer_email = job_application.job.company_email
        if employer_email:
            try:
                subject = "New Job Application"
                message = f"Dear Employer,\n\nYou have received a new application for the job '{job_application.job.title}' from {job_application.user.username}. Please review the application."
                send_mail(subject, message, settings.EMAIL_HOST_USER, [employer_email])
            except Exception as e:
                print(f"Failed to send email to employer: {e}")

class EmployerJobListView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EmployerJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        job = get_object_or_404(Job, pk=self.kwargs['pk'], user=self.request.user)
        return job


class JobApplicationListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        job = get_object_or_404(Job, pk=self.kwargs['job_id'], user=self.request.user)
        return JobApplication.objects.filter(job=job)
    

class JobSeekerJobApplicationListView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)


class JobSeekerResumeView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class JobCategoryListView(generics.ListCreateAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer

class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = Job.objects.all()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        return queryset
    
class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        existing_resume = Resume.objects.filter(user=request.user).first()
        if existing_resume:
            return Response({"error": "You have already uploaded a resume."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        resume = self.get_object()
        resume.resume_file.delete()
        resume.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class JobApplicationStatusListView(generics.ListAPIView):
    serializer_class = JobApplicationStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

class JobApplicationStatusUpdateView(APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            application = JobApplication.objects.get(pk=pk)
            status = request.data.get("status")
            if status not in ['pending', 'reviewed', 'accepted', 'rejected']:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            application.status = status
            application.save()

            return Response({"message": "Application status updated successfully"}, status=status.HTTP_200_OK)

        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.none()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.select_related('job_seeker', 'employer')
        employer_id = self.request.query_params.get('employer')
        if employer_id:
            queryset = queryset.filter(employer_id=employer_id)
        return queryset

    def perform_create(self, serializer):
        job_seeker = serializer.validated_data.get('job_seeker')
        employer = serializer.validated_data.get('employer')

        if job_seeker == employer:
            raise serializers.ValidationError("You cannot review yourself.")

        serializer.save()

