from django.contrib import admin
from .models import (
    Course,
    CourseEnrollment,
    CourseProgress,
    Module,
    ModuleProgress,
    Lesson,
    LearningActivity,
    LessonProgress,
    Role,
    LessonResource,
    Badge,
    UserBadge,
    Question,
    Answer
)
# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(CourseEnrollment)
admin.site.register(CourseProgress)
admin.site.register(Module)
admin.site.register(ModuleProgress)

admin.site.register(Lesson)
admin.site.register(LearningActivity)
admin.site.register(LessonProgress)
admin.site.register(LessonResource)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(Question)
admin.site.register(Answer)