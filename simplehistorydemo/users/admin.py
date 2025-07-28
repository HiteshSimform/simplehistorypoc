# from django.contrib import admin
# from .models import CustomUser

# # Register your models here.

# admin.site.register(CustomUser)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, SimpleHistoryAdmin):
    """
    Admin configuration for the CustomUser model.
    Combines Django's built-in UserAdmin with simple-history tracking.
    """

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important Dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    # This ensures simple_history gets the request.user for tracking
    def save_model(self, request, obj, form, change):
        obj._history_user = request.user
        super().save_model(request, obj, form, change)
