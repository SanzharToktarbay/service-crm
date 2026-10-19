from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from clients.mixins import ManagerScopedMixin

from .forms import DealForm
from .models import Deal


class DealBoardView(LoginRequiredMixin, ManagerScopedMixin, ListView):
    model = Deal
    template_name = "deals/deal_board.html"

    def get_queryset(self):
        return super().get_queryset().select_related("client", "manager")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deals = list(context["object_list"])
        context["columns"] = [
            {
                "stage": value,
                "label": label,
                "deals": [d for d in deals if d.stage == value],
                "total": sum(d.amount for d in deals if d.stage == value),
            }
            for value, label in Deal.Stage.choices
        ]
        return context


class DealFormMixin:
    model = Deal
    form_class = DealForm
    template_name = "deals/deal_form.html"
    success_url = reverse_lazy("deals:board")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DealCreateView(LoginRequiredMixin, DealFormMixin, CreateView):
    def get_initial(self):
        initial = super().get_initial()
        if "client" in self.request.GET:
            initial["client"] = self.request.GET["client"]
        return initial

    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.manager = self.request.user
        messages.success(self.request, "Сделка создана")
        return super().form_valid(form)


class DealUpdateView(LoginRequiredMixin, ManagerScopedMixin, DealFormMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Сделка обновлена")
        return super().form_valid(form)

class DealStageView(LoginRequiredMixin, ManagerScopedMixin, SingleObjectMixin, View):
    """Смена этапа перетаскиванием карточки на доске. Отвечает JSON, а не HTML."""

    model = Deal
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        deal.stage = request.POST.get("stage", "")
        deal.lost_reason = request.POST.get("lost_reason", deal.lost_reason).strip()
        try:
            deal.full_clean()
        except ValidationError as e:
            return JsonResponse({"errors": e.messages}, status=400)
        deal.save()
        return JsonResponse({"stage": deal.stage})
