from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clients.models import Client
from deals.models import Deal

from .models import Task

User = get_user_model()


class TaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("manager", password="pass")
        cls.other = User.objects.create_user("other", password="pass")
        cls.customer = Client.objects.create(
            first_name="Клиент", phone="+77010000001", manager=cls.manager
        )
        cls.deal = Deal.objects.create(title="Сделка", client=cls.customer, manager=cls.manager)

    def make_task(self, **kwargs):
        data = {
            "title": "Задача",
            "assignee": self.manager,
            "due_at": timezone.now() + timedelta(days=1),
        }
        data.update(kwargs)
        return Task.objects.create(**data)

    def test_is_overdue(self):
        past = timezone.now() - timedelta(hours=1)
        self.assertTrue(self.make_task(due_at=past).is_overdue)
        self.assertFalse(self.make_task().is_overdue)
        self.assertFalse(self.make_task(due_at=past, is_done=True).is_overdue)

    def test_client_is_taken_from_deal(self):
        task = self.make_task(deal=self.deal)
        self.assertEqual(task.client, self.customer)

    def test_done_at_is_set_and_cleared(self):
        task = self.make_task()
        task.is_done = True
        task.save()
        self.assertIsNotNone(task.done_at)

        task.is_done = False
        task.save()
        self.assertIsNone(task.done_at)

    def test_manager_cannot_toggle_foreign_task(self):
        task = self.make_task(assignee=self.other)
        self.client.force_login(self.manager)
        response = self.client.post(reverse("tasks:toggle", args=[task.pk]))
        self.assertEqual(response.status_code, 404)

    def test_toggle_ignores_external_next_url(self):
        task = self.make_task()
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("tasks:toggle", args=[task.pk]), {"next": "https://evil.example.com/"}
        )
        self.assertRedirects(response, reverse("tasks:list"))
        task.refresh_from_db()
        self.assertTrue(task.is_done)