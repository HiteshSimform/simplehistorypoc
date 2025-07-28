from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# Create your views here.
from rest_framework import (
    generics,
    permissions,
)
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import (
    UserHistorySerializer,
    UserRegisterSerializer,
    UserSerializer,
)


class UserRegisterView(generics.CreateAPIView):
    """
    API view to register a new user.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        self.request._history_user = user  # Track who created the user (self in this case)


class UserProfileView(APIView):
    """
    API view to retrieve the currently authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserHistoryView(RetrieveAPIView):
    """
    Admin-only view to get historical changes of a user.
    """

    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        history = user.history.all().order_by("-history_date")

        serializer = UserHistorySerializer(history, many=True)
        return Response(serializer.data)
