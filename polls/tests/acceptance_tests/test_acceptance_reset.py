from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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

    def test_password_reset_request(self):
        #Test if password reset request can be called
        response = self.client.post(reverse('password_reset'), {'email': self.user.email})
        # Check if the user is redirected to the password_reset_done page
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_confirm(self):
        #Test to get uidb64 and token successfully generated
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token_generator = CustomTokenGenerator()
        token = token_generator.make_token(self.user)

        # Construct the URL with the uidb64 and token
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        # Simulate a GET request to the password reset confirm page
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 200)
        

    def test_password_reset_success(self):
        #Test if user can reset password successfully
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token_generator = CustomTokenGenerator()
        token = token_generator.make_token(self.user)

        # Make the url for the password reset confirm page
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        # Simulate a post request with valid password data
        response = self.client.post(reset_url, {'password1': 'newpassword123', 'password2': 'newpassword123'})
        # Check if the user is redirected to the password_reset_complete page
        self.assertRedirects(response, reverse('password_reset_complete'))

        # Verify the password was updated successfully
        self.user.refresh_from_db()
        self.user.password = 'newpassword123'