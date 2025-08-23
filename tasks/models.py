from django.db import models
from django.conf import settings
from projects.models import Project
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="todo")

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="tasks_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    assignees = models.ManyToManyField(
        User,
        through="TaskAssignment",
        related_name="tasks_assigned",
        blank=True,
    )

    def __str__(self):
        return f"{self.title} ({self.project.name})"


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("task", "user")

    def __str__(self):
        return f"{self.user} → {self.task}"
    

class Comment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"


class Subtask(models.Model):
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="subtasks"
    )
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="todo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} [{self.status}] → {self.task}"


class Attachment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="attachments"
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Attachment for {self.task} by {self.uploaded_by}"