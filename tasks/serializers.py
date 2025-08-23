from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, TaskAssignment, Comment, Subtask, Attachment

User = get_user_model()


class TaskAssignmentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = TaskAssignment
        fields = ["id", "user", "assigned_at"]


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.email")
    assignees = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description", "due_date",
            "priority", "status", "created_by", "created_at", "assignees"
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def create(self, validated_data):
        assignees = validated_data.pop("assignees", [])
        task = Task.objects.create(**validated_data)
        for user in assignees:
            TaskAssignment.objects.create(task=task, user=user)
        return task

    def update(self, instance, validated_data):
        assignees = validated_data.pop("assignees", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if assignees is not None:
            instance.assignees.set(assignees)

        return instance
    


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "content", "created_at"]
        read_only_fields = ["id", "task", "author", "created_at"]


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ["id", "task", "title", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "task", "created_at", "updated_at"]



class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source="uploaded_by.email")

    class Meta:
        model = Attachment
        fields = ["id", "task", "uploaded_by", "file", "uploaded_at"]
        read_only_fields = ["id", "task", "uploaded_by", "uploaded_at"]