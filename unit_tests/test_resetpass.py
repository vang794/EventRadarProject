from django.test import TestCase
from polls.models import User

class TestLogin(TestCase):

    def setUp(self):
        # Create a test user before each test
        self.user = User.objects.create(
            email="testuser@example.com",
            password="testpassword"
        )