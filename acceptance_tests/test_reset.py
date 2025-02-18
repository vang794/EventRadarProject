from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User, Roles
from Methods.Login import Login


class LogInAcceptanceTests(TestCase):
    def setUp(self):

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

        #Test from login and then clicking forget password
        #then fill out email
        #then submit button
        #check for email (???)
        #reset pass word
        #check that password is reset (aka not like old password)
