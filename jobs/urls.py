from django.urls import path, include
from .views import JobCreateView,JobApplicationCreateView,JobListView,EmployerDashboardView, JobSeekerDashboardView,UpdateProfileView,TrackApplicationsView,JobCategoryView,UpdateJobApplicationStatusView,ReviewCreateView,ReviewListView,DeleteJob,JobUpdateView,initiate_payment,payment_success,payment_cancel,payment_failed

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('api/jobs/delete/<int:job_id>/', DeleteJob.as_view(), name='delete-job'),
    path('api/jobs/update/<int:pk>/', JobUpdateView.as_view(), name='job-update'),
    path("dashboard/employer/", EmployerDashboardView.as_view(), name="employer-dashboard"),
    path("dashboard/jobseeker/", JobSeekerDashboardView.as_view(), name="jobseeker-dashboard"),
    path("dashboard/profile/update/", UpdateProfileView.as_view(), name="update-profile"),
    path('applications-track/', TrackApplicationsView.as_view(), name='track-applications'),
    path('categories/', JobCategoryView.as_view(), name='job-categories'),
    
    path('applications/', JobApplicationCreateView.as_view(), name='create-application'),
    path('applications/<int:application_id>/update-status/', UpdateJobApplicationStatusView.as_view(), name='update-application-status'),
    
    path('reviews/', ReviewCreateView.as_view(), name='create-review'),
    path('reviews/<int:employer_id>/', ReviewListView.as_view(), name='list-reviews'),
    
    # Payment
    path("payment/initiate/",initiate_payment,name="initiate-payment"),
    path("payment/success/", payment_success,name="payment-success"),
    path("payment/cancel/", payment_cancel,name="payment-cancel"),
    path("payment/failed/", payment_failed,name="payment-failed")
]