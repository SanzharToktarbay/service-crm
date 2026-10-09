from django.contrib import admin
from .models import Client, Interaction


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "status", "created_at")
    list_filter = ("status", "source")
    search_fields = ("first_name", "last_name", "phone")
    inlines = [InteractionInline]


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("client", "type", "happened_at")
    list_filter = ("type", "happened_at")
    search_fields = ("client__first_name", "client__phone", "comment")