from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating projects.
    """

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["is_deleted"]


# class ProjectHistorySerializer(serializers.ModelSerializer):
#     """
#     Serializer for historical records of a project, showing what changed.
#     """
#     history_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
#     changed_by = serializers.SerializerMethodField()
#     changes = serializers.SerializerMethodField()

#     class Meta:
#         model = Project.history.model
#         fields = [
#             'id',
#             'name',
#             'description',
#             'status',
#             'manager',
#             'history_id',
#             'history_date',
#             'history_type',
#             'changed_by',
#             'changes',
#         ]

#     def get_changed_by(self, obj):
#         return str(obj.history_user) if obj.history_user else "System"

#     def get_changes(self, obj):
#         previous = obj.prev_record
#         if not previous:
#             return {}

#         changes = {}
#         for field in ['name', 'description', 'status', 'manager_id']:
#             old = getattr(previous, field, None)
#             new = getattr(obj, field, None)
#             if old != new:
#                 changes[field] = {'from': old, 'to': new}
#         return changes


class ProjectHistorySerializer(serializers.ModelSerializer):
    history_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    changed_by = serializers.SerializerMethodField()
    change_reason = serializers.SerializerMethodField()
    changes = serializers.SerializerMethodField()

    class Meta:
        model = Project.history.model
        fields = [
            "history_id",
            "history_type",
            "history_date",
            "changed_by",
            "change_reason",
            "changes",
            "name",
            "description",
            "status",
            "manager",
        ]

    def get_changed_by(self, obj):
        return str(obj.history_user) if obj.history_user else "System"

    def get_change_reason(self, obj):
        return getattr(obj, "history_change_reason", None)

    def get_changes(self, obj):
        previous = obj.prev_record
        if not previous:
            return {}

        fields = ["name", "description", "status", "manager_id"]
        changes = {}
        for field in fields:
            old = getattr(previous, field)
            new = getattr(obj, field)
            if old != new:
                changes[field] = {"from": old, "to": new}
        return changes
