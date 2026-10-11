from django.contrib import admin

from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_filter = ("stage", "manager")
    search_fields = ("title", "client__first_name", "client__phone")
    list_editable = ("stage",)
    autocomplete_fields = ("client",)
    readonly_fields = ("closed_at", "created_at", "updated_at")
    list_display = ("title", "client", "manager", "amount", "stage", "closed_at", "created_at")