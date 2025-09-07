from django.shortcuts import render,get_object_or_404
from django.db.models import Count, Prefetch,OuterRef,Exists,Sum
from django.utils.timezone import localdate, timedelta

from rest_framework import generics, permissions,status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response






from . import models, serializers

# Create your views here.

class CourseListView(generics.ListAPIView):
    """Lists all courses...also their module count and number of lessons"""

    serializer_class=serializers.CourseListSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            models.Course.objects.filter(is_published=True)
            .annotate(total_modules=Count('modules', distinct=True),total_lessons=Count('modules__lessons',distinct=True))
            .select_related('created_by')
            .prefetch_related('roles', Prefetch('modules',queryset=models.Module.objects.only('id','course','order')))
            .order_by('created_at')
           
        )
    

class CourseDetailView(generics.RetrieveAPIView):
    """Retrieves a single sourse with a list of its module and also lesson counts"""

    serializer_class=serializers.CourseDetailSerializer
    permission_classes=[permissions.IsAuthenticated]


    def get_queryset(self):
        return(
            models.Course.objects.filter(is_published=True).select_related('created_by').prefetch_related(
                'roles', Prefetch('modules', queryset=(
                    models.Module.objects.annotate(lesson_count=Count('lessons')).order_by('order')
                    .only('id','course_id','title','order')
                ))
            )
        )
    


class CourseEnrollmentView(generics.CreateAPIView):
    """For enrolling users to a course"""
    serializer_class = serializers.CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course = get_object_or_404(models.Course, pk=course_id)

        # Check if user is already enrolled
        if models.CourseEnrollment.objects.filter(user=request.user, course=course).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data={})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, course=course)

        return Response(
            {"detail": "Enrollment successful!", "course_id": course.id},
            status=status.HTTP_201_CREATED
        )



class ModuleListView(generics.ListAPIView):
    """listing modules within a oarticular course"""
    serializer_class=serializers.ModuleListSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        course_id=self.kwargs.get('course_id')
        return (
            models.Module.objects.filter(course_id=course_id).select_related('course')
            .annotate(lesson_count=Count('lessons',distinct=True))
            .only('id','title','order','course_id').order_by('order')
        )


class ModuleDetailView(generics.RetrieveAPIView):
    """retrieves  a single module"""

    serializer_class=serializers.ModuleDetailSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            models.Module.objects.select_related('course', 'badge')
            .prefetch_related(Prefetch('lessons', queryset=(
                models.Lesson.objects.annotate(questions_count=Count('questions', distinct=True))
                .only('id','title','order','module_id')
                .order_by('order')
            )))
        )
    




class LessonListView(generics.ListAPIView):
    """List all lessons within a module"""
    serializer_class = serializers.LessonListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        user = self.request.user

        # Subquery to check if this user has a completed progress for that lesson
        progress_qs = models.LessonProgress.objects.filter(
            user=user,
            lesson=OuterRef('pk'),
            completed=True
        )

        qs = (
            models.Lesson.objects
            .filter(module_id=module_id)
            .annotate(
                question_count=Count('questions', distinct=True),
                completed=Exists(progress_qs)
            )
            .order_by('order')
        )
        return qs


class LessonDetailView(generics.RetrieveAPIView):
    """retrieves single lesson with some conditions"""
    serializer_class = serializers.LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson = super().get_object()
        user = self.request.user

        # If the user already completed this lesson, allow viewing (review).
        completed = models.LessonProgress.objects.filter(
            user=user, lesson=lesson, completed=True
        ).exists()

        # If not completed, enforce prerequisite: previous lesson must be completed
        if not completed:
            previous_lessons = (
                models.Lesson.objects
                .filter(module=lesson.module, order__lt=lesson.order)
                .order_by('-order')
            )
            if previous_lessons.exists():
                last_prev = previous_lessons.first()
                prev_completed = models.LessonProgress.objects.filter(
                    user=user, lesson=last_prev, completed=True
                ).exists()
                if not prev_completed:
                    raise PermissionDenied("You must complete the previous lesson before accessing this one.")

        # If completed or previous completed -> allow
        return lesson
    
    def get_queryset(self):
        return (
            models.Lesson.objects.select_related('module')
            .prefetch_related(
                'resources',
                Prefetch(
                    'questions',queryset=models.Question.objects.prefetch_related('answers')
                )
            )
        )



