from rest_framework import filters, viewsets

from .mixins import ManagerScopedMixin, OwnerOnCreateMixin
from .models import Client, Interaction
from .serializers import ClientSerializer, InteractionSerializer

NO_DELETE = ["get", "post", "put", "patch", "head", "options"]


class ClientViewSet(ManagerScopedMixin, OwnerOnCreateMixin, viewsets.ModelViewSet):
    queryset = Client.objects.select_related("manager")
    serializer_class = ClientSerializer
    http_method_names = NO_DELETE
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "phone"]
    ordering_fields = ["created_at", "first_name"]

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class InteractionViewSet(ManagerScopedMixin, viewsets.ModelViewSet):
    queryset = Interaction.objects.select_related("client")
    serializer_class = InteractionSerializer
    manager_field = "client__manager"
    http_method_names = NO_DELETE

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = self.request.query_params.get("client", "")
        if client_id.isdigit():
            qs = qs.filter(client_id=client_id)
        return qs