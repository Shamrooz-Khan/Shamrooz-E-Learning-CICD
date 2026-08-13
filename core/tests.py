from django.test import TestCase, Client
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
        """Test that a student user is created correctly."""
        self.assertEqual(self.student.username, "teststudent")
        self.assertEqual(self.student.role, "student")

    def test_login(self):
        """Test that a registered student can log in."""
        login = self.client.login(
            username="teststudent",
            password="TestPassword123"
        )

        self.assertTrue(login)

    def test_student_dashboard_access(self):
        """Test that a logged-in student can access the dashboard."""
        self.client.login(
            username="teststudent",
            password="TestPassword123"
        )

        response = self.client.get("/student/dashboard/")

        self.assertEqual(response.status_code, 200)