from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from .models import Job,JobApplication,JobCategory,Review
from accounts.models import User
from .serializers import JobSerializer,JobApplicationSerializer,UserProfileSerializer,JobCategorySerializer,ReviewSerializer
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.core.mail import send_mail
from django.conf import settings
import sslcommerz
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import time


class JobCategoryView(generics.ListCreateAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [AllowAny]

class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Job.objects.all()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class JobCreateView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        company_name = self.request.data.get('company_name', '')
        company_logo = self.request.FILES.get('company_logo', None)
        serializer.save(
            posted_by=self.request.user, 
            company_name=company_name, 
            company_logo=company_logo
        )


        
# Job Delete
class DeleteJob(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, posted_by=request.user)
            job.delete()
            return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response({"message": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        
#  Job Update
class JobUpdateView(UpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user:
            return Response({"detail": "You do not have permission to edit this job."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

class JobApplicationCreateView(generics.CreateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "job_seeker":
            raise PermissionDenied("Only job seekers can apply for jobs.")
        
        job_id = self.request.data.get("job")
        job = Job.objects.get(id=job_id)
        application = serializer.save(applicant=user, job=job)
        
        send_mail(
            subject="Job Application Confirmation",
            message=f"Dear {user.username},\n\nYou have successfully applied for the position of {job.title}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        send_mail(
            subject="New Job Application Received",
            message=f"Dear {job.posted_by.username},\n\nYou have received a new application for {job.title} from {user.username}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[job.posted_by.email],
            fail_silently=False,
        )

        return Response({"message": "Application submitted successfully."}, status=201)
    
class UpdateJobApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, application_id):
        user = request.user
        application = JobApplication.objects.get(id=application_id)
        if user.role != 'employer' or application.job.posted_by != user:
            raise PermissionDenied("Only the employer who posted the job can update the status.")
        new_status = request.data.get('status')
        application.status = new_status
        application.save()

        return Response({"message": "Application status updated successfully."}, status=status.HTTP_200_OK)

class EmployerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "employer":
            return Response({"error": "Access Denied. Only employers can access this dashboard."}, status=403)

        jobs = Job.objects.filter(posted_by=user)
        applications = JobApplication.objects.filter(job__in=jobs)

        job_serializer = JobSerializer(jobs, many=True)
        application_serializer = JobApplicationSerializer(applications, many=True)

        return Response({
            "posted_jobs": job_serializer.data,
            "received_applications": application_serializer.data,
        })


class JobSeekerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "job_seeker":
            return Response({"error": "Access Denied. Only job seekers can access this dashboard."}, status=403)

        applications = JobApplication.objects.filter(applicant=user)

        application_serializer = JobApplicationSerializer(applications, many=True)

        return Response({
            "applied_jobs": application_serializer.data
        })

class UpdateProfileView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class TrackApplicationsView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user)
    
class ApplyJobView(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        user = request.user
        if JobApplication.objects.filter(applicant=user, job=job).exists():
            return Response({"message": "You have already applied for this job."}, status=status.HTTP_400_BAD_REQUEST)

        application = JobApplication.objects.create(applicant=user, job=job)
        send_mail(
            subject="Job Application Confirmation",
            message=f"Dear {user.username},\n\nYou have successfully applied for {job.title}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        send_mail(
            subject="New Job Application Received",
            message=f"Dear {job.posted_by.username},\n\nYou have received a new application for {job.title}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[job.posted_by.email],
            fail_silently=False,
        )

        return Response({"message": "Application submitted successfully."}, status=status.HTTP_201_CREATED)


class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "job_seeker":
            raise PermissionDenied("Only job seekers can leave reviews.")
        
        job_id = self.request.data.get("job")
        try:
            job = Job.objects.get(id=job_id)
        except ObjectDoesNotExist:
            raise PermissionDenied("The job does not exist.")
        if job.posted_by != self.request.user:
            raise PermissionDenied("You cannot leave a review for a job that you did not apply for.")
        serializer.save(job_seeker=user, employer=job.posted_by, job=job)
        
class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        employer_id = self.kwargs['employer_id']
        return Review.objects.filter(employer_id=employer_id).order_by('-created_at')
    


# SSLCommercez
@login_required
def promote_job(request, job_id):
    # Assuming you have a Job model and it has is_promoted field
    job = Job.objects.get(id=job_id, employer=request.user)

    # Check if the job is already promoted
    if job.is_promoted:
        return JsonResponse({'message': 'This job is already promoted.'}, status=400)

    # Generate a unique transaction ID
    order_id = f"job_promotion_{job.id}_{int(time.time())}"

    # Payment data
    payment_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_password': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': 100,  # Set your promotion price
        'currency': 'BDT',
        'tran_id': order_id,
        'cus_name': request.user.username,
        'cus_email': request.user.email,
        'cus_phone': request.user.profile.phone,  # Assuming you have a phone field in user profile
        'success_url': f'{request.scheme}://{request.get_host()}/payment/success/{job.id}',
        'fail_url': f'{request.scheme}://{request.get_host()}/payment/fail/{job.id}',
        'cancel_url': f'{request.scheme}://{request.get_host()}/payment/cancel/{job.id}',
    }

    try:
        # Create SSLCommerz instance for sandbox
        ssl_commerz = sslcommerz.SSLCommerz(
            store_id=settings.SSLCOMMERZ_STORE_ID,
            store_password=settings.SSLCOMMERZ_STORE_PASSWORD,
            is_sandbox=True  # Sandbox environment for testing
        )
        
        # Send payment request
        response = ssl_commerz.payment_request(payment_data)

        # If response is successful, redirect to SSLCommerz payment page
        if response['status'] == 'SUCCESS':
            payment_url = response['GatewayPageURL']
            return HttpResponseRedirect(payment_url)

        return JsonResponse({'error': 'Payment initiation failed.'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    


def payment_success(request, job_id):
    # Handle success logic (e.g., mark job as promoted)
    job = Job.objects.get(id=job_id)
    job.is_promoted = True
    job.save()
    return render(request, 'payment/success.html', {'job': job})

def payment_fail(request, job_id):
    # Handle failure logic
    job = Job.objects.get(id=job_id)
    return render(request, 'payment/fail.html', {'job': job})

def payment_cancel(request, job_id):
    # Handle cancellation
    job = Job.objects.get(id=job_id)
    return render(request, 'payment/cancel.html', {'job': job})
