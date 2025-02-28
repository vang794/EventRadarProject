from django.test import TestCase

from Methods.reset import Reset
from polls.models import User, Roles
from Methods.Login import Login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from polls.models import User
from django.contrib.auth.views import PasswordResetView
from django import forms


class TestLogin(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            role=Roles.USER
        )
        self.reset = Reset()
    def tearDown(self):
        # Clean up after each test
        self.user.delete()

    #Test that the correct type of email goes in
    def test_correct_email(self):
        self.assertEqual(self.user.email, "testuser@example.com")

    #Test that the email is not blank
    def test_email_not_blank(self):
        """Test that the email_not_blank method correctly identifies blank and non-blank emails."""
        self.assertTrue(self.reset.email_not_blank("test@example.com"))
        self.assertFalse(self.reset.email_not_blank(""))

    def test_email_find(self):
        """Test that the email_find method correctly checks if the email exists in the database."""
        self.assertTrue(self.reset.email_find("testuser@example.com"))
        self.assertFalse(self.reset.email_find("nonexistent@example.com"))

    def test_valid_email_form(self):
        """Test that the valid_email_form method correctly validates email format."""
        self.assertTrue(self.reset.valid_email_form("valid@example.com"))
        self.assertFalse(self.reset.valid_email_form("invalid-email"))

    def test_pass_exact(self):
        """Test that the pass_exact method checks if two passwords match."""
        self.assertTrue(self.reset.pass_exact("password123", "password123"))
        self.assertFalse(self.reset.pass_exact("password123", "differentpassword"))

    def test_pass_maximum(self):
        """Test that the pass_maximum method checks if the password is within the maximum length."""
        self.assertTrue(self.reset.pass_maximum("shortpassword"))
        self.assertFalse(self.reset.pass_maximum("a" * 51))  # More than 50 characters
        self.assertFalse(self.reset.pass_maximum(""))

    def test_set_password(self):
        """Test that the set_password method correctly updates the password."""
        new_password = "newpassword123"
        self.reset.set_password(self.user.email, new_password)
        self.user.refresh_from_db()
        self.assertTrue(self.user.password==new_password)

    def test_pass_not_blank(self):
        """Test that the pass_not_blank method checks if the password is blank."""
        self.assertTrue(self.reset.pass_not_blank("nonemptypassword"))
        self.assertFalse(self.reset.pass_not_blank(""))

    def test_authenticate(self):
        """Test that the authenticate method checks email validity."""
        self.assertTrue(self.reset.authenticate("testuser@example.com"))
        self.assertFalse(self.reset.authenticate("invalidemail@example.com"))
        self.assertFalse(self.reset.authenticate(""))