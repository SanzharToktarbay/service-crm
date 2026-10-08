from django.db import models


class Client(models.Model):
    class Status(models.TextChoices):
        LEAD = "lead", "Лид"
        ACTIVE = "active", "Активный"
        INACTIVE = "inactive", "Неактивный"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD)
    source = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()