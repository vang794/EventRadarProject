from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User, Roles
from Methods.Login import Login


class LogInAcceptanceTests(TestCase):
    def setUp(self):
        """Create a test user before each test."""
        self.client = Client()
        self.user_data = {
            'id': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone_number': 1234567890,
            'role': Roles.USER
        }

        # Create user instance and save to database
        self.user = User.objects.create(**self.user_data)

        # Initialize login handler
        self.login = Login()

    def test_user_can_sign_in(self):
        """Test that a user can successfully sign in."""

        # Ensure login page loads correctly
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        # Attempt login using POST request
        response = self.client.post(reverse("login"), {"email": "test@example.com", "password": "testpass123"}, follow=True)

        # Ensure user exists in the database
        user = User.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(user, "User should exist in the database")

        # Ensure the password is correct
        self.assertTrue(self.login.checkpassword("test@example.com", "testpass123"),
                        "Password should match the stored password")

        # Check if the response redirects to settings page
        self.assertRedirects(response, reverse("homepage"))

    def test_sign_in_fail(self):
        """Test login failure with incorrect credentials."""

        # Ensure login page loads correctly
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        # Login with wrong username and password
        response = self.client.post(reverse("login"), {'id': "wronguser", 'password': "wrongpass"}, follow=True)

        # Make sure authentication fails
        self.assertFalse(self.login.checkpassword("wronguser", "wrongpass"),
                         "Authentication should fail with incorrect credentials")