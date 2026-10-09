from django.db import models


class Client(models.Model):
    class Status(models.TextChoices):
        LEAD = "lead", "Лид"
        ACTIVE = "active", "Активный"
        INACTIVE = "inactive", "Неактивный"

    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100, blank=True)
    phone = models.CharField("Телефон", max_length=20, unique=True)
    email = models.EmailField("Email", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.LEAD)
    source = models.CharField("Источник", max_length=50, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Interaction(models.Model):
    class Type(models.TextChoices):
        CALL = "call", "Звонок"
        MESSAGE = "message", "Сообщение"
        MEETING = "meeting", "Встреча"

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="interactions",
        verbose_name="Клиент",
    )
    type = models.CharField("Тип", max_length=20, choices=Type.choices, default=Type.CALL)
    happened_at = models.DateTimeField("Дата и время")
    comment = models.TextField("Комментарий", blank=True)

    class Meta:
        ordering = ["-happened_at"]
        verbose_name = "Взаимодействие"
        verbose_name_plural = "Взаимодействия"

    def __str__(self):
        return f"{self.get_type_display()} — {self.client}"