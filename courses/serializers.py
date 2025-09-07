from rest_framework import serializers
from . import models
from django.utils import timezone
from datetime import timedelta






class RoleSerializer(serializers.ModelSerializer):
    """Serializes the role model....the field names are like voter,citizen,polling admin, party agents....will later be used in the admin panel
    where it wil be used to categorize the courses """
    class Meta:
        model = models.Role
        fields = ['id', 'name', 'description']


class BadgeSerializer(serializers.ModelSerializer):
    """Defines the course module badge"""
    class Meta:
        model = models.Badge
        fields = ['id', 'name', 'description', 'module', 'icon']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Certificate
        fields = ['id', 'course', 'code', 'issued_date', 'file']



class UserBadgeSerializer(serializers.ModelSerializer):
    """serializes userbadge model which defines the badge a specific user gets/has"""
    badge = BadgeSerializer(read_only=True)
    badge_id = serializers.PrimaryKeyRelatedField(
        source='badge', queryset=models.Badge.objects.all(), write_only=True
    )

    class Meta:
        model = models.UserBadge
        fields = ['id', 'user', 'badge', 'badge_id', 'awarded_at']
        read_only_fields = ['awarded_at', 'user']

class AchievementSerializer(serializers.Serializer):
    total_points = serializers.IntegerField()
    badges_count = serializers.IntegerField()
    badges = BadgeSerializer(many=True, read_only=True)
    certificates_count = serializers.IntegerField()
    certificates = CertificateSerializer(many=True, read_only=True)
    lessons_completed = serializers.IntegerField()
    modules_completed = serializers.IntegerField()
    courses_enrolled = serializers.IntegerField()
    streak_days = serializers.IntegerField()


class AnswerSerializer(serializers.ModelSerializer):
    """for answer model basically...to be used in the admin panel"""
    class Meta:
        model = models.Answer
        fields = ['id', 'question', 'text', 'is_correct', 'order']

    def validate(self, data):
        """
        Ensure single-correct-answer when question.allow_multiple_answers is False.
        """
        question = data.get('question') or getattr(self.instance, 'question', None)
        is_correct = data.get('is_correct', getattr(self.instance, 'is_correct', False))
        
        if question and is_correct and not question.allow_multiple_answers:
            qs = models.Answer.objects.filter(question=question, is_correct=True)

            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "This question already has a correct answer "
                    "and multiple answers are not allowed."
                )
        return data


class QuestionSerializer(serializers.ModelSerializer):
    """serializes the Question model"""
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = models.Question
        fields = ['id', 'lesson', 'text', 'allow_multiple_answers', 'order', 'answers']


class LessonResourceSerializer(serializers.ModelSerializer):
    """For uploading lesson resource files like .txt,.pdf etc"""
    file = serializers.FileField(use_url=True)

    class Meta:
        model = models.LessonResource
        fields = ['id', 'lesson', 'file', 'description']




class LessonListSerializer(serializers.ModelSerializer):
    """Display list of the lessons available in a particular module"""
    resources = LessonResourceSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)
    completed=serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Lesson
        fields = [
            'id', 'module', 'title', 'slug', 'lesson_type', 'estimated_duration',
            'has_quiz', 'is_published', 'order', 'resources', 'questions_count', 'completed'
        ]




class LessonDetailSerializer(serializers.ModelSerializer):
    """detailed view of the lesson contents...caters also for the next lellosn button"""
    resources = LessonResourceSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    next_lesson = serializers.SerializerMethodField()

    class Meta:
        model = models.Lesson
        fields = [
            'id', 'module', 'title', 'slug', 'content_text', 'video_url', 'infographic',
            'lesson_type', 'estimated_duration', 'has_quiz', 'is_published', 'order',
            'resources', 'questions', 'next_lesson'
        ]

    def get_next_lesson(self, obj):
        next_l = obj.get_next_lesson()
        if not next_l:
            return None
        return LessonListSerializer(next_l, context=self.context).data



