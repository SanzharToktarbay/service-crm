from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from clients.mixins import scope_for_user
from clients.models import Client, Interaction
from deals.models import Deal
from tasks.models import Task


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        month_start = timezone.localtime(now).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        clients = scope_for_user(Client.objects.all(), user)
        deals = scope_for_user(Deal.objects.all(), user)
        tasks = scope_for_user(Task.objects.all(), user, "assignee")

        context["clients_stats"] = clients.aggregate(
            total=Count("id"),
            leads=Count("id", filter=Q(status=Client.Status.LEAD)),
        )

        open_stages = [Deal.Stage.NEW, Deal.Stage.IN_PROGRESS]
        won_this_month = Q(stage=Deal.Stage.WON, closed_at__gte=month_start)
        lost_this_month = Q(stage=Deal.Stage.LOST, closed_at__gte=month_start)
        stats = deals.aggregate(
            open_count=Count("id", filter=Q(stage__in=open_stages)),
            open_sum=Sum("amount", filter=Q(stage__in=open_stages)),
            won_count=Count("id", filter=won_this_month),
            won_sum=Sum("amount", filter=won_this_month),
            lost_count=Count("id", filter=lost_this_month),
        )
        closed = stats["won_count"] + stats["lost_count"]
        context["deals_stats"] = stats
        context["conversion"] = round(stats["won_count"] * 100 / closed) if closed else None

        open_tasks = tasks.filter(is_done=False)
        context["tasks_stats"] = open_tasks.aggregate(
            total=Count("id"),
            overdue=Count("id", filter=Q(due_at__lt=now)),
        )
        context["urgent_tasks"] = open_tasks.select_related("client").filter(
            due_at__lt=now + timedelta(days=1)
        )[:7]
        context["recent_interactions"] = Interaction.objects.filter(
            client__in=clients
        ).select_related("client")[:6]
        return context