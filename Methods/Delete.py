from polls.models import User
from django.contrib.auth.hashers import check_password
import re
from Methods.Verification import VerifyAccount

#DELETE page
#Send to page that confirms that they understand that they will not be able to retrieve their account
#If they click yes, they get brought to a page that they enter their email and enter their password two times
#if they successfully enter the right email and passwords, the account is deleted and if it is successfully
# deleted, they are redirected to a page that they successfully deleted account and go to login page

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
        if self.authenticate and self.pass_exact(password1,password2):
            self.del_acct_action(email)
            return True
        else:
            return False

