from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # HOME REDIRECT (FIX FOR VIEW SITE ISSUE)
    # =========================
    path('', views.home_redirect, name='home'),

    # =========================
    # AUTH
    # =========================
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # =========================
    # DASHBOARDS
    # =========================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),

    # =========================
    # EVALUATION
    # =========================
    path('evaluate/<int:t_id>/', views.submit_eval, name='submit_eval'),

    # =========================
    # EXPORT CSV
    # =========================
    path('export/', views.export_csv, name='export'),
]