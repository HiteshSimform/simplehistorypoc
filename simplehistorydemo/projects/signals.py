import threading

from django.db.models.signals import (
    post_delete,
    post_save,
)
from django.dispatch import receiver
from django.utils.timezone import now
from simple_history.utils import update_change_reason

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class ThreadLocalMiddleware:
    """
    Middleware to store request in thread-local storage for audit access.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
