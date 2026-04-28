from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),

    path('register/', views.register, name='register'),

    path('logout/', views.user_logout, name='logout'),

    # 👑 DASHBOARDS (DIRECT, NO REDIRECT ROUTE)
    path('dashboard/', views.dashboard, name='dashboard'),

    path('student/', views.student_dashboard, name='student_dashboard'),

    # 📝 EVALUATION
    path('eval/<int:t_id>/', views.submit_eval, name='submit_eval'),
    # 📄 CSV EXPORT
    path('export/', views.export_csv, name='export'),
]