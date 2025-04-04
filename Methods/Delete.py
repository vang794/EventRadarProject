from polls.models import User
from django.contrib.auth.hashers import check_password
import re
from Methods.Verification import VerifyAccount

class DeleteAcct(VerifyAccount):
    def del_acct_action(self,email):
        account=self.find_acct(email)
        if account is not None:
            account.delete()

    def del_acct(self,email,password1,password2):
        if self.authenticate_email(email) and self.pass_exact(password1,password2):
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
