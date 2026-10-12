from rest_framework import serializers

from clients.models import Client
from clients.serializers import ScopedRelatedField, StaffOnlyFieldsMixin
from deals.models import Deal

from .models import Task


class TaskSerializer(StaffOnlyFieldsMixin, serializers.ModelSerializer):
    client = ScopedRelatedField(Client, required=False, allow_null=True)
    deal = ScopedRelatedField(Deal, required=False, allow_null=True)
    is_overdue = serializers.BooleanField(read_only=True)
    staff_only_fields = ("assignee",)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "client", "deal", "assignee", "due_at",
            "priority", "is_done", "done_at", "is_overdue", "created_at",
        ]
        read_only_fields = ["done_at", "created_at"]

    def validate(self, attrs):
        client = attrs.get("client", getattr(self.instance, "client", None))
        deal = attrs.get("deal", getattr(self.instance, "deal", None))
        if deal and client and deal.client_id != client.id:
            raise serializers.ValidationError({"deal": "Эта сделка принадлежит другому клиенту"})
        return attrs