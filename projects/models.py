# projects/models.py
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


class Project(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,   # prevent owner from being deleted accidentally
        related_name="projects_owned",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        User,
        through="ProjectMembership",
        related_name="projects",
    )

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")

    class Meta:
        unique_together = ("user", "project")
        # DB-level guard: at most ONE owner per project
        constraints = [
            models.UniqueConstraint(
                fields=["project"],
                condition=Q(role="owner"),
                name="unique_owner_per_project",
            )
        ]
        
    def clean(self):
        # App-level guard (defense in depth, and for DBs without partial unique indexes)
        if self.role == "owner":
            qs = ProjectMembership.objects.filter(project=self.project, role="owner")
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("This project already has an owner.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user} in {self.project} ({self.role})"
