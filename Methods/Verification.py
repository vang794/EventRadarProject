from polls.models import User
from django.contrib.auth.hashers import check_password
import re

class VerifyAccount:
    def authenticate(self, email):
        return self.email_not_blank(email) and self.email_find(email) and self.valid_email_form(email)

        # Check if fields are blank
        # If email is not blank, return true.

    def email_not_blank(self, email):
        if not email:
            return False
        return True

        # See if email is in database
    def email_find(self, email):
        return User.objects.filter(email=email).exists()

        # Check for valid email form
        # returns true (if email form) or false (if not)
    def valid_email_form(self, email):
        email = email
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
        return bool(valid)

        # make sure that the passwords match exactly
    def pass_exact(self, password1, password2):
        return password1 == password2

    #check that password is not blank
    def pass_not_blank(self,password):
        if not password:
            return False
        return True

    #get account by email
    def find_acct(self,email):
        if self.email_find(email):
            return User.objects.filter(email=email)

