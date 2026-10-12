from django import forms

from .models import Client, Interaction


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "phone", "email", "status", "source", "manager"]
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+7 7XX XXX XX XX"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and not user.is_staff:
            del self.fields["manager"]


class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ["type", "happened_at", "comment"]
        widgets = {
            "happened_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Что обсудили"}),
        }