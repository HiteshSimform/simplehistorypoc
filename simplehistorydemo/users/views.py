from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from projects.serializers import ProjectHistorySerializer
from rest_framework import (
    generics,
    permissions,
    status,
)
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
)
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
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

    Creates a new user using the provided data.
    Accessible by unauthenticated users.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        self.request._history_user = user


class UserProfileView(APIView):
    """
    API view to retrieve the profile of the currently authenticated user.

    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": _("An error occurred while retrieving the profile.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserHistoryView(RetrieveAPIView):
    """
    API view to get historical changes of a specific user.

    Admin-only access.
    """

    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            history = user.history.all().order_by("-history_date")
            serializer = UserHistorySerializer(history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            raise NotFound(_("User not found."))
        except Exception as e:
            return Response(
                {"detail": _("Unable to fetch user history.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserActivityHistoryView(APIView):
    """
    API view to get all history logs (user, project, task, etc.)
    for a given user. Only accessible to authenticated users.

    Admins can view history for any user.
    Non-admins can only view their own history.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = get_object_or_404(CustomUser, pk=user_id)

            if request.user != user and not request.user.is_staff:
                raise PermissionDenied(_("You do not have permission to view this data."))

            user_histories = user.history.all().order_by("-history_date")
            project_histories = Project.history.filter(history_user=user).order_by("-history_date")

            response_data = {
                "user": UserHistorySerializer(user_histories, many=True).data,
                "projects": ProjectHistorySerializer(project_histories, many=True).data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except PermissionDenied as pd:
            return Response({"detail": str(pd)}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            return Response({"detail": _("User not found.")}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"detail": _("An error occurred while retrieving activity history.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
