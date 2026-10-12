from rest_framework import filters, viewsets

from clients.mixins import ManagerScopedMixin, OwnerOnCreateMixin

from .models import Deal
from .serializers import DealSerializer


class DealViewSet(ManagerScopedMixin, OwnerOnCreateMixin, viewsets.ModelViewSet):
    queryset = Deal.objects.select_related("client", "manager")
    serializer_class = DealSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "client__first_name", "client__phone"]
    ordering_fields = ["created_at", "amount"]

    def get_queryset(self):
        qs = super().get_queryset()
        stage = self.request.query_params.get("stage")
        if stage:
            qs = qs.filter(stage=stage)
        return qs