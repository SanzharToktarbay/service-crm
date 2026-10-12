from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clients.models import Client
from deals.models import Deal

User = get_user_model()


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("manager", password="pass")
        other = User.objects.create_user("other", password="pass")
        own = Client.objects.create(first_name="Свой", phone="+77010000001", manager=cls.manager)
        foreign = Client.objects.create(first_name="Чужой", phone="+77010000002", manager=other)
        Deal.objects.create(
            title="Выиграна", client=own, manager=cls.manager, amount=1000, stage=Deal.Stage.WON
        )
        Deal.objects.create(
            title="Отказ", client=own, manager=cls.manager, stage=Deal.Stage.LOST, lost_reason="Дорого"
        )
        Deal.objects.create(
            title="Чужая", client=foreign, manager=other, amount=5000, stage=Deal.Stage.WON
        )

    def test_manager_sees_only_own_stats(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["clients_stats"]["total"], 1)
        self.assertEqual(response.context["deals_stats"]["won_sum"], 1000)
        self.assertEqual(response.context["conversion"], 50)