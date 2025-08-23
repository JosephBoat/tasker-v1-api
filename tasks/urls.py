from django.urls import path
from .views import (TaskListCreateView, TaskDetailView, 
                    CommentListCreateView, CommentDetailView,
                    SubtaskListCreateView, SubtaskDetailView,
                    AttachmentDetailView, AttachmentListCreateView)

urlpatterns = [
    path("projects/<int:project_pk>/tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:task_pk>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("tasks/<int:task_pk>/subtasks/", SubtaskListCreateView.as_view(), name="subtask-list-create"),
    path("subtasks/<int:pk>/", SubtaskDetailView.as_view(), name="subtask-detail"),
    path("tasks/<int:task_pk>/attachments/", AttachmentListCreateView.as_view(), name="attachment-list-create"),
    path("attachments/<int:pk>/", AttachmentDetailView.as_view(), name="attachment-detail"),
]
