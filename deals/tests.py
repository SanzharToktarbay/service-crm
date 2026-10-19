from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from clients.models import Client

from .models import Deal

User = get_user_model()


class DealModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = Client.objects.create(first_name="Клиент", phone="+77010000001")

    def test_closed_at_is_set_and_cleared(self):
        deal = Deal.objects.create(title="Сделка", client=self.customer, amount=1000)
        self.assertIsNone(deal.closed_at)

        deal.stage = Deal.Stage.WON
        deal.save()
        self.assertIsNotNone(deal.closed_at)

        deal.stage = Deal.Stage.IN_PROGRESS
        deal.save()
        self.assertIsNone(deal.closed_at)

    def test_lost_deal_requires_reason(self):
        deal = Deal(title="Сделка", client=self.customer, stage=Deal.Stage.LOST)
        with self.assertRaises(ValidationError):
            deal.full_clean()


class DealApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("manager", password="pass")
        cls.customer = Client.objects.create(
            first_name="Клиент", phone="+77010000001", manager=cls.manager
        )
        cls.deal = Deal.objects.create(
            title="Сделка", client=cls.customer, manager=cls.manager, lost_reason="Дорого"
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(self.manager)

    def test_lost_without_reason_is_rejected(self):
        response = self.api.post(
            "/api/deals/",
            {"title": "Новая", "client": self.customer.pk, "stage": "lost"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("lost_reason", response.data)

    def test_patch_uses_existing_reason(self):
        response = self.api.patch(f"/api/deals/{self.deal.pk}/", {"stage": "lost"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["closed_at"])

class DealStageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("manager", password="pass")
        cls.other = User.objects.create_user("other", password="pass")
        cls.customer = Client.objects.create(
            first_name="Клиент", phone="+77010000001", manager=cls.manager
        )
        cls.deal = Deal.objects.create(title="Сделка", client=cls.customer, manager=cls.manager)

    def url(self):
        return f"/deals/{self.deal.pk}/stage/"

    def test_manager_moves_own_deal(self):
        self.client.force_login(self.manager)
        response = self.client.post(self.url(), {"stage": "won"})
        self.assertEqual(response.status_code, 200)
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.stage, Deal.Stage.WON)
        self.assertIsNotNone(self.deal.closed_at)

    def test_other_manager_gets_404(self):
        self.client.force_login(self.other)
        response = self.client.post(self.url(), {"stage": "won"})
        self.assertEqual(response.status_code, 404)

    def test_lost_without_reason_is_rejected(self):
        self.client.force_login(self.manager)
        response = self.client.post(self.url(), {"stage": "lost"})
        self.assertEqual(response.status_code, 400)
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.stage, Deal.Stage.NEW)

    def test_unknown_stage_is_rejected(self):
        self.client.force_login(self.manager)
        response = self.client.post(self.url(), {"stage": "hacked"})
        self.assertEqual(response.status_code, 400)

    def test_get_is_not_allowed(self):
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(self.url()).status_code, 405)
