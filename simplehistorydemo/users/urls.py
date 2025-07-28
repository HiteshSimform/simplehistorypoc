from django.urls import path

from .views import (
    UserHistoryView,
    UserProfileView,
    UserRegisterView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("users/<int:id>/history/", UserHistoryView.as_view(), name="user-history"),
]
