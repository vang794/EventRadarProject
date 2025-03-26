from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User, Roles

class DeleteAcceptanceTests(TestCase):
    def setUp(self):
        """Create a test user before each test."""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone_number': 1234567890,
            'role': Roles.USER
        }

        # Create user instance and save to database
        self.user = User.objects.create(**self.user_data)

        #User can successfully delete account
        def test_user_can_delete(self):
            pass

        #User does not successfully delete account
        def test_user_cant_delete(self):
            pass

