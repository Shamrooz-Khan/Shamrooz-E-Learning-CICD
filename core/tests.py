from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser


class BasicSystemTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.student = CustomUser.objects.create_user(
            username="teststudent",
            email="student@test.com",
            password="TestPassword123",
            role="student"
        )

    def test_user_creation(self):
        self.assertEqual(self.student.username, "teststudent")
        self.assertEqual(self.student.role, "student")

    def test_login(self):
        login = self.client.login(
            username="teststudent",
            password="TestPassword123"
        )

        self.assertTrue(login)

    def test_home_page(self):
        response = self.client.get("/")

        self.assertIn(response.status_code, [200, 302])