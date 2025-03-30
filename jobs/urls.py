from django.urls import path, include
from .views import JobCreateView,JobApplicationCreateView,JobListView,EmployerDashboardView, JobSeekerDashboardView,UpdateProfileView,TrackApplicationsView,JobCategoryView,UpdateJobApplicationStatusView,ReviewCreateView,ReviewListView

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    # path("<int:pk>/apply/", JobApplicationCreateView.as_view(), name="job-apply"),
    path("dashboard/employer/", EmployerDashboardView.as_view(), name="employer-dashboard"),
    path("dashboard/jobseeker/", JobSeekerDashboardView.as_view(), name="jobseeker-dashboard"),
    path("dashboard/profile/update/", UpdateProfileView.as_view(), name="update-profile"),
    path('applications-track/', TrackApplicationsView.as_view(), name='track-applications'),
    path('categories/', JobCategoryView.as_view(), name='job-categories'),
    
    path('applications/', JobApplicationCreateView.as_view(), name='create-application'),
    path('applications/<int:application_id>/update-status/', UpdateJobApplicationStatusView.as_view(), name='update-application-status'),
    
    path('reviews/', ReviewCreateView.as_view(), name='create-review'),
    path('reviews/<int:employer_id>/', ReviewListView.as_view(), name='list-reviews'),
]