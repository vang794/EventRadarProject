from django.test import TestCase
from django.urls import reverse
from django.core import mail
from polls.models import Roles


class ConfirmEmailAcceptanceTests(TestCase):
    def test_new_user_receives_welcome_email_after_registration(self):
        """
        Test scenario: A new user signs up through the website and receives
        a welcome email confirming their registration.
        """
        response = self.client.get(reverse('create_account'))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@example.com',
            'password': 'SecurePass123',
            'phone_number': '1234567890',
            'role': Roles.USER.value,
        }
        response = self.client.post(reverse('create_account'), form_data)

        self.assertRedirects(response, reverse('login'))

        self.assertEqual(len(mail.outbox), 1)
        welcome_email = mail.outbox[0]
        self.assertIn('john.smith@example.com', welcome_email.to)
        self.assertIn('Welcome to Event Radar', welcome_email.subject)
        self.assertIn('John', welcome_email.body)  # Personalized with first name

    def test_user_sees_error_and_receives_no_email_when_registration_fails(self):
        """
        Test scenario: A user attempts to register with invalid information
        and doesn't receive a welcome email.
        """
        self.client.get(reverse('create_account'))

        invalid_form_data = {
            'username': '',  # missing username
            'email': 'invalid@example.com',
            # missing other required fields
        }
        response = self.client.post(reverse('create_account'), invalid_form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        self.assertEqual(len(mail.outbox), 0)

    def test_multiple_users_receive_correct_personalized_emails(self):
        """
        Test scenario: Multiple users register in succession and each receives
        their own personalized welcome email.
        """
        users = [
            {
                'username': 'user1',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice@example.com',
                'password': 'Pass123!',
                'phone_number': '1111111111',
                'role': Roles.USER.value,
            },
            {
                'username': 'user2',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'email': 'bob@example.com',
                'password': 'Pass456!',
                'phone_number': '2222222222',
                'role': Roles.USER.value,
            }
        ]

        for user_data in users:
            self.client.post(reverse('create_account'), user_data)

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('alice@example.com', mail.outbox[0].to)
        self.assertIn('Alice', mail.outbox[0].body)
        self.assertIn('bob@example.com', mail.outbox[1].to)
        self.assertIn('Bob', mail.outbox[1].body) 