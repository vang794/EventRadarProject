from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from polls.models import User, Roles
from Methods.reset import Reset
from Methods.CustomTokenGenerator import CustomTokenGenerator
from Methods.sendgrid_reset import send_reset_email

class ResetAcceptanceTests(TestCase):
    def setUp(self):
        """Create a test user before each test."""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@gmail.com',
            'password': 'testpass123',
            'phone_number': 1234567890,
            'role': Roles.USER
        }

        # Create user instance and save to database
        self.user = User.objects.create(**self.user_data)

        self.CustomPasswordResetForm = Reset()

    def test_user_success(self):
        #being on page reset
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

        #test of putting in email
        form_data = {
            'email': 'test@gmail.com'
        }
        #email is correct
        response = self.client.post(reverse('password_reset'), form_data)

        self.assertRedirects(response, reverse('password_reset_done'))

        #email sends
        self.assertEqual(len(mail.outbox), 1)
        welcome_email = mail.outbox[0]
        self.assertIn('test@example.com', welcome_email.to)
        self.assertIn('Password Reset on 127.0.0.1:8000', welcome_email.subject)
        #clicking on reset/<uidb64>/<token>/ leads to the reset password page
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': 'testuid', 'token': 'testtoken'})
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 200)

        #entered passwords are correct
        reset_form_data = {
            'new_password1': 'newpassword',
            'new_password2': 'newpassword',
        }
        response = self.client.post(reset_url, reset_form_data)
        self.assertRedirects(response, reverse('password_reset_complete'))

        # Leads to page that tells you that you are done (reset/done/)
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)

