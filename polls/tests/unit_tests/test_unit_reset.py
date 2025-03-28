from django.contrib.auth.hashers import make_password,check_password
from django.test import TestCase

from Methods.reset import Reset
from Methods.Verification import VerifyAccount
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
            password=make_password("testpassword"),
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
        #Test that email is not blank
        self.assertTrue(self.reset.email_not_blank("test@example.com"))
        self.assertFalse(self.reset.email_not_blank(""))

    def test_email_find(self):
        #Test to see if email is in the database
        self.assertTrue(self.reset.email_find("testuser@example.com"))
        self.assertFalse(self.reset.email_find("nonexistent@example.com"))

    def test_valid_email_form(self):
        #Test if the email is valid
        self.assertTrue(self.reset.valid_email_form("valid@example.com"))
        self.assertFalse(self.reset.valid_email_form("invalid-email"))

    def test_pass_exact(self):
        #Test if the passwords match
        self.assertTrue(self.reset.pass_exact("password123", "password123"))
        self.assertFalse(self.reset.pass_exact("password123", "differentpassword"))

    def test_pass_maximum(self):
        #Test if the password is more than 0 characters and less than 51 characters
        self.assertTrue(self.reset.pass_maximum("shortpassword"))
        self.assertFalse(self.reset.pass_maximum("a" * 51))  # More than 50 characters
        self.assertFalse(self.reset.pass_maximum(""))

    def test_set_password(self):
        #Test if the password is successfully updated
        new_password = "newpassword123"
        self.reset.set_password(self.user.email, new_password)
        self.user.refresh_from_db()
        self.assertTrue(check_password(new_password,encoded=self.user.password))

    def test_pass_not_blank(self):
        #Test if the password is blank
        self.assertTrue(self.reset.pass_not_blank("nonemptypassword"))
        self.assertFalse(self.reset.pass_not_blank(""))

    def test_authenticate(self):
        #Check if the email is valid
        self.assertTrue(self.reset.authenticate_email("testuser@example.com"))
        self.assertFalse(self.reset.authenticate_email("invalidemail@example.com"))
        self.assertFalse(self.reset.authenticate_email(""))