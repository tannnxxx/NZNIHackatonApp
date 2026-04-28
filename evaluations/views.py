from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Teacher, Evaluation, Profile
import csv
from django.http import HttpResponse

# =========================
# 🔐 AUTH LOGIC
# =========================
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'student_dashboard')
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard' if user.is_staff else 'student_dashboard')
        messages.error(request, "Invalid credentials")
    return render(request, 'evaluations/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username taken")
        else:
            User.objects.create_user(username=u, password=p)
            messages.success(request, "Account created! Please login.")
            return redirect('login')
    return render(request, 'evaluations/register.html')

# =========================
# 👑 ADMIN DASHBOARD (Results Only)
# =========================
@login_required(login_url='login')
def dashboard(request):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    
    teachers = Teacher.objects.all()
    results = []
    for t in teachers:
        results.append({
            'id': t.id,
            'name': t.name,
            'dept': t.department,
            'score': t.calculate_composite()
        })
    return render(request, 'evaluations/dashboard.html', {'results': results})

# =========================
# 🎓 STUDENT DASHBOARD (With Evaluate Button)
# =========================
@login_required(login_url='login')
def student_dashboard(request):
    # Professors List para sa GRC
    profs_data = [
        ('Mr. Romark Cacho', 'AMC (Advance Mobile Computing)'),
        ('Mr. Christian Esguerra', 'ARCHORG (COMPUTER ARCHITECTURE AND ORGANIZATION)'),
        ('Mr. Eduardo Rodrigo', 'CAPS1 (Capstone 1)'),
        ('Mr. Rhavee Valencia', 'INFOSEC(Information Assurance and Security 1 )'),
        ('Mrs. Maria Maritess Olvis', 'RIZAL'),
        ('Mr. Mark Gabriel Antipala', 'WEBSYS (Web System and Technologies)'),
        ('Mrs. Ann Camile Maupay', 'QMTHODS (Quantitative Methods)'),
    ]
    
    # Auto-create professors sa database para hindi mag-error ang IDs
    for name, dept in profs_data:
        Teacher.objects.get_or_create(name=name, department=dept)

    teachers = Teacher.objects.all()
    evaluated_ids = Evaluation.objects.filter(rater=request.user).values_list('teacher_id', flat=True)
    
    return render(request, 'evaluations/student_dashboard.html', {
        'teachers': teachers,
        'evaluated_ids': list(evaluated_ids)
    })

# =========================
# 📝 SUBMIT EVALUATION
# =========================
@login_required(login_url='login')
def submit_eval(request, t_id):
    teacher = get_object_or_404(Teacher, id=t_id)
    
    if Evaluation.objects.filter(teacher=teacher, rater=request.user).exists():
        messages.warning(request, "Already evaluated this teacher.")
        return redirect('student_dashboard')

    if request.method == "POST":
        try:
            # Simple average logic for student evaluation
            q1 = int(request.POST.get('clarity', 0))
            q2 = int(request.POST.get('engagement', 0))
            q3 = int(request.POST.get('fairness', 0))
            
            # (Total Score / Max Score) * 100
            final_score = ((q1 + q2 + q3) / 15) * 100

            Evaluation.objects.create(
                teacher=teacher,
                rater=request.user,
                role='STUDENT',
                score=round(final_score, 2)
            )
            messages.success(request, f"Successfully evaluated {teacher.name}!")
            return redirect('student_dashboard')
        except:
            messages.error(request, "Please fill out all ratings.")

    return render(request, 'evaluations/form.html', {'teacher': teacher, 'role': 'STUDENT'})

# =========================
# 📄 EXPORT
# =========================
@login_required(login_url='login')
def export_csv(request):
    if not request.user.is_staff: return redirect('student_dashboard')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="eval_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Teacher', 'Score', 'Date'])
    for e in Evaluation.objects.all():
        writer.writerow([e.teacher.name, e.score, e.created_at])
    return response