from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import Project

admin.site.register(User, SimpleHistoryAdmin)
admin.site.register(Project, SimpleHistoryAdmin)
