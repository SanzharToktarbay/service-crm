from rest_framework import viewsets

from clients.mixins import ManagerScopedMixin, OwnerOnCreateMixin

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(ManagerScopedMixin, OwnerOnCreateMixin, viewsets.ModelViewSet):
    queryset = Task.objects.select_related("client", "assignee")
    serializer_class = TaskSerializer
    manager_field = "assignee"

    def get_queryset(self):
        qs = super().get_queryset()
        is_done = self.request.query_params.get("is_done")
        if is_done in ("true", "false"):
            qs = qs.filter(is_done=(is_done == "true"))
        return qs