class UserEnrolledCoursesView(generics.ListAPIView):
    serializer_class = serializers.UserEnrolledCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return models.CourseEnrollment.objects.filter(user=user, active=True)\
            .select_related('course')\
            .prefetch_related('course__modules__lessons')
    



class LessonProgressSubmitView(generics.UpdateAPIView):
    serializer_class = serializers.LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson_id = self.request.data.get('lesson_id')
        if not lesson_id:
            raise serializers.ValidationError("lesson_id is required.")
        progress, _ = models.LessonProgress.objects.get_or_create(
            user=self.request.user,
            lesson_id=lesson_id
        )
        return progress


class LessonProgressByLessonView(generics.RetrieveAPIView):
    serializer_class = serializers.LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson_id = self.kwargs['lesson_id']
        # Auto-create progress record for first-time quiz takers
        progress, created = models.LessonProgress.objects.get_or_create(
            user=self.request.user,
            lesson_id=lesson_id
        )
        return progress

class LessonProgressUpdateView(generics.UpdateAPIView):
    serializer_class = serializers.LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lesson_progress_id = self.kwargs.get('pk')
        lesson_id = self.request.data.get('lesson_id')

        if lesson_progress_id and lesson_progress_id != "null":
            # Try fetching by ID
            return models.LessonProgress.objects.get(
                id=lesson_progress_id,
                user=self.request.user
            )

        if lesson_id:
            # Auto-create progress if only lesson_id is given
            progress, _ = models.LessonProgress.objects.get_or_create(
                user=self.request.user,
                lesson_id=lesson_id
            )
            return progress

        raise serializers.ValidationError("Lesson ID is required if progress ID is null.")

    def get_queryset(self):
        return models.LessonProgress.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        progress = serializer.instance
        user = self.request.user

        # Check if previous lesson is completed
        previous_lessons = (
            models.Lesson.objects
            .filter(module=progress.lesson.module, order__lt=progress.lesson.order)
            .order_by('-order')
        )
        if previous_lessons.exists():
            last_prev = previous_lessons.first()
            prev_completed = models.LessonProgress.objects.filter(
                user=user, lesson=last_prev, completed=True
            ).exists()
            if not prev_completed:
                raise PermissionDenied("You must complete the previous lesson first.")

        serializer.save()






class AchievementView(generics.GenericAPIView):
    serializer_class = serializers.AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        total_points = models.LessonProgress.objects.filter(
            user=user
        ).aggregate(points=Sum("points_awarded"))["points"] or 0

      
        user_badges = models.UserBadge.objects.filter(user=user).select_related("badge")
        badges_data = serializers.UserBadgeSerializer(user_badges, many=True).data
      


        certificates = models.Certificate.objects.filter(user=user).select_related("course")
        certificates_data = serializers.CertificateSerializer(certificates, many=True).data


        lessons_completed = models.LessonProgress.objects.filter(
            user=user, completed=True
        ).count()


        modules_completed = models.ModuleProgress.objects.filter(
            user=user, completed=True
        ).count()

      

        courses_enrolled = models.CourseEnrollment.objects.filter(
            user=user, active=True
        ).count()

 
        days = models.LearningActivity.objects.filter(
            user=user
        ).values_list("timestamp", flat=True)

        active_days = {ts.date() for ts in days}
     
        streak_days = 0
        if active_days:
            today = localdate()
            while today in active_days:
                streak_days += 1
                today -= timedelta(days=1)

        courses_data = []
        enrollments = models.CourseEnrollment.objects.filter(user=user, active=True).select_related("course")

        for enrollment in enrollments:
            course = enrollment.course
            total_modules = course.modules.count()  
            completed_modules = models.ModuleProgress.objects.filter(
                user=user, module__course=course, completed=True
            ).count()

            courses_data.append({
                "course_name": course.title,
                "modules_total": total_modules,
                "modules_completed": completed_modules,
            })


        data = {
            "total_points": total_points,
            "badges_count": user_badges.count(),
            "badges": badges_data,
            "certificates_count": certificates.count(),
            "certificates": certificates_data,
            "lessons_completed": lessons_completed,
            "modules_completed": modules_completed,
            "courses_enrolled": courses_enrolled,
            "streak_days": streak_days,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
