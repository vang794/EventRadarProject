from polls.models import User
from django.contrib.auth.hashers import check_password
import re
from Methods.Verification import VerifyAccount
#change user into event manager
#if user exists, change role into desired role
class ChangeRole(VerifyAccount):

    def change_account_role(self, user, role):
        #Check if user exists and is not None
        if user is not None:
            self.change_role(user, role)

    def change_role(self, user, role):
        user.role = role  #Update the user's role
        user.save()