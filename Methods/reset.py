from polls.models import User
from django.contrib.auth.hashers import check_password
import re
from Methods.Verification import VerifyAccount
from django.contrib.auth.hashers import make_password


class Reset(VerifyAccount):

##make sure that the passwords are not the same as before
    ##If password is the same as past password, return true else return false
    def pass_duplicate(self,email,password):
        user = User.objects.filter(email=email).first()

        # If the user exists, check if the provided password matches the stored password
        if user and check_password(password, user.password):
            return True  # Password is the same as the previous one
        return False

    #Returns true if password is 50 or less characters
    def pass_maximum(self,password):
        if self.pass_not_blank(password):
            return 50 >= len(password) > 0
        else:
            return False

    #set password
    def set_password(self, email, password):
        hashed = make_password(password) #hashed
        User.objects.filter(email=email).update(password=hashed)


