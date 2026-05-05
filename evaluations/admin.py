from django.contrib import admin
from .models import Teacher, Evaluation, Profile


# =========================
# 👨‍🏫 TEACHER ADMIN (IMPROVED)
# =========================
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'department',
        'subject',
        'year_level',
        'section'
    )

    list_filter = (
        'department',
        'year_level',
        'section'
    )

    search_fields = (
        'name',
        'department',
        'subject'
    )


# =========================
# 📝 EVALUATION ADMIN (IMPROVED)
# =========================
@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'score',
        'role',
        'year_level',
        'section',
        'created_at'
    )

    list_filter = (
        'role',
        'year_level',
        'section',
        'created_at'
    )

    search_fields = (
        'teacher__name',
        'role'
    )

    ordering = ('-created_at',)


# =========================
# 👤 PROFILE ADMIN (IMPROVED)
# =========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'role',
        'year_level',
        'section'
    )

    list_filter = (
        'role',
        'year_level',
        'section'
    )

    search_fields = (
        'user__username',
    )