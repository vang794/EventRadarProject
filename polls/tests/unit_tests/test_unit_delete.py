from django.test import TestCase
from polls.models import User, Roles
from django.contrib.auth.models import User
from polls.models import User
from Methods.Delete import DeleteAcct


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
        self.delete = DeleteAcct()

        #test delete action
    def test_delete_User(self):
        #successfully delete an Existing account
        email=self.user.email
        account = User.objects.filter(email=email).first()
        if account:
            account.delete()
        #Then check if account is None
        account = User.objects.filter(email=email).first()
        self.assertIsNone(account)

    def test_delete_None(self):
        #If no account returned, no account is deleted
        non_exist_email="testuser2@example.com"
        self.delete.del_acct_action(non_exist_email)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=non_exist_email)

#Test that delete class successfully inherited verification
#Test that the correct type of email goes in
    def test_correct_email(self):
        self.assertEqual(self.user.email, "testuser@example.com")

    #Test that the email is not blank
    def test_email_not_blank(self):
        #Test that email is not blank
        self.assertTrue(self.delete.email_not_blank("test@example.com"))
        self.assertFalse(self.delete.email_not_blank(""))

    def test_email_find(self):
        #Test to see if email is in the database
        self.assertTrue(self.delete.email_find("testuser@example.com"))
        self.assertFalse(self.delete.email_find("nonexistent@example.com"))

    def test_valid_email_form(self):
        #Test if the email is valid
        self.assertTrue(self.delete.valid_email_form("valid@example.com"))
        self.assertFalse(self.delete.valid_email_form("invalid-email"))

    def test_pass_exact(self):
        #Test if the passwords match
        self.assertTrue(self.delete.pass_exact("password123", "password123"))
        self.assertFalse(self.delete.pass_exact("password123", "differentpassword"))

    def test_pass_not_blank(self):
        #Test if the password is blank
        self.assertTrue(self.delete.pass_not_blank("nonemptypassword"))
        self.assertFalse(self.delete.pass_not_blank(""))


