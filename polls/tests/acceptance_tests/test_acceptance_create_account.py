from django.test import TestCase
from django.urls import reverse
from polls.models import User, Roles
from Methods.forms import CreateAccountForm


class CreateAccountAcceptanceTests(TestCase):
    def test_user_can_create_account_through_form(self):
        """test that a user can create an account through the web interface"""
        response = self.client.get(reverse('create_account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_account.html')

        form_data = {
            'username': 'newuser123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'securepass123',
            'phone_number': '1234567890',
            'role': Roles.USER
        }

        response = self.client.post(reverse('create_account'), form_data)
        self.assertRedirects(response, reverse('login'))

        self.assertTrue(User.objects.filter(username='newuser123').exists())

    def test_user_sees_error_for_duplicate_username(self):
        """test that appropriate error is shown when trying to create account with existing username"""
        User.objects.create(username='existinguser', email='test@example.com', password='testpassword')

        duplicate_data = {
            'username': 'existinguser',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'different@example.com',
            'password': 'password123',
            'phone_number': '9876543210',
            'role': Roles.USER
        }

        response = self.client.post(reverse('create_account'), duplicate_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['User with this Username already exists.'])


    def test_user_sees_error_for_missing_required_fields(self):
        """Test that appropriate errors are shown when required fields are missing"""
        incomplete_data = {
            'username': 'newuser',
            'email': 'new@example.com'
        }

        response = self.client.post(reverse('create_account'), incomplete_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('password', form.errors)
        self.assertIn('role', form.errors)


    def test_create_account_page_shows_correct_form(self):
        """Test that the create account page shows all required fields"""
        response = self.client.get(reverse('create_account'))

        self.assertContains(response, 'Username:')
        self.assertContains(response, 'First name:')
        self.assertContains(response, 'Last name:')
        self.assertContains(response, 'Email:')
        self.assertContains(response, 'Password:')
        self.assertContains(response, 'Phone number:')
        self.assertContains(response, 'Role:')