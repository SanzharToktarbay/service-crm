from django.contrib import admin
from .models import Client, Interaction
from deals.models import Deal
from tasks.models import Task


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1


class DealInline(admin.TabularInline):
    model = Deal
    extra = 0
    fields = ("title", "amount", "stage", "lost_reason", "manager")
    show_change_link = True


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ("title", "assignee", "due_at", "priority", "is_done")
    show_change_link = True


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "status", "created_at")
    list_filter = ("status", "source")
    search_fields = ("first_name", "last_name", "phone")
    inlines = [InteractionInline, DealInline, TaskInline]
    list_display = ("first_name", "last_name", "phone", "status", "manager", "created_at")
    list_filter = ("status", "source", "manager")


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("client", "type", "happened_at")
    list_filter = ("type", "happened_at")
    search_fields = ("client__first_name", "client__phone", "comment")