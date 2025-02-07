from django.test import TestCase
from polls.models import User, Roles


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
            'role': Roles.USER
        }
        response = self.client.post('create', user_data)
        self.assertEqual(response.status_code, 201)

    def test_create_account_missing_required_fields(self):
        """Test creating an account with missing required fields"""
        incomplete_data = {
            'id': 'testuser2',
            'email': 'incomplete@example.com'
        }
        response = self.client.post('create', incomplete_data)
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
            'role': Roles.USER
        }
        response = self.client.post('create', user_data)
        self.assertEqual(response.status_code, 201)

        duplicate_data = user_data.copy()
        duplicate_data['email'] = 'different@example.com'
        response = self.client.post('create', duplicate_data)
        self.assertEqual(response.status_code, 400)