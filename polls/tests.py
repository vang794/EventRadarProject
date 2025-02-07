from django.test import TestCase
from .models import User, Roles
from django.urls import reverse
from django.contrib.auth import get_user_model


class CreateAccountTests(TestCase):
    def test_create_valid_user_account(self):
        """Test creating a user account with valid data"""
        user_data = {
            'id': 'testuser1',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'securepass123',
            'phone_number': 1234567890,
            'role': Roles.User
        }
        response = self.client.post('/create-account/', user_data)
        self.assertEqual(response.status_code, 201)
        
    def test_create_account_missing_required_fields(self):
        """Test creating an account with missing required fields"""
        incomplete_data = {
            'id': 'testuser2',
            'email': 'incomplete@example.com'
        }
        response = self.client.post('/create-account/', incomplete_data)
        self.assertEqual(response.status_code, 400)
        
    def test_create_account_duplicate_username(self):
        """Test creating an account with an existing username"""
        user_data = {
            'id': 'existinguser',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'password': 'password123',
            'phone_number': 9876543210,
            'role': Roles.User
        }
        response = self.client.post('/create-account/', user_data)
        self.assertEqual(response.status_code, 201)
        
        duplicate_data = user_data.copy()
        duplicate_data['email'] = 'different@example.com'
        response = self.client.post('/create-account/', duplicate_data)
        self.assertEqual(response.status_code, 400)


User = get_user_model()
class SignOutTests(TestCase):
    def setUp(self):
        """Set up a test user"""
        self.user = User.objects.create_user(
            id='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpassword123',
            phone_number=1234567890,
            role='User'
        )
        self.client.login(email='test@example.com', password='testpassword123')

    def test_sign_out_success(self):
        """Test if a logged-in user can successfully sign out"""
        response = self.client.post(reverse('sign_out'))

        # Ensure the user is redirected after logout
        self.assertEqual(response.status_code, 302)  # Redirect to 'account_created'
        self.assertRedirects(response, reverse('account_created'))

        # Ensure user is logged out
        response = self.client.get(reverse('settings'))
        self.assertNotIn('_auth_user_id', self.client.session)