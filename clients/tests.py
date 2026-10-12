from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .forms import ClientForm
from .models import Client, Interaction, normalize_phone

User = get_user_model()


class NormalizePhoneTests(SimpleTestCase):
    def test_formats_are_normalized(self):
        for raw in ["87071234567", "+7 707 123 45 67", "8 (707) 123-45-67", "7071234567"]:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_phone(raw), "+77071234567")

    def test_invalid_phone_raises(self):
        for raw in ["123", "874766696054", ""]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValidationError):
                    normalize_phone(raw)


class ClientValidationTests(TestCase):
    def test_duplicate_phone_in_other_format_is_rejected(self):
        admin = User.objects.create_user("admin", password="pass", is_staff=True)
        Client.objects.create(first_name="Алмас", phone="+77071234567")
        form = ClientForm(
            data={"first_name": "Дубль", "phone": "8 707 123 45 67", "status": "lead"},
            user=admin,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_interaction_in_future_is_invalid(self):
        customer = Client.objects.create(first_name="Тест", phone="+77070000000")
        interaction = Interaction(client=customer, happened_at=timezone.now() + timedelta(days=1))
        with self.assertRaises(ValidationError):
            interaction.full_clean()


class ClientAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("admin", password="pass", is_staff=True)
        cls.manager = User.objects.create_user("manager", password="pass")
        cls.other = User.objects.create_user("other", password="pass")
        cls.own_client = Client.objects.create(
            first_name="Свой", phone="+77010000001", manager=cls.manager
        )
        cls.foreign_client = Client.objects.create(
            first_name="Чужой", phone="+77010000002", manager=cls.other
        )

    def test_login_required(self):
        response = self.client.get(reverse("clients:list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('clients:list')}")

    def test_manager_sees_only_own_clients(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(list(response.context["clients"]), [self.own_client])

    def test_admin_sees_all_clients(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(response.context["paginator"].count, 2)

    def test_manager_gets_404_for_foreign_client(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("clients:detail", args=[self.foreign_client.pk]))
        self.assertEqual(response.status_code, 404)

    def test_manager_becomes_owner_even_if_other_manager_is_sent(self):
        self.client.force_login(self.manager)
        self.client.post(
            reverse("clients:create"),
            {"first_name": "Новый", "phone": "8 701 000 00 03", "status": "lead", "manager": self.other.pk},
        )
        created = Client.objects.get(phone="+77010000003")
        self.assertEqual(created.manager, self.manager)


class ClientApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("admin", password="pass", is_staff=True)
        cls.manager = User.objects.create_user("manager", password="pass")
        cls.other = User.objects.create_user("other", password="pass")
        cls.own_client = Client.objects.create(
            first_name="Свой", phone="+77010000001", manager=cls.manager
        )
        cls.foreign_client = Client.objects.create(
            first_name="Чужой", phone="+77010000002", manager=cls.other
        )

    def setUp(self):
        self.api = APIClient()

    def test_unauthenticated_request_is_rejected(self):
        response = self.api.get("/api/clients/")
        self.assertEqual(response.status_code, 401)

    def test_manager_sees_only_own_clients(self):
        self.api.force_authenticate(self.manager)
        response = self.api.get("/api/clients/")
        self.assertEqual(response.data["count"], 1)

    def test_cannot_create_interaction_for_foreign_client(self):
        self.api.force_authenticate(self.manager)
        response = self.api.post(
            "/api/interactions/",
            {"client": self.foreign_client.pk, "type": "call", "happened_at": timezone.now().isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("client", response.data)

    def test_clients_cannot_be_deleted(self):
        self.api.force_authenticate(self.admin)
        response = self.api.delete(f"/api/clients/{self.own_client.pk}/")
        self.assertEqual(response.status_code, 405)

    def test_duplicate_phone_in_other_format_is_rejected(self):
        self.api.force_authenticate(self.admin)
        response = self.api.post(
            "/api/clients/", {"first_name": "Дубль", "phone": "8 701 000 00 01"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)