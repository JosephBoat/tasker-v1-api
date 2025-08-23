from rest_framework.permissions import BasePermission
from .models import ProjectMembership, Project


def get_user_role(user, project):
    try:
        membership = ProjectMembership.objects.get(user=user, project=project)
        return membership.role
    except ProjectMembership.DoesNotExist:
        return None


class IsProjectOwner(BasePermission):
    """Allow only project owner."""

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        role = get_user_role(request.user, project)
        return role == "owner"


class IsAdminOrOwner(BasePermission):
    """Allow project admins and owner."""

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        role = get_user_role(request.user, project)
        return role in ["admin", "owner"]


class IsMember(BasePermission):
    """Allow any project member."""

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        role = get_user_role(request.user, project)
        return role in ["member", "admin", "owner"]


class IsSelfOrAdminOrOwner(BasePermission):
    """Used for cases like deleting/updating own comment or attachment."""

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        role = get_user_role(request.user, project)
        return (
            obj.uploaded_by == request.user
            or getattr(obj, "created_by", None) == request.user
            or role in ["admin", "owner"]
        )


class IsProjectMember(BasePermission):
    """
    Allows access only to members of the project.
    """

    def has_object_permission(self, request, view, obj):
        # obj may be Project itself, or something linked (Task, Comment, etc.)
        project = None
        if isinstance(obj, Project):
            project = obj
        elif hasattr(obj, "project"):
            project = obj.project
        elif hasattr(obj, "task"):  # e.g., Comment, Attachment
            project = obj.task.project

        if project is None:
            return False

        return ProjectMembership.objects.filter(
            project=project, user=request.user
        ).exists()