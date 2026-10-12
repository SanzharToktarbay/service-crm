from rest_framework import serializers

from clients.models import Client
from clients.serializers import ScopedRelatedField, StaffOnlyFieldsMixin

from .models import Deal


class DealSerializer(StaffOnlyFieldsMixin, serializers.ModelSerializer):
    client = ScopedRelatedField(Client)
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    staff_only_fields = ("manager",)

    class Meta:
        model = Deal
        fields = [
            "id", "title", "client", "manager", "amount", "stage", "stage_display",
            "lost_reason", "created_at", "updated_at", "closed_at",
        ]
        read_only_fields = ["created_at", "updated_at", "closed_at"]

    def validate(self, attrs):
        stage = attrs.get("stage", getattr(self.instance, "stage", None))
        lost_reason = attrs.get("lost_reason", getattr(self.instance, "lost_reason", ""))
        if stage == Deal.Stage.LOST and not lost_reason:
            raise serializers.ValidationError({"lost_reason": "Укажите причину отказа"})
        return attrs