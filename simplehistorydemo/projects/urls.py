from django.urls import path

from .views import (
    ProjectHistoryDiffView,
    ProjectHistoryListView,
    ProjectHistoryView,
    ProjectListCreateView,
    ProjectRetrieveUpdateDestroyView,
    RollbackProjectView,
)

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="project-list-create"),
    path(
        "projects/<int:pk>/",
        ProjectRetrieveUpdateDestroyView.as_view(),
        name="project-detail",
    ),
    # path('projects/<int:pk>/history/', ProjectHistoryView.as_view(), name='project-history'),
    path(
        "projects/<int:pk>/history/",
        ProjectHistoryListView.as_view(),
        name="project-history",
    ),
    path(
        "projects/<int:pk>/rollback/<int:history_id>/",
        RollbackProjectView.as_view(),
        name="project-rollback",
    ),
    path(
        "projects/<int:pk>/diff/",
        ProjectHistoryDiffView.as_view(),
        name="project-history-diff",
    ),
]
