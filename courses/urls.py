
from django.urls import path
from . import views

urlpatterns = [

    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('my-courses/', views.UserEnrolledCoursesView.as_view(), name='my-courses'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/enroll/', views.CourseEnrollmentView.as_view(), name='course-enroll'),
    path('courses/<int:course_id>/modules/', views.ModuleListView.as_view(), name='module-list'),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module-detail'),
    path('modules/<int:module_id>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('lesson-progress/<int:pk>/', views.LessonProgressUpdateView.as_view(), name='lesson-progress-update'),
    path('lesson-progress/by-lesson/<int:lesson_id>/',views.LessonProgressByLessonView.as_view(),name='lesson-progress-by-lesson'),
    path('lesson-progress/submit/', views.LessonProgressSubmitView.as_view()),
    path("achievements/", views.AchievementView.as_view(), name="achievements"),
]
