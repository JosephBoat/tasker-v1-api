from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, ProjectInviteView, UpdateMemberRoleView

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list-create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:pk>/invite/", ProjectInviteView.as_view(), name="project-invite"),
    path("projects/<int:project_id>/members/<int:user_id>/role/", UpdateMemberRoleView.as_view(), name="update-member-role"),

    
]
