import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clients.models import Client, Interaction
from deals.models import Deal
from tasks.models import Task

User = get_user_model()

CLIENTS = [
    ("Айгерим", "Сейткали", "+77011110001", "Instagram"),
    ("Дана", "Нурланова", "+77011110002", "2GIS"),
    ("Асель", "Жумабаева", "+77011110003", "Рекомендация"),
    ("Мадина", "Ахметова", "+77011110004", "Сайт"),
    ("Камила", "Оспанова", "+77011110005", "Instagram"),
    ("Жанна", "Ким", "+77011110006", "WhatsApp"),
    ("Алия", "Тулегенова", "+77011110007", "2GIS"),
    ("Сабина", "Ержанова", "+77011110008", "Рекомендация"),
]

DEALS = [
    ("Абонемент на 5 стрижек", 45000),
    ("Окрашивание и уход", 38000),
    ("Свадебный образ", 120000),
    ("Макияж на корпоратив, 6 человек", 90000),
    ("Абонемент на маникюр", 30000),
    ("Кератиновое выпрямление", 55000),
]

TASKS = [
    "Перезвонить и уточнить удобное время",
    "Отправить прайс в WhatsApp",
    "Напомнить о записи за день",
    "Спросить отзыв после визита",
]


class Command(BaseCommand):
    help = "Создаёт демо-данные: менеджера demo, клиентов, сделки и задачи"

    def add_arguments(self, parser):
        parser.add_argument("--password", required=True, help="Пароль для пользователя demo")

    @transaction.atomic
    def handle(self, *args, **options):
        if Client.objects.exists():
            self.stdout.write(self.style.WARNING("В базе уже есть клиенты, демо-данные не созданы"))
            return

        demo, _ = User.objects.get_or_create(
            username="demo", defaults={"first_name": "Демо", "last_name": "Менеджер"}
        )
        demo.set_password(options["password"])
        demo.save()
        admin = User.objects.filter(is_superuser=True).first() or demo

        rng = random.Random(42)
        now = timezone.now()

        for index, (first_name, last_name, phone, source) in enumerate(CLIENTS):
            manager = demo if index % 2 == 0 else admin
            client = Client.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                source=source,
                status=rng.choice(Client.Status.values),
                manager=manager,
            )

            for _ in range(rng.randint(1, 3)):
                Interaction.objects.create(
                    client=client,
                    type=rng.choice(Interaction.Type.values),
                    happened_at=now - timedelta(days=rng.randint(0, 20), hours=rng.randint(1, 10)),
                    comment="Обсудили услуги и удобное время визита",
                )

            if index < len(DEALS):
                title, amount = DEALS[index]
                stage = rng.choice(Deal.Stage.values)
                deal = Deal.objects.create(
                    title=title,
                    client=client,
                    manager=manager,
                    amount=amount,
                    stage=stage,
                    lost_reason="Выбрала другой салон" if stage == Deal.Stage.LOST else "",
                )
            else:
                deal = None

            Task.objects.create(
                title=rng.choice(TASKS),
                client=client,
                deal=deal,
                assignee=manager,
                due_at=now + timedelta(days=rng.randint(-2, 5), hours=rng.randint(1, 8)),
                priority=rng.choice(Task.Priority.values),
            )

        self.stdout.write(self.style.SUCCESS(f"Создано клиентов: {len(CLIENTS)}. Вход: demo"))