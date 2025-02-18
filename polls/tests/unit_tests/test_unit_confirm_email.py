from django.test import TestCase
from django.urls import reverse
from django.core import mail
from polls.models import Roles
from Methods.sendgrid_email import WELCOME_EMAIL_BODY_TEMPLATE, WELCOME_EMAIL_SUBJECT

class ConfirmEmailTests(TestCase):
    def test_confirmation_email_sent_on_signup(self):
        initial_email_count = len(mail.outbox)
        
        form_data = {
            'username': 'confirmuser',
            'first_name': 'Confirm',
            'last_name': 'User',
            'email': 'confirm@example.com',
            'password': 'confirmPass123',
            'phone_number': '1234567890',
            'role': Roles.USER,
        }
        
        response = self.client.post(reverse('create_account'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        
        self.assertEqual(len(mail.outbox), initial_email_count + 1)
        email_msg = mail.outbox[-1]
        self.assertEqual(email_msg.subject, WELCOME_EMAIL_SUBJECT)
        self.assertEqual(email_msg.from_email, "Event Radar <hackba74@uwm.edu>")
        self.assertIn("confirm@example.com", email_msg.to)
        expected_body = WELCOME_EMAIL_BODY_TEMPLATE.format(first_name="Confirm")
        self.assertEqual(email_msg.body, expected_body)

    def test_no_confirmation_email_for_invalid_signup(self):
        """
        Test that no confirmation email is sent if account creation fails.
        """
        initial_email_count = len(mail.outbox)
        
        form_data = {
            'username': '', #username is missing
            'first_name': 'Invalid',
            'last_name': 'User',
            'email': 'invalid@example.com',
            'password': 'pass123',
            'phone_number': '1234567890',
            'role': Roles.USER,
        }
        
        response = self.client.post(reverse('create_account'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), initial_email_count) 