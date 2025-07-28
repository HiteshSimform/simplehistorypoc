# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from django.utils.translation import gettext_lazy as _
# from rest_framework.validators import UniqueValidator
# from .models import CustomUser

# User = get_user_model()


# class UserRegisterSerializer(serializers.ModelSerializer):
#     """
#     Serializer for registering new users.
#     Includes password confirmation and validation.
#     """

#     email = serializers.EmailField(
#         required=True, validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#     username = serializers.CharField(
#         required=True, validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#     password = serializers.CharField(
#         write_only=True,
#         required=True,
#         validators=[validate_password],
#         style={"input_type": "password"},
#     )
#     confirm_password = serializers.CharField(
#         write_only=True,
#         required=True,
#         label=_("Confirm Password"),
#         style={"input_type": "password"},
#     )

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "username",
#             "first_name",
#             "last_name",
#             "password",
#             "confirm_password",
#         )
#         extra_kwargs = {
#             "first_name": {"required": True},
#             "last_name": {"required": True},
#         }

#     def validate(self, attrs):
#         if attrs["password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError(
#                 {"confirm_password": _("Passwords do not match.")}
#             )
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop("confirm_password")
#         user = User.objects.create_user(**validated_data)
#         return user


# class UserSerializer(serializers.ModelSerializer):
#     """
#     Serializer for displaying user details.
#     """

#     name = serializers.ReadOnlyField()

#     class Meta:
#         model = User
#         fields = (
#             "id",
#             "email",
#             "username",
#             "first_name",
#             "last_name",
#             "name",
#             "is_active",
#             "is_staff",
#             "created_at",
#         )
#         read_only_fields = ("is_active", "is_staff", "created_at")


# class UserHistorySerializer(serializers.ModelSerializer):
#     """
#     Serializer for displaying user history logs.
#     """

#     changed_by = serializers.SerializerMethodField()
#     history_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

#     class Meta:
#         model = CustomUser.history.model  # Access historical model
#         fields = (
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'history_id',
#             'history_date',
#             'history_type',
#             'changed_by',
#         )

#     def get_changed_by(self, obj):
#         return str(obj.history_user) if obj.history_user else "System"

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import CustomUser

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.
    Includes password confirmation and validation.
    """

    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        label=_("Confirm Password"),
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user details.
    """

    # Assuming you want a full name field combining first_name and last_name:
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "name",
            "is_active",
            "is_staff",
            "created_at",
        )
        read_only_fields = ("is_active", "is_staff", "created_at")

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# class UserHistorySerializer(serializers.ModelSerializer):
#     """
#     Serializer for showing user change history with field-level diffs.
#     """

#     changed_by = serializers.SerializerMethodField()
#     history_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
#     changes = serializers.SerializerMethodField()

#     class Meta:
#         model = CustomUser.history.model
#         fields = (
#             "id",
#             "email",
#             "username",
#             "first_name",
#             "last_name",
#             "history_id",
#             "history_date",
#             "history_type",
#             "changed_by",
#             "changes",
#         )

#     # def get_changed_by(self, obj):
#     #     return str(obj.history_user) if obj.history_user else "System"

#     def get_changed_by(self, obj):
#         return obj.changed_by.username if obj.changed_by else "System"

#     def get_changes(self, obj):
#         """
#         Compare current historical record with the previous one and return a dict of changes.
#         """
#         previous = obj.prev_record
#         if not previous:
#             return {}  # No previous record means this was creation

#         changes = {}
#         for field in ["email", "username", "first_name", "last_name"]:
#             old = getattr(previous, field, None)
#             new = getattr(obj, field, None)
#             if old != new:
#                 changes[field] = {"from": old, "to": new}
#         return changes


class UserHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for showing user change history with field-level diffs.
    """

    changed_by = serializers.SerializerMethodField()
    history_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    changes = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser.history.model
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "history_id",
            "history_date",
            "history_type",
            "changed_by",
            "changes",
        )

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else "System"

    def get_changes(self, obj):
        """
        Compare current historical record with the previous one and return a dict of changes.
        """
        previous = obj.prev_record
        if not previous:
            return {}

        changes = {}
        for field in ["email", "username", "first_name", "last_name"]:
            old = getattr(previous, field, None)
            new = getattr(obj, field, None)
            if old != new:
                changes[field] = {"from": old, "to": new}
        return changes
