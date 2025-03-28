from polls.models import User
from django.contrib.auth.hashers import check_password
import re
from Methods.Verification import VerifyAccount

class DeleteAcct(VerifyAccount):
#first: check the email and password
#check that email is not blank
#check email is in database

#make sure passwords match

#make sure password is the password that the email has


#third: delete email IF and ONLY IF the password matches the email and the password and confirmation password are exact same
    #if and only if account is found, delete the account
    #if no account found (gets None) dont delete anything
    def del_acct_action(self,email):
        account=self.find_acct(email)
        if account is not None:
            account.delete()

    def del_acct(self,email,password1,password2):
        if self.authenticate_email and self.pass_exact(password1,password2):
            self.del_acct_action(email)
            return True
        else:
            return False
    def isNotBlank(self, email, password1, password2=None):
        # Check if fields are blank
        if not email and password1 and password2:
            return False
        else:
            return True
