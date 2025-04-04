from django.test import TestCase
from polls.models import User, Roles
from django.contrib.auth.models import User
from polls.models import User
from Methods.Verification import VerifyAccount
class TestDelete(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            role=Roles.USER
        )
        self.verify = VerifyAccount()

        #test delete action

    def test_correct_email(self):
        self.assertEqual(self.user.email, "testuser@example.com")

    #Test that the email is not blank
    def test_email_not_blank(self):
        #Test that email is not blank
        self.assertTrue(self.verify.email_not_blank("test@example.com"))
        self.assertFalse(self.verify.email_not_blank(""))

    def test_email_find(self):
        #Test to see if email is in the database
        self.assertTrue(self.verify.email_find("testuser@example.com"))
        self.assertFalse(self.verify.email_find("nonexistent@example.com"))

    def test_valid_email_form(self):
        #Test if the email is valid
        self.assertTrue(self.verify.valid_email_form("valid@example.com"))
        self.assertFalse(self.verify.valid_email_form("invalid-email"))

    def test_pass_exact(self):
        #Test if the passwords match
        self.assertTrue(self.verify.pass_exact("password123", "password123"))
        self.assertFalse(self.verify.pass_exact("password123", "differentpassword"))

    def test_pass_not_blank(self):
        #Test if the password is blank
        self.assertTrue(self.verify.pass_not_blank("nonemptypassword"))
        self.assertFalse(self.verify.pass_not_blank(""))

