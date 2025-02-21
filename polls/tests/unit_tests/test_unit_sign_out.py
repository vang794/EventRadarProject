from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User, Roles

class SignOutTests(TestCase):

    def setUp(self):
        # Set up a test client and a test user
        self.client = Client()
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            role=Roles.USER
        )
        # Log in the user for testing sign out
        session = self.client.session
        session['email'] = self.user.email
        session.save()

    def tearDown(self):
        # Clean up after each test
        self.user.delete()

    def test_sign_out_success(self):
        """Test that a logged-in user can successfully sign out"""
        response = self.client.post(reverse('sign_out'))
        self.assertRedirects(response, reverse('login'))  # Should redirect to login page

    def test_session_clear_on_sign_out(self):
        """Test that the session is cleared on sign out"""
        self.client.post(reverse('sign_out'))
        session = self.client.session
        self.assertNotIn('email', session)  # Email should be removed from session

    def test_no_email_in_session_after_sign_out(self):
        """Ensure no email is in session after sign out"""
        self.client.post(reverse('sign_out'))
        self.assertIsNone(self.client.session.get('email'))  # Session email should be None

    def test_unauthenticated_user_redirect(self):
        """Test that unauthenticated user is redirected to login page"""
        # Clear session to simulate unauthenticated user
        self.client.session.flush()
        response = self.client.get(reverse('setting_page'))
        self.assertRedirects(response, reverse('login'))  # Should redirect to login page
