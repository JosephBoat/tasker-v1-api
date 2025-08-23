from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Project, ProjectMembership
from rest_framework.exceptions import PermissionDenied
from .serializers import (ProjectSerializer, ProjectMembershipSerializer,
                           ProjectInviteSerializer, RoleUpdateSerializer)
from accounts.permissions import IsProjectOwner, IsProjectMember, IsProjectOwner



class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        # Add creator as owner in ProjectMembership
        ProjectMembership.objects.create(
            project=project, user=self.request.user, role="owner"
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def perform_update(self, serializer):
        project = serializer.instance
        # Only owner can update
        if not IsProjectOwner().has_object_permission(self.request, self, project):
            raise permissions.PermissionDenied("Only project owner can edit.")
        serializer.save()

    def perform_destroy(self, instance):
        if not IsProjectOwner().has_object_permission(self.request, self, instance):
            raise permissions.PermissionDenied("Only project owner can delete.")
        instance.delete()

class ProjectInviteView(APIView):
    """
    POST /api/projects/<id>/invite/
    body: { "email": "user@example.com" }
    """

    permission_classes = [permissions.IsAuthenticated, IsProjectOwner]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        # Check owner permissions
        if not IsProjectOwner().has_object_permission(request, self, project):
            return Response({"detail": "Only owner can invite members."}, status=403)

        serializer = ProjectInviteSerializer(
            data=request.data, context={"project": project}
        )
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()

        return Response(
            {"message": f"{membership.user.email} added as {membership.role}"},
            status=201,
        )
    
class UpdateMemberRoleView(generics.UpdateAPIView):
    """
    PATCH /api/projects/{project_id}/members/{user_id}/role/
    """
    serializer_class = RoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectOwner]

    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        # ensure the requester is the owner
        if not ProjectMembership.objects.filter(project=project, user=self.request.user, role="owner").exists():
            raise PermissionDenied("Only the project owner can change roles.")

        member = get_object_or_404(ProjectMembership, project=project, user_id=self.kwargs["user_id"])
        if member.role == "owner":
            raise PermissionDenied("Cannot change the owner's role.")
        return member