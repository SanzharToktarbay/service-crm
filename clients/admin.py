from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "status", "created_at")
    list_filter = ("status", "source")
    search_fields = ("first_name", "last_name", "phone")