class ModuleListSerializer(serializers.ModelSerializer):
    completed_lessons = serializers.SerializerMethodField()
    lesson_count = serializers.IntegerField(read_only=True)  

    class Meta:
        model = models.Module
        fields = ['id', 'course', 'title', 'description', 'order', 'lesson_count', 'completed_lessons']

    def get_completed_lessons(self, obj):
        user = self.context['request'].user
        return models.LessonProgress.objects.filter(
            user=user,
            lesson__module=obj,
            completed=True
        ).count()

    

    


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Detailed view of the modules"""
    lessons = LessonListSerializer(many=True, read_only=True)
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = models.Module
        fields = ['id', 'course', 'title', 'description', 'order', 'lessons', 'badge']



class CourseListSerializer(serializers.ModelSerializer):
    """List all available course"""
    total_lessons = serializers.IntegerField(read_only=True)
    total_modules = serializers.IntegerField(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Course
        fields = ['id', 'title', 'slug', 'description', 'is_published','roles', 'created_by',
                  'created_at', 'updated_at', 'total_modules', 'total_lessons']

    


class CourseDetailSerializer(serializers.ModelSerializer):
    """Detailed view of the lessons"""
    modules = ModuleListSerializer(many=True, read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Course
        fields = [
            'id', 'title', 'slug', 'description', 'roles', 'is_published',
            'created_by', 'created_at', 'updated_at', 'modules'
        ]
        read_only_fields = ['slug']  



class CourseEnrollmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CourseEnrollment
        fields = ['id', 'user', 'course', 'enrolled_at', 'active']
        read_only_fields = ['id', 'user', 'course', 'enrolled_at']




class LessonProgressSerializer(serializers.ModelSerializer):
    answers = serializers.DictField(write_only=True)

    class Meta:
        model = models.LessonProgress
        fields = [
            'id', 'user', 'lesson', 'completed', 'score', 'points_awarded',
            'attempts', 'last_attempted', 'date_completed', 'answers'
        ]
        read_only_fields = [
            'user', 'completed', 'score', 'points_awarded',
            'attempts', 'last_attempted', 'date_completed'
        ]

    def update(self, instance, validated_data):
        raw_answers = validated_data.pop('answers', {}) or {}

   
        if not instance.can_attempt():
            if instance.last_attempted:
                unlock_time = instance.last_attempted + timedelta(hours=instance.COOLDOWN_HOURS)
            else:
                unlock_time = timezone.now() + timedelta(hours=instance.COOLDOWN_HOURS)

            seconds_remaining = max(0, int((unlock_time - timezone.now()).total_seconds()))
            instance._blocked = True
            instance._unlock_at = unlock_time
            instance._seconds_remaining = seconds_remaining
            instance._retry_allowed = False
            return instance

       
        score = 0
        questions = instance.lesson.questions.prefetch_related('answers').all()
        total_questions = questions.count()

        for q in questions:
            submitted = raw_answers.get(str(q.id)) if raw_answers.get(str(q.id)) is not None else raw_answers.get(q.id)

            if q.allow_multiple_answers:
                if submitted is None:
                    submitted_ids = []
                elif isinstance(submitted, list):
                    submitted_ids = [int(x) for x in submitted]
                else:
             
                    try:
                        submitted_ids = [int(submitted)]
                    except (TypeError, ValueError):
                        submitted_ids = []
                submitted_set = set(submitted_ids)
                correct_set = set(q.answers.filter(is_correct=True).values_list('id', flat=True))
             
                if correct_set and submitted_set == correct_set:
                    score += 1
            else:
                try:
                    submitted_id = int(submitted) if submitted is not None else None
                except (TypeError, ValueError):
                    submitted_id = None
                if submitted_id and q.answers.filter(id=submitted_id, is_correct=True).exists():
                    score += 1

        percentage = (score / total_questions) * 100 if total_questions else 0
        points = score  

        try:
            instance.mark_completed(score=score, points=points)
        except ValueError as e:
           
            if instance.last_attempted:
                unlock_time = instance.last_attempted + timedelta(hours=instance.COOLDOWN_HOURS)
            else:
                unlock_time = timezone.now() + timedelta(hours=instance.COOLDOWN_HOURS)
            seconds_remaining = max(0, int((unlock_time - timezone.now()).total_seconds()))
            instance._blocked = True
            instance._unlock_at = unlock_time
            instance._seconds_remaining = seconds_remaining
            instance._retry_allowed = False
            return instance

        instance._percentage = percentage
        instance._passed = (percentage >= 75)

        next_lesson = instance.lesson.get_next_lesson() if hasattr(instance.lesson, "get_next_lesson") else None
        if next_lesson:
            instance._next_lesson_id = next_lesson.id
            instance._next_lesson_title = next_lesson.title
        else:
            instance._next_lesson_id = None
            instance._next_lesson_title = None

        instance._retry_allowed = not instance._passed and instance.can_attempt()
      
        if not instance._retry_allowed and not instance._passed:
            if instance.last_attempted:
                unlock_time = instance.last_attempted + timedelta(hours=instance.COOLDOWN_HOURS)
            else:
                unlock_time = timezone.now() + timedelta(hours=instance.COOLDOWN_HOURS)
            instance._unlock_at = unlock_time
            instance._seconds_remaining = max(0, int((unlock_time - timezone.now()).total_seconds()))

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)

       
        rep['percentage'] = round(getattr(instance, '_percentage', 0), 2)
        rep['passed'] = getattr(instance, '_passed', False)
        rep['next_lesson_id'] = getattr(instance, '_next_lesson_id', None)
        rep['next_lesson_title'] = getattr(instance, '_next_lesson_title', None)
        rep['retry_allowed'] = getattr(instance, '_retry_allowed', False)

 
        if getattr(instance, '_blocked', False):
            rep['blocked'] = True
            rep['unlock_at'] = getattr(instance, '_unlock_at', None)
            rep['seconds_remaining'] = getattr(instance, '_seconds_remaining', 0)
        else:
            rep['blocked'] = False
            rep['unlock_at'] = getattr(instance, '_unlock_at', None)
            rep['seconds_remaining'] = getattr(instance, '_seconds_remaining', 0)

        return rep


class ModuleProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleProgress
        fields = ['id', 'user', 'modules', 'completed', 'date_completed']
        read_only_fields = ['date_completed']


class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseProgress
        fields = ['id', 'user', 'course', 'completed', 'date_completed', 'certificate_issued', 'certificate_code']
        read_only_fields = ['date_completed', 'certificate_code', 'certificate_issued']




class LearningActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LearningActivity
        fields = ['id', 'user', 'action', 'lesson', 'timestamp', 'metadata']
        read_only_fields = ['timestamp']


class UserEnrolledCourseSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source='course.id', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    modules = ModuleListSerializer(many=True, source='course.modules', read_only=True)

    class Meta:
        model = models.CourseEnrollment
        fields = ['course_id', 'course_title', 'enrolled_at', 'active', 'modules']
