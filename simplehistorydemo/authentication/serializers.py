import re

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise ValidationError("Email and Password are required")

        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Invalid user or password")
        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)

        return {
            "user": {"email": user.email},
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "message": "Login Successfull",
        }
