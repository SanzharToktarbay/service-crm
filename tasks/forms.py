from django import forms

from clients.mixins import scope_for_user
from clients.models import Client
from deals.models import Deal

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "client", "deal", "assignee", "due_at", "priority"]
        widgets = {
            "due_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = scope_for_user(Client.objects.all(), user)
        self.fields["deal"].queryset = scope_for_user(Deal.objects.select_related("client"), user)
        if not user.is_staff:
            del self.fields["assignee"]