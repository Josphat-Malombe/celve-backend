from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from datetime import timedelta
import uuid


# Create your models here.

User = get_user_model()

def validate_file_type(file):
    allowed = ['.pdf','.txt','.docx','.pptx']
    if not any(file.name.endswith(ext) for ext in allowed):
        raise ValidationError("Unsupported file type. Allowed: PDF, TXT,DOCX,PPTX.")


class Role(models.Model):
    """
    basically to define the users role which can be voter,polling station managers,laders,party agents ,citizens
    """
    name = models.CharField(max_length=50, unique=True)  
    description = models.TextField(blank=True,help_text="explain what the role is all about")

    def __str__(self):
        return self.name


# model we are using for the lms Course-->Modules-->lessons

class Course(models.Model):
    """
    defines a particular course
    got also some functions total_lessons, total_modules,
    slug is generated from title if its available
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True,help_text="Describe the course.")
    roles = models.ManyToManyField(Role, blank=True, related_name='courses') 
    is_published = models.BooleanField(default=False)
    is_free=models.BooleanField(default=True)
    price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug'])
            
        ]
    

    def save(self, *args, **kargs):
        """
        generates slug if not provided using the title
        """
        if not self.slug:
            self.slug=slugify(self.title)

        super(Course,self).save(*args, **kargs)

    def __str__(self):
        return self.title

    def total_lessons(self):
        """calculate tu the total lessons found in a particula module in this particular course"""
        return Lesson.objects.filter(module__course=self).count()

    def total_modules(self):
        return self.modules.count()


class Module(models.Model):
    """
    module -defines just the subsection within courses like module1 module2
    """
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    def lesson_count(self):
        """
        number of lessons in this module
        """
        return self.lessons.count()

    def all_lessons(self):
        """
        lessons in this module
        """
        return self.lessons.order_by('order')


class Lesson(models.Model):


    """
    the smallest particle now(atom)  model is for the lesson which will have two pages....one for the content and another for the quiz
    the content include a reading section, a video section and also an infographic section
    """
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('reading', 'Reading'),
        ('infographic', 'infographic'),
        ('quiz', 'Quiz'),
        
    ]

    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255,db_index=True)
    slug = models.SlugField(max_length=255)
    content_text = models.TextField(blank=True, help_text="HTML or Markdown content")
    video_url = models.URLField(blank=True, null=True)
    infographic = models.ImageField(upload_to='infographics/', blank=True, null=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='reading')
    estimated_duration = models.DurationField(null=True, blank=True)  # e.g., 00:05:00
    has_quiz = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('module', 'order')

    def __str__(self):
        return f"{self.module.course.title} / {self.module.title} / {self.title}"

    def get_next_lesson(self):

        """This function is for getting next lesson in higher order if its available, if not in that modules it
          checks the next module in higher order and shows first lesson"""
        
        next_lesson = Lesson.objects.filter(module=self.module, order__gt=self.order).order_by('order').first()
        if next_lesson:
            return next_lesson
        next_module = Module.objects.filter(course=self.module.course, order__gt=self.module.order).order_by('order').first()
        if next_module:
            return next_module.lessons.order_by('order').first()
        return None


class LessonResource(models.Model):

    """Represents a resource file (PDF, TXT, etc.) attached to a lesson."""
        

    lesson = models.ForeignKey(Lesson, related_name='resources', on_delete=models.CASCADE)
    file = models.FileField(upload_to='lesson_resources/',validators=[validate_file_type])
    description = models.CharField(max_length=255, blank=True)

    

    def __str__(self):
        return f"{self.file.name} ({self.lesson.title})"






#Question and answerss

class Question(models.Model):
    """
    question model which is for questions also you can tick to allow for multiple answers
    """
    lesson = models.ForeignKey(Lesson, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    allow_multiple_answers = models.BooleanField(default=False)  # supports multi-correct
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        constraints = [
                models.UniqueConstraint(fields=['lesson', 'order'], name='unique_question_order_per_lesson')
               ]

       

    def __str__(self):
        return f"Q: {self.text[:60]}..."

    def correct_answers(self):
        return self.answers.filter(is_correct=True)


class Answer(models.Model):
    """
    model for answers to the questions
    """
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['question','order'], name="unique_answer_order_per_question")
        ]

    def clean(self):
        if not self.is_correct and not self.question.answers.exclude(id=self.id).filter(is_correct=True).exists():
            raise ValidationError("Each question must have atleast one correct answer")

    def __str__(self):
        return self.text







#  Enrollment / Progress / Points 

class CourseEnrollment(models.Model):
    """
    Link model for a user and a course
    active=true gives access to user the course materials
    """
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        """Ensure no duplicate reregistration of same course"""
        unique_together = ('user', 'course')


class LessonProgress(models.Model):
    user = models.ForeignKey(User, related_name='lesson_progresses', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='progresses', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.PositiveSmallIntegerField(default=0)
    points_awarded = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    last_attempted = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    MAX_ATTEMPTS = 3
    COOLDOWN_HOURS = 12

    class Meta:
        unique_together = ('user', 'lesson')

    def can_attempt(self):
        """conditions for attempting a quiz.....not have exceeded the maximum attempts and if exceeded
        quiz is unlocked after 12 hours from the attempt"""
        if self.attempts < self.MAX_ATTEMPTS:
            return True
        
        if self.last_attempted:
            unlock_time = self.last_attempted + timedelta(hours=self.COOLDOWN_HOURS)
            return timezone.now() >= unlock_time
        
        return True

    def mark_completed(self, score, points):
        """tracks progress invoving score from quiz, points"""
        if not self.can_attempt():
            raise ValueError("Max attempts reached. Please try Again later. ")
        
        

        self.score = score
        self.points_awarded = points
        self.attempts += 1
        self.last_attempted = timezone.now()

        total=self.lesson.questions.count() or 1
        percentage=(score/total)*100

        if percentage >= 75:  
            self.completed = True
            self.date_completed = timezone.now()
        self.save()


class ModuleProgress(models.Model):
    """progress within the module"""

    user = models.ForeignKey(User, related_name='module_progresses', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, related_name='progresses', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'module')

        constraints = [
            models.UniqueConstraint(fields=['user','module'],name="unique_user_module_progress")
        ]


    def check_mark_completed(self):
        """checks if all lessons in that particular module are complete"""

        if self.completed:
            return
        total_lessons = self.module.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__module=self.module,
            completed=True
           ).count()

        if total_lessons == completed_lessons and total_lessons > 0:
           self.mark_completed()


    def mark_completed(self):
        """marks if a module is complete"""
        self.completed=True
        self.date_completed=timezone.now()
        self.save()


   

class CourseProgress(models.Model):
    """Tracks user's overall progress in a course"""

    user = models.ForeignKey(User, related_name='course_progresses', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='progresses', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_code = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course')

        constraints = [
              models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_progress')
                    ]


    def check_and_mark_completed(self):
        """Check if all modules in this course are complete"""

        if self.completed:
            return

        total_modules = self.course.modules.count()
        completed_modules = ModuleProgress.objects.filter(
            user=self.user,
            module__course=self.course,
            completed=True
        ).count()

        if total_modules == completed_modules and total_modules > 0:
            self.mark_completed_and_issue_certificate()

    def mark_completed_and_issue_certificate(self):
        """Mark course as completed and issue certificate"""
        self.completed = True
        self.date_completed = timezone.now()
        if not self.certificate_code:
            self.certificate_code = uuid.uuid4().hex
        self.certificate_issued = True
        self.save()





# badges and certificates



class Badge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module = models.OneToOneField(Module, related_name='badge', on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='badge/', null=True, blank=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, related_name='badges', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, related_name='awarded', on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} → {self.badge.name}"




class LearningActivity(models.Model):
    ACTION_CHOICE = [
        ('view_lesson', 'View Lesson'),
        ('start_quiz', 'Start Quiz'),
        ('complete_lesson', 'Complete Lesson'),
        ('pass_quiz', 'Pass Quiz'),
        ('fail_quiz', 'Fail Quiz'),
    ]
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICE)
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True) 

    class Meta:
        ordering = ['-timestamp']



class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    code = models.CharField(max_length=64, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="certificates/", blank=True, null=True)  # for PDF later

    def __str__(self):
        return f"Certificate {self.code} for {self.user.username} - {self.course.title}"
