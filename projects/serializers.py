from rest_framework import serializers
from .models import Project, ProjectMembership
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "start_date", "end_date",
                  "status", "created_by", "created_at"]


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ["id", "user", "role"]


class ProjectInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        project = self.context["project"]
        email = validated_data["email"]
        user = User.objects.get(email=email)

        membership, created = ProjectMembership.objects.get_or_create(
            project=project,
            user=user,
            defaults={"role": "member"},
        )
        if not created:
            raise serializers.ValidationError("User is already a project member.")

        return membership
    
class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = ["role"]

    def validate_role(self, value):
        if value not in ["admin", "member"]:
            raise serializers.ValidationError("Role must be either 'admin' or 'member'.")
        return value