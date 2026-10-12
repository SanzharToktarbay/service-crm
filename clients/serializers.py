from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .mixins import scope_for_user
from .models import Client, Interaction, normalize_phone


class ScopedRelatedField(serializers.PrimaryKeyRelatedField):
    """Связь, в которой можно выбрать только доступные пользователю записи."""

    def __init__(self, model, manager_field="manager", **kwargs):
        self.model = model
        self.manager_field = manager_field
        super().__init__(**kwargs)

    def get_queryset(self):
        request = self.context.get("request")
        if request is None:
            return self.model.objects.none()
        return scope_for_user(self.model.objects.all(), request.user, self.manager_field)


class StaffOnlyFieldsMixin:
    """Поля, которые может менять только персонал. Для менеджера они только для чтения."""

    staff_only_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_staff:
            for name in self.staff_only_fields:
                self.fields[name].read_only = True


class ClientSerializer(StaffOnlyFieldsMixin, serializers.ModelSerializer):
    phone = serializers.CharField(max_length=20)
    manager_name = serializers.SerializerMethodField()
    staff_only_fields = ("manager",)

    class Meta:
        model = Client
        fields = [
            "id", "first_name", "last_name", "phone", "email",
            "status", "source", "manager", "manager_name", "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_manager_name(self, obj):
        if obj.manager is None:
            return None
        return obj.manager.get_full_name() or obj.manager.username

    def validate_phone(self, value):
        try:
            phone = normalize_phone(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        duplicates = Client.objects.filter(phone=phone)
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("Клиент с таким телефоном уже существует")
        return phone


class InteractionSerializer(serializers.ModelSerializer):
    client = ScopedRelatedField(Client)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Interaction
        fields = ["id", "client", "type", "type_display", "happened_at", "comment"]

    def validate_happened_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Дата взаимодействия не может быть в будущем")
        return value