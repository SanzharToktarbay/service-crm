from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, ListView

from clients.mixins import ManagerScopedMixin, scope_for_user

from .forms import TaskForm
from .models import Task


class TaskListView(LoginRequiredMixin, ManagerScopedMixin, ListView):
    model = Task
    manager_field = "assignee"
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        qs = super().get_queryset().select_related("client", "assignee")
        if self.request.GET.get("show") == "done":
            return qs.filter(is_done=True).order_by("-done_at")
        return qs.filter(is_done=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show"] = self.request.GET.get("show", "open")
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if "client" in self.request.GET:
            initial["client"] = self.request.GET["client"]
        return initial

    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.assignee = self.request.user
        messages.success(self.request, "Задача создана")
        return super().form_valid(form)


class TaskToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(
            scope_for_user(Task.objects.all(), request.user, "assignee"), pk=pk
        )
        task.is_done = not task.is_done
        task.save()
        next_url = request.POST.get("next", "")
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("tasks:list")