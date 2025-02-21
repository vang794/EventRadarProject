from django.test import TestCase

from Methods.reset import CustomPasswordResetForm
from polls.models import User, Roles
from Methods.Login import Login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from polls.models import User
from django.contrib.auth.views import PasswordResetView
from django import forms

#Reset classes will inherit from PasswordResetView (Django Authorization System)

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
    def tearDown(self):
        # Clean up after each test
        self.user.delete()

    #Test that the correct type of email goes in
    def test_correct_email(self):
        self.assertEqual(self.user.email, "testuser@example.com")

    #Test an incomplete email (Not correct format)
    def test_incomplete_email(self):
        with self.assertRaises(forms.ValidationError):
            CustomPasswordResetForm(data={"email": "invalidemail"}).is_valid()

    #Test that the email is not case sensitive
    def test_email_not_case_sensitive(self):
        form = CustomPasswordResetForm(data={"email": "test@EXAMPLE.COM"})
        self.assertTrue(form.is_valid())
    #Test if the email retrieved is in all capitals
    def test_email_all_capitals(self):
        form = CustomPasswordResetForm(data={"email": "TEST@EXAMPLE.COM"})
        self.assertTrue(form.is_valid())

    #Test if the email has some capitals
    def test_email_some_capitals(self):
        form = CustomPasswordResetForm(data={"email": "TesT@Example.Com"})
        self.assertTrue(form.is_valid())

    #Test if email is in database
    def test_email_in_database(self):
        self.assertTrue(User.objects.filter(email__iexact="testuser@example.com").exists())

    #Test if email is not in database
    def test_email_not_in_database(self):
        form = CustomPasswordResetForm(data={"email": "nonexistent@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)