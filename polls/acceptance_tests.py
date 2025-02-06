from django.test import TestCase
from django.urls import reverse
from .models import User, Roles

class CreateAccountAcceptanceTests(TestCase):
    def test_user_can_create_account_through_form(self):
        """test that a user can create an account through the web interface"""
        response = self.client.get(reverse('create_account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/create_account.html')
        
        form_data = {
            'username': 'newuser123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'securepass123',
            'phone_number': '1234567890',
            'role': Roles.User
        }
        
        response = self.client.post(reverse('create_account'), form_data)
        self.assertRedirects(response, reverse('account_created'))
        
        self.assertTrue(User.objects.filter(id='newuser123').exists())
        
    def test_user_sees_error_for_duplicate_username(self):
        """test that appropriate error is shown when trying to create account with existing username"""
        existing_user = {
            'username': 'existinguser',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'password': 'password123',
            'phone_number': '9876543210',
            'role': Roles.User
        }
        self.client.post(reverse('create_account'), existing_user)
        
        duplicate_data = existing_user.copy()
        duplicate_data['email'] = 'different@example.com'
        
        response = self.client.post(reverse('create_account'), duplicate_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'Username already exists')
        
    def test_user_sees_error_for_missing_required_fields(self):
        """Test that appropriate errors are shown when required fields are missing"""
        incomplete_data = {
            'username': 'newuser',
            'email': 'new@example.com'
        }
        
        response = self.client.post(reverse('create_account'), incomplete_data)
        self.assertEqual(response.status_code, 200)
        
        self.assertFormError(response, 'form', 'first_name', 'This field is required')
        self.assertFormError(response, 'form', 'last_name', 'This field is required')
        self.assertFormError(response, 'form', 'password', 'This field is required')
        self.assertFormError(response, 'form', 'phone_number', 'This field is required')
        
    def test_create_account_page_shows_correct_form(self):
        """Test that the create account page shows all required fields"""
        response = self.client.get(reverse('create_account'))
        
        self.assertContains(response, 'Username')
        self.assertContains(response, 'First name')
        self.assertContains(response, 'Last name')
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Phone number')
        self.assertContains(response, 'Role') 