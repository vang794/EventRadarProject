from django.test import TestCase
from django.urls import reverse
from polls.models import Roles

class SignOutAcceptanceTests(TestCase):
    def setUp(self):
        """crreate a test user and log them in before each test """
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone_number': '1234567890',
            'role': Roles.User
        }
        self.client.post(reverse('create_account'), self.user_data)
        self.client.login(username='testuser', password='testpass123')

    def test_user_can_sign_out(self):
        """Test that a loggedin user can successfully sign out"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('sign_out'))
        self.assertRedirects(response, reverse('login'))
        
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_sign_out_clears_session(self):
        """test that signing out clears the users session"""
        self.assertIn('_auth_user_id', self.client.session)
        
        self.client.get(reverse('sign_out'))
        
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_signed_out_user_redirected_to_login(self):
        """test that a signeout user is redirected to login when accessing protected pages"""
        self.client.get(reverse('sign_out'))
        
        protected_urls = ['home', 'profile', 'dashboard']
        
        for url in protected_urls:
            response = self.client.get(reverse(url))
            self.assertRedirects(
                response, 
                f"{reverse('login')}?next={reverse(url)}"
            )

    def test_already_signed_out_user_can_access_sign_out(self):
        """Test that accessing signout when already signed out doesnt cause errors"""
        self.client.get(reverse('sign_out'))
        
        response = self.client.get(reverse('sign_out'))
        self.assertRedirects(response, reverse('login'))
