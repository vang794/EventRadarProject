from django.test import TestCase
from django.urls import reverse
from polls.models import User, Roles
from Methods.forms import CreateAccountForm


class CreateAccountTests(TestCase):
    def test_create_valid_user_account(self):
        """Test creating a user account with valid data"""
        user_data = {
            'username': 'testuser1',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'securepass123',
            'phone_number': 1234567890,
            'role': Roles.USER
        }
        form = CreateAccountForm(data=user_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser1')
        self.assertEqual(user.email, 'john@example.com')

    def test_create_account_missing_required_fields(self):
        """Test creating an account with missing required fields"""
        incomplete_data = {
            'username': 'testuser2',
            'email': 'incomplete@example.com'
        }
        form = CreateAccountForm(data=incomplete_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('password', form.errors)
        self.assertIn('role', form.errors)

    def test_create_account_duplicate_username(self):
        """Test creating an account with an existing username"""
        User.objects.create(username='existinguser', email='test@example.com', password='password123')

        user_data = {
            'username': 'existinguser',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'password': 'password123',
            'phone_number': 9876543210,
            'role': Roles.USER
        }

        form = CreateAccountForm(data=user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['User with this Username already exists.'])