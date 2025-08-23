# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    TaskerTokenObtainPairSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    body: { "email": "", "password": "" }
    """
    serializer_class = TaskerTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    """
    POST /api/auth/refresh/
    body: { "refresh": "<token>" }
    """
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/me/          -> current user profile
    PATCH /api/auth/me/        -> update name/profile_picture
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
