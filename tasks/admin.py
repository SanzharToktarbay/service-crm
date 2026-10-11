from django.contrib import admin
from django.utils import timezone

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "assignee", "priority", "due_at", "is_done", "overdue")
    list_filter = ("is_done", "priority", "assignee")
    search_fields = ("title", "client__first_name", "client__phone")
    list_editable = ("is_done",)
    autocomplete_fields = ("client", "deal")
    readonly_fields = ("done_at", "created_at")
    actions = ["mark_done"]

    @admin.display(boolean=True, description="Просрочена")
    def overdue(self, obj):
        return obj.is_overdue

    @admin.action(description="Отметить выполненными")
    def mark_done(self, request, queryset):
        updated = queryset.filter(is_done=False).update(is_done=True, done_at=timezone.now())
        self.message_user(request, f"Выполнено задач: {updated}")