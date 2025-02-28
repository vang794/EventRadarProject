from polls.models import User
from django.contrib.auth.hashers import check_password
import re

class Reset:
    def authenticate(self, email):
        return self.email_not_blank(email) and self.email_find(email) and self.valid_email_form(email)

    def email_case(self,email):
        pass

    # Check if fields are blank
    #If email is not blank, return true.
    def email_not_blank(self,email):

        if not email:
            return False
        return True

#See if email is in database
    def email_find(self,email):
        return User.objects.filter(email=email).exists()
#Check for valid email form
    #returns true (if email form) or false (if not)
    def valid_email_form(self,email):
        email = email
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
        return bool(valid)
#make sure that the passwords match exactly
    def pass_exact(self,password1,password2):
        return password1 == password2

##make sure that the passwords are not the same as before
    ##If password is the same as past password, return true else return false
    def pass_duplicate(self,email,password):
        ##Returns user, None if no user
        user = User.objects.filter(email=email).first()
        ##if it is not None and the passwords are same, returns true
        if user and check_password(password, user.password):
            return True
        return False
#Returns true if password is 50 or less characters
    def pass_maximum(self,password):
        if self.pass_not_blank(password):
            return 50 >= len(password) > 0
        else:
            return False

    #set password
    def set_password(self,email, password):
        User.objects.filter(email=email).update(password=password)

    #check that password is not blank
    def pass_not_blank(self,password):
        if not password:
            return False
        return True
