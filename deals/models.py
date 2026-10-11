from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from clients.models import Client


class Deal(models.Model):
    class Stage(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        WON = "won", "Успешно"
        LOST = "lost", "Отказ"

    title = models.CharField("Название", max_length=200)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="deals",
        verbose_name="Клиент",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
        verbose_name="Менеджер",
    )
    amount = models.DecimalField(
        "Сумма, ₸",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    stage = models.CharField("Этап", max_length=20, choices=Stage.choices, default=Stage.NEW)
    lost_reason = models.CharField("Причина отказа", max_length=200, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)
    closed_at = models.DateTimeField("Закрыта", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"

    def __str__(self):
        return f"{self.title} — {self.client}"

    def clean(self):
        if self.stage == self.Stage.LOST and not self.lost_reason:
            raise ValidationError({"lost_reason": "Укажите причину отказа"})

    def save(self, *args, **kwargs):
        if self.stage in (self.Stage.WON, self.Stage.LOST):
            if self.closed_at is None:
                self.closed_at = timezone.now()
        else:
            self.closed_at = None
        super().save(*args, **kwargs)