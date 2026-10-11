from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from clients.models import Client
from deals.models import Deal


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        NORMAL = "normal", "Обычный"
        HIGH = "high", "Высокий"

    title = models.CharField("Задача", max_length=200)
    description = models.TextField("Описание", blank=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Клиент",
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Сделка",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Исполнитель",
    )
    due_at = models.DateTimeField("Срок")
    priority = models.CharField(
        "Приоритет", max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    is_done = models.BooleanField("Выполнена", default=False)
    done_at = models.DateTimeField("Дата выполнения", null=True, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        ordering = ["is_done", "due_at"]
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        indexes = [models.Index(fields=["assignee", "is_done", "due_at"])]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return not self.is_done and self.due_at < timezone.now()

    def clean(self):
        if self.deal_id and self.client_id and self.deal.client_id != self.client_id:
            raise ValidationError({"deal": "Эта сделка принадлежит другому клиенту"})

    def save(self, *args, **kwargs):
        if self.deal_id and not self.client_id:
            self.client = self.deal.client
        if self.is_done and self.done_at is None:
            self.done_at = timezone.now()
        elif not self.is_done:
            self.done_at = None
        super().save(*args, **kwargs)