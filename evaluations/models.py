from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# =========================
# YEAR LEVEL
# =========================
YEAR_LEVEL_CHOICES = [
    ('1ST', '1st Year'),
    ('2ND', '2nd Year'),
    ('3RD', '3rd Year'),
    ('4TH', '4th Year'),
]


# =========================
# SECTION MAP
# =========================
SECTION_MAP = {
    '1ST': [(str(i), str(i)) for i in range(101, 108)],
    '2ND': [(str(i), str(i)) for i in range(201, 208)],
    '3RD': [(str(i), str(i)) for i in range(301, 308)],
    '4TH': [(str(i), str(i)) for i in range(401, 408)],
}


# =========================
# TEACHER
# =========================
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)

    year_level = models.CharField(max_length=4, choices=YEAR_LEVEL_CHOICES)
    section = models.CharField(max_length=3)

    def clean(self):
        allowed_sections = SECTION_MAP.get(self.year_level, [])
        valid_values = [s[0] for s in allowed_sections]

        if self.section not in valid_values:
            raise ValidationError("Invalid section for this year level")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


# =========================
# PROFILE
# =========================
class Profile(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('PH', 'Program Head'),
        ('DEAN', 'Dean'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    department = models.CharField(max_length=100, blank=True, null=True)
    year_level = models.CharField(max_length=4, blank=True, null=True)
    section = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# =========================
# EVALUATION (FIXED + SAFE + UPDATED)
# =========================
class Evaluation(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('PH', 'Program Head'),
        ('DEAN', 'Dean')
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    rater = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # ⭐ 5 CATEGORIES (SAFE DEFAULTS ADDED)
    clarity = models.IntegerField(default=0)
    organization = models.IntegerField(default=0)
    engagement = models.IntegerField(default=0)
    fairness = models.IntegerField(default=0)
    professionalism = models.IntegerField(default=0)

    score = models.FloatField(default=0)

    year_level = models.CharField(max_length=4, blank=True, null=True)
    section = models.CharField(max_length=3, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================
    # AUTO SCORE + VALIDATION
    # =========================
    def save(self, *args, **kwargs):

        if self.rater:
            profile = getattr(self.rater, "profile", None)

            if not profile:
                raise ValidationError("Profile missing")

            self.role = profile.role
            self.year_level = profile.year_level
            self.section = profile.section

            # STRICT VALIDATION
            if profile.role == "STUDENT":
                if (
                    self.teacher.year_level != profile.year_level or
                    self.teacher.section != profile.section or
                    self.teacher.department != profile.department
                ):
                    raise ValidationError("Not allowed to evaluate this teacher")

        # ⭐ SAFE SCORE CALCULATION
        total = (
            self.clarity +
            self.organization +
            self.engagement +
            self.fairness +
            self.professionalism
        )

        self.score = round((total / 25) * 100, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher.name} - {self.score}"