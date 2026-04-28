from django.contrib import admin
from .models import Teacher, Evaluation

# Para mas maganda ang itsura ng listahan sa Admin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name',)

class EvaluationAdmin(admin.ModelAdmin):
    # Ipinapakita ang teacher, role, at score sa listahan
    list_display = ('teacher', 'role', 'score', 'rater', 'created_at')
    list_filter = ('role', 'teacher') # Filter sa gilid para madaling maghanap

# I-register ang mga models
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Evaluation, EvaluationAdmin)