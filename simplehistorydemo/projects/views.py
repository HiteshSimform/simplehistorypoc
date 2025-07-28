from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    render,
)

# Create your views here.
from rest_framework import (
    generics,
    permissions,
    status,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from simple_history.utils import update_change_reason

from .models import Project
from .serializers import (
    ProjectHistorySerializer,
    ProjectSerializer,
)


class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to allow only Admins or Managers to create/update/delete projects.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "admin",
            "manager",
        ]


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    GET: List all projects (authenticated users only).
    POST: Create a new project (admins or managers only).
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        self.request._history_user = self.request.user  # Track creator
        serializer.save()


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a project.
    PUT/PATCH: Update project (admins or managers only).
    DELETE: Delete project (admins only).
    """

    queryset = Project.objects.filter(is_deleted=False)
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        self.request._history_user = self.request.user
        serializer.save()

    def perform_destroy(self, instance):
        self.request._history_user = self.request.user
        instance.delete()


class ProjectHistoryView(APIView):
    """
    GET: View history of a specific project (admin only).
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
            if project.is_deleted:
                return Response({"detail": "Project is deleted."}, status=404)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    GET: List all projects with filtering by status or manager.
    POST: Create a new project.
    """

    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(is_deleted=False)
        status_param = self.request.query_params.get("status")
        manager_param = self.request.query_params.get("manager")

        if status_param:
            queryset = queryset.filter(status=status_param)
        if manager_param:
            queryset = queryset.filter(manager_id=manager_param)
        return queryset


# class ProjectRollbackView(APIView):
#     """
#     POST: Roll back a project to a specific historical version (admin only).
#     """

#     permission_classes = [permissions.IsAdminUser]

#     def post(self, request, pk, history_id):
#         project = get_object_or_404(Project, pk=pk, is_deleted=False)
#         history_obj = get_object_or_404(project.history.all(), history_id=history_id)

#         fields_to_restore = ["name", "description", "status", "manager"]

#         for field in fields_to_restore:
#             setattr(project, field, getattr(history_obj, field))

#         update_change_reason(project, f"Rolled back to version {history_id}")
#         request._history_user = request.user
#         project.save()

#         serializer = ProjectSerializer(project)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class RollbackProjectView(APIView):
    """
    Rollback a project to a specific historical version.
    """

    def post(self, request, pk, history_id):
        try:
            project = Project.objects.get(pk=pk)
            historical_record = project.history.get(history_id=history_id)

            # Get restored object
            restored_instance = historical_record.instance

            # Set rollback actor and reason
            restored_instance._history_user = request.user
            update_change_reason(restored_instance, f"Rolled back to version {history_id}")

            # Save to persist rollback
            restored_instance.save()

            return Response(
                {"detail": f"Project {pk} rolled back to history ID {history_id}."}, status=status.HTTP_200_OK
            )

        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        except project.history.model.DoesNotExist:
            return Response({"detail": "Historical version not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectHistoryListView(generics.ListAPIView):
    """
    Returns the history log of a specific project.
    """

    serializer_class = ProjectHistorySerializer

    def get_queryset(self):
        return Project.history.filter(id=self.kwargs["pk"]).order_by("-history_date")
