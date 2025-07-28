from django.urls import path

from .views import (
    UserActivityHistoryView,
    UserHistoryView,
    UserProfileView,
    UserRegisterView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("users/<int:id>/history/", UserHistoryView.as_view(), name="user-history"),
    path(
        "users/<int:user_id>/activity-history/",
        UserActivityHistoryView.as_view(),
        name="user-activity-history",
    ),
]
