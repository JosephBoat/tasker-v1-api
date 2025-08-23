from rest_framework import permissions
from projects.models import ProjectMembership


class IsProjectOwner(permissions.BasePermission):
    """
    Permission: only project owner has full access.
    """

    def has_object_permission(self, request, view, obj):
        # obj is a Project
        membership = ProjectMembership.objects.filter(
            project=obj, user=request.user, role="owner"
        ).first()
        return membership is not None


class IsProjectMember(permissions.BasePermission):
    """
    Permission: user must be a member of the project to view/interact.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMembership.objects.filter(
            project=obj, user=request.user
        ).exists()
