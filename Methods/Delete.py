from polls.models import User
from django.contrib.auth.hashers import check_password
import re
from Methods.Verification import VerifyAccount

class DeleteAcct(VerifyAccount):
    def del_acct_action(self,email):
        account=self.find_acct(email)
        if account is not None:
            account.delete()
    #check that the password matches account password
    def pass_verif(self,email,password):
        account = self.find_acct(email)
        acct_password= account.password
        return check_password(password,acct_password)


    def del_acct(self,email,password1,password2):
        if self.authenticate_email(email) and self.pass_exact(password1,password2) and self.pass_verif(email,password1):
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
