from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User,Roles


class LogInAcceptanceTests(TestCase):
    client= None
    def setUp(self):
        """create a test user and log them in before each test """
        self.client=Client()
        self.user_data = {
            'id': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone_number': '1234567890',
            'role': Roles.USER
        }

        self.client.login(id='testuser', password='testpass123')

    def test_user_can_sign_in(self):
        """Test that user can successfully sign in"""

        # Ensure login page loads correctly
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        # Attempt login using POST request
        resp = self.client.post(reverse("login"), {"id": "testuser", "password": "testpass123"})

        # Ensure the user exists in the database
        user = User.objects.filter(id="testuser").first()
        self.assertIsNotNone(user, "User should exist in the database")

        # Ensure the password corresponds to the stored password
        #!!METHOD FOR CHECKING PASSWORD
        self.assertTrue(check_password("testpass123", user.password), "Password should match the stored password")

        # If login is successful, redirect to home page
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_sign_in_fail(self):
        """test that user uses wrong username or password"""
        # Ensure login page loads correctly
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        # Attempt login with wrong credentials
        resp = self.client.post(reverse("login"), {'id': "tester", 'password': "student123"}, follow=True)
        self.assertEqual(resp.context['error'], "User not found")

        self.assertFalse(check_password("testpass12", user.password), "Password should match the stored password")
