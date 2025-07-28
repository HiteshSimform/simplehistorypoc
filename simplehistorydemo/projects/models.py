# Create your models here.
from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from simple_history.utils import update_change_reason

from .signals import get_current_request


class Project(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)  # Soft delete flag
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        request = get_current_request()
        if request:
            user = getattr(request, "user", None)
            ip = request.META.get("REMOTE_ADDR")
            ua = request.META.get("HTTP_USER_AGENT")
            reason = f"Changed via API by {user} | IP: {ip} | UA: {ua}"

            # Safe: attach user and reason via request
            request._history_user = user
            request._change_reason = reason  # will be picked by middleware

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name
