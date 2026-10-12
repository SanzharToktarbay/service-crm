from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ClientForm, InteractionForm
from .mixins import ManagerScopedMixin, scope_for_user
from .models import Client


class ClientListView(LoginRequiredMixin, ManagerScopedMixin, ListView):
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("manager")
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone__icontains=q)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Client.Status.choices
        context["q"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context


class ClientDetailView(LoginRequiredMixin, ManagerScopedMixin, DetailView):
    model = Client
    template_name = "clients/client_detail.html"
    context_object_name = "client"

    def get_queryset(self):
        return super().get_queryset().select_related("manager")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object
        context["interactions"] = client.interactions.all()
        context["deals"] = client.deals.all()
        context["tasks"] = client.tasks.select_related("assignee")
        context["interaction_form"] = InteractionForm(initial={"happened_at": timezone.localtime()})
        return context


class ClientFormMixin:
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ClientCreateView(LoginRequiredMixin, ClientFormMixin, CreateView):
    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.manager = self.request.user
        messages.success(self.request, "Клиент создан")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, ManagerScopedMixin, ClientFormMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Изменения сохранены")
        return super().form_valid(form)


class InteractionCreateView(LoginRequiredMixin, CreateView):
    form_class = InteractionForm
    http_method_names = ["post"]

    def get_client(self):
        return get_object_or_404(
            scope_for_user(Client.objects.all(), self.request.user), pk=self.kwargs["pk"]
        )

    def form_valid(self, form):
        client = self.get_client()
        form.instance.client = client
        form.save()
        messages.success(self.request, "Взаимодействие добавлено")
        return redirect(client)

    def form_invalid(self, form):
        self.get_client()
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
        return redirect("clients:detail", pk=self.kwargs["pk"])