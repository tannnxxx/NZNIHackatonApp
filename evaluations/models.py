from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def calculate_composite(self):
        evals = self.evaluation_set.all()

        s_avg = evals.filter(role='STUDENT').aggregate(Avg('score'))['score__avg'] or 0
        p_avg = evals.filter(role='PH').aggregate(Avg('score'))['score__avg'] or 0
        d_avg = evals.filter(role='DEAN').aggregate(Avg('score'))['score__avg'] or 0

        composite = (s_avg * 0.50) + (p_avg * 0.30) + (d_avg * 0.20)
        return round(composite, 2)

    def __str__(self):
        return self.name


# ✅ NEW PROFILE MODEL (para sa roles)
class Profile(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('PH', 'Program Head'),
        ('DEAN', 'Dean'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ✅ AUTO CREATE PROFILE
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Evaluation(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('PH', 'Program Head'),
        ('DEAN', 'Dean')
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    rater = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 AUTO ROLE FROM USER
    def save(self, *args, **kwargs):
        if self.rater and hasattr(self.rater, 'profile'):
            self.role = self.rater.profile.role
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher.name} - {self.role} - {self.score}"