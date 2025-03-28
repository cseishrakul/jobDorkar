from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, JobApplicationViewSet, EmployerJobListView, EmployerJobDetailView, JobApplicationListView, JobSeekerJobApplicationListView, JobListView,JobCategoryListView,ResumeViewSet,JobApplicationStatusListView,JobApplicationStatusUpdateView,ReviewViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet)
router.register('applications', JobApplicationViewSet)
router.register('resumes', ResumeViewSet, basename='resume')
router.register('reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('employer/jobs/', EmployerJobListView.as_view(), name='employer-job-list'),
    path('employer/jobs/<int:pk>/', EmployerJobDetailView.as_view(), name='employer-job-detail'),
    path('employer/jobs/<int:job_id>/applications/', JobApplicationListView.as_view(), name='employer-job-applications'),
    path('job-seeker/applications/', JobSeekerJobApplicationListView.as_view(), name='job-seeker-job-applications'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('categories/', JobCategoryListView.as_view(), name='category-list'),
    path('job-seeker/application-status/', JobApplicationStatusListView.as_view(), name='job-seeker-application-status'),
    path('employer/application-status/<int:pk>/', JobApplicationStatusUpdateView.as_view(), name='employer-application-status-update'),

]
