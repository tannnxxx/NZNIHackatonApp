from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
import csv
import json

from .models import Teacher, Evaluation, Profile


# =========================
# PROFILE HELPER (SAFE FIX)
# =========================
def get_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)

    # ✅ SAFE DEFAULTS (prevents blank dashboard)
    if not profile.role:
        profile.role = "STUDENT"

    if not profile.year_level:
        profile.year_level = "1ST"

    if not profile.section:
        profile.section = "101"

    if not profile.department:
        profile.department = "BSIT"

    profile.save()
    return profile


# =========================
# HOME REDIRECT (FIXED ROUTING)
# =========================
def home_redirect(request):

    if not request.user.is_authenticated:
        return redirect('login')

    profile = get_profile(request.user)

    if request.user.is_superuser or profile.role != "STUDENT":
        return redirect('dashboard')

    return redirect('student_dashboard')


# =========================
# LOGIN
# =========================
def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid username or password")

    return render(request, 'evaluations/login.html')


# =========================
# LOGOUT
# =========================
def user_logout(request):
    logout(request)
    return redirect('login')


# =========================
# REGISTER (FIXED SAFE PROFILE CREATION)
# =========================
def register(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Missing fields")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        profile = get_profile(user)

        profile.role = "STUDENT"
        profile.year_level = request.POST.get('year') or "1ST"
        profile.section = request.POST.get('section') or "101"
        profile.department = request.POST.get('department') or "BSIT"
        profile.save()

        return redirect('login')

    return render(request, 'evaluations/register.html')


# =========================
# ADMIN DASHBOARD (FIXED + CLEAN + ACCURATE SCORES)
# =========================
@login_required
def dashboard(request):

    profile = get_profile(request.user)

    if profile.role == "STUDENT" and not request.user.is_superuser:
        return redirect('student_dashboard')

    teachers = Teacher.objects.all()

    results = []

    for t in teachers:
        avg_score = t.evaluation_set.aggregate(Avg('score'))['score__avg'] or 0

        results.append({
            'id': t.id,
            'name': t.name,
            'dept': t.department,
            'score': round(avg_score, 2)
        })

    labels = json.dumps([r['name'] for r in results])
    data = json.dumps([r['score'] for r in results])

    return render(request, 'evaluations/dashboard.html', {
        'results': results,
        'labels': labels,
        'data': data
    })


# =========================
# STUDENT DASHBOARD (FIXED FILTER + SAFE DATA)
# =========================
@login_required
def student_dashboard(request):

    profile = get_profile(request.user)

    teachers = Teacher.objects.filter(
        year_level=profile.year_level,
        section=profile.section,
        department=profile.department
    )

    evaluated = Evaluation.objects.filter(
        rater=request.user
    ).values_list('teacher_id', flat=True)

    return render(request, 'evaluations/student_dashboard.html', {
        'teachers': teachers,
        'evaluated_ids': list(evaluated),
        'profile': profile
    })


# =========================
# SUBMIT EVALUATION (5 CATEGORIES FIXED + SAFE SCORE CALC)
# =========================
@login_required
def submit_eval(request, t_id):

    teacher = get_object_or_404(Teacher, id=t_id)
    profile = get_profile(request.user)

    if request.method == "POST":

        clarity = int(request.POST.get('clarity', 0))
        organization = int(request.POST.get('organization', 0))
        engagement = int(request.POST.get('engagement', 0))
        fairness = int(request.POST.get('fairness', 0))
        professionalism = int(request.POST.get('professionalism', 0))

        Evaluation.objects.create(
            teacher=teacher,
            rater=request.user,
            role=profile.role,

            clarity=clarity,
            organization=organization,
            engagement=engagement,
            fairness=fairness,
            professionalism=professionalism,
        )

        return redirect('student_dashboard')

    return render(request, 'evaluations/form.html', {
        'teacher': teacher,
        'role': profile.role
    })


# =========================
# EXPORT CSV (ADMIN ONLY)
# =========================
@login_required
def export_csv(request):

    if not request.user.is_superuser:
        return redirect('student_dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="evaluation_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Teacher', 'Department', 'Score'])

    for e in Evaluation.objects.all():
        writer.writerow([
            e.teacher.name,
            e.teacher.department,
            e.score
        ])

    return response