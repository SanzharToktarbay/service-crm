from django import forms

from clients.mixins import scope_for_user
from clients.models import Client

from .models import Deal


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ["title", "client", "amount", "stage", "lost_reason", "manager"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = scope_for_user(Client.objects.all(), user)
        if not user.is_staff:
            del self.fields["manager"]