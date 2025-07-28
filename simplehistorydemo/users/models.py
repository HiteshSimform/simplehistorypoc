# Create your models here
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from .manager import CustomUserManager


def validate_gmail_email(value):
    """
    Validator to ensure the email ends with @gmail.com.
    """
    if not value.lower().endswith("@gmail.com"):
        raise ValidationError(_("Email must be a Gmail address."))


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email as the primary login field and also supports username.
    Tracks changes using django-simple-history.
    """

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("staff", "Staff"),
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        verbose_name=_("username"),
    )

    email = models.EmailField(unique=True, validators=[validate_gmail_email], verbose_name=_("email address"))

    first_name = models.CharField(max_length=100, verbose_name=_("first name"))

    last_name = models.CharField(max_length=100, verbose_name=_("last name"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
        verbose_name=_("active"),
    )

    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
        verbose_name=_("staff status"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("last updated"))

    history = HistoricalRecords()

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.username})"

    @property
    def name(self):
        """
        Returns full name (first + last).
        """
        return f"{self.first_name} {self.last_name}"
