from django.test import TestCase
from polls.models import User, Roles
from Methods.Login import Login
from django.contrib.auth.hashers import make_password



class TestLogin(TestCase):

    def setUp(self):
        # Create a test user before each test
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            password=make_password("testpassword"),
            first_name="Test",
            last_name="User",
            role=Roles.USER
        )
        self.login = Login()
    def tearDown(self):
        # Clean up after each test
        self.user.delete()

    def test_authenticate_valid_user(self):
        #test for base case: correct password and correct email
        result = self.login.authenticate("testuser@example.com", "testpassword")
        self.assertTrue(result)

    def test_authenticate_invalid_email(self):
        #test bad email
        result = self.login.authenticate("invalid@example.com", "testpassword")
        self.assertFalse(result)

    def test_authenticate_invalid_password(self):
        #test authentication
        result = self.login.authenticate("testuser@example.com", "wrongpassword")
        self.assertFalse(result)

    def test_checkemail_valid(self):
        #test that checkemail is the right email
        result = self.login.checkemail("testuser@example.com")
        self.assertTrue(result)

    def test_checkemail_invalid(self):
        #Return false if email isn't in database
        result = self.login.checkemail("none@example.com")
        self.assertFalse(result)

    def test_checkpassword_valid(self):
        #Test if correct password is TRUE
        result = self.login.checkpassword("testuser@example.com", "testpassword")
        self.assertTrue(result)

    def test_checkpassword_invalid(self):
        #Test if checkpassword is wrong and FALSE
        result = self.login.checkpassword("testuser@example.com", "wrongpassword")
        self.assertFalse(result)

    def test_isNotBlank_valid(self):

        #Test if nonblank email and password are TRUE
        result = self.login.isNotBlank("testuser@example.com", "testpassword")
        self.assertTrue(result)

    def test_isNotBlank_invalid_email(self):
        #Test if blank email returns FALSE
        result = self.login.isNotBlank("", "testpassword")
        self.assertFalse(result)

    def test_isNotBlank_invalid_password(self):
        #Test if blank password returns FALSE
        result = self.login.isNotBlank("testuser@example.com", "")
        self.assertFalse(result)

    def test_isNotBlank_both_blank(self):
        #Test that if both blank email and password then return FALSE
        result = self.login.isNotBlank("", "")
        self.assertFalse(result)


