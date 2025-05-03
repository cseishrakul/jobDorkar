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
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from sslcommerz_lib import SSLCOMMERZ 

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
@api_view(['POST'])
def initiate_payment(request):
    settings = { 'store_id': 'jobdo68162c3a4bfb4', 'store_pass': 'jobdo68162c3a4bfb4@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = 100.26
    post_body['currency'] = "BDT"
    post_body['tran_id'] = "12345"
    post_body['success_url'] = "your success url"
    post_body['fail_url'] = "your fail url"
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = "test"
    post_body['cus_email'] = "test@test.com"
    post_body['cus_phone'] = "01700000000"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body) # API response
    print(response)
    
    if response.get('status') == 'SUCCESS':
        return Response({"payment_url": response['GatewayPageURL']})
    return Response({"error":"Payment initiation failed"},status=status.HTTP_400_BAD_REQUEST)