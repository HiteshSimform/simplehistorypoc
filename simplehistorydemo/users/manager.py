from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for handling user creation using email instead of username.
    Supports creation of regular users and superusers.

    Usage:
        CustomUser.objects.create_user(...)
        CustomUser.objects.create_superuser(...)
    """

    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email, username, first name,
        last name, and password.

        Args:
            email (str): User's email address (must be unique).
            username (str): User's unique username.
            first_name (str): User's first name.
            last_name (str): User's last name.
            password (str, optional): Password for the user.
            extra_fields (dict): Additional fields for the user model.

        Returns:
            CustomUser: The newly created user instance.

        Raises:
            ValueError: If email or username is not provided.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        if not username:
            raise ValueError(_("The Username field must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given credentials.

        Ensures that is_staff and is_superuser flags are set.

        Args:
            email (str): User's email address.
            username (str): User's username.
            first_name (str): First name.
            last_name (str): Last name.
            password (str): Password.
            extra_fields (dict): Additional fields.

        Returns:
            CustomUser: The newly created superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, username, first_name, last_name, password, **extra_fields)
