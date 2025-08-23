from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Task, Comment, Subtask, Attachment
from .serializers import (TaskSerializer, CommentSerializer, 
                          SubtaskSerializer, AttachmentSerializer)
from projects.models import Project, ProjectMembership
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from projects.permissions import IsMember, IsAdminOrOwner, IsSelfOrAdminOrOwner, IsProjectMember, IsProjectOwner
from rest_framework.exceptions import PermissionDenied

class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/projects/{project_pk}/tasks/
    POST /api/projects/{project_pk}/tasks/
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsMember]

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return Task.objects.filter(project=project)

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        # user must at least be a member
        if not ProjectMembership.objects.filter(project=project, user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this project.")
        serializer.save(project=project, created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/{id}/
    PATCH  /api/tasks/{id}/
    DELETE /api/tasks/{id}/
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsMember]

    def perform_update(self, serializer):
        task = self.get_object()
        project = task.project

        # Allow if: creator OR admin/owner
        if task.created_by != self.request.user and not IsAdminOrOwner().has_object_permission(self.request, self, project):
            raise PermissionDenied("You do not have permission to update this task.")

        serializer.save()

    def perform_destroy(self, instance):
        project = instance.project

        # Only admin/owner can delete tasks
        if not IsAdminOrOwner().has_object_permission(self.request, self, project):
            raise PermissionDenied("Only admins or owner can delete tasks.")

        instance.delete()


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/{task_pk}/comments/
    POST /api/tasks/{task_pk}/comments/
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsMember]

    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        return task.comments.all()

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        if not ProjectMembership.objects.filter(project=task.project, user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this project.")
        serializer.save(task=task, created_by=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/comments/{id}/
    PATCH  /api/comments/{id}/
    DELETE /api/comments/{id}/
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsMember]

    def perform_update(self, serializer):
        comment = self.get_object()
        project = comment.task.project

        # Allow if: comment author OR admin/owner
        if comment.created_by != self.request.user and not IsAdminOrOwner().has_object_permission(self.request, self, project):
            raise PermissionDenied("You cannot update this comment.")

        serializer.save()

    def perform_destroy(self, instance):
        project = instance.task.project

        # Allow if: comment author OR admin/owner
        if instance.created_by != self.request.user and not IsAdminOrOwner().has_object_permission(self.request, self, project):
            raise PermissionDenied("You cannot delete this comment.")

        instance.delete()


class SubtaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/<task_pk>/subtasks/
    POST /api/tasks/<task_pk>/subtasks/
    """
    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        return task.subtasks.all()

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        # ensure requester is a project member
        if not ProjectMembership.objects.filter(
            project=task.project, user=self.request.user
        ).exists():
            raise PermissionDenied("You are not a member of this project.")
        serializer.save(task=task)


class SubtaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/subtasks/<pk>/
    PATCH  /api/subtasks/<pk>/
    DELETE /api/subtasks/<pk>/
    """
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def _can_modify(self, subtask):
        project = subtask.task.project
        return (
            IsProjectOwner().has_object_permission(self.request, self, project)
            or subtask.task.created_by == self.request.user
        )

    def perform_update(self, serializer):
        subtask = self.get_object()
        if not self._can_modify(subtask):
            raise PermissionDenied("Only project owner or task creator can update.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self._can_modify(instance):
            raise PermissionDenied("Only project owner or task creator can delete.")
        instance.delete()


class AttachmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/<task_pk>/attachments/
    POST /api/tasks/<task_pk>/attachments/
    """
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        return task.attachments.all()

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_pk"])
        # ensure uploader is a project member
        if not ProjectMembership.objects.filter(
            project=task.project, user=self.request.user
        ).exists():
            raise PermissionDenied("You are not a member of this project.")
        serializer.save(task=task, uploaded_by=self.request.user)


class AttachmentDetailView(generics.DestroyAPIView):
    """
    DELETE /api/attachments/<pk>/
    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def perform_destroy(self, instance):
        project = instance.task.project
        user = self.request.user

        # ✅ Inline check: only project owner or the uploader can delete
        if project.owner != user and instance.uploaded_by != user:
            raise PermissionDenied("Only project owner or uploader can delete this file.")

        instance.delete()