from polls.models import User   #imports user model from poll app

#for email validation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

#method to change user email, username, first name and/or last name 
#phone number is added
def change_account_details(user, new_email=None, new_username=None, new_first_name=None, new_last_name=None, new_phone_number=None):
    updated_fields = [] #keeps track of what is updated

    if new_email:
        if User.objects.filter(email = new_email).exists(): #check if email is already being used
            return False
        try: #check if email is in correct format
            validate_email(new_email)
        except ValidationError:
            return False
        user.email = new_email
        updated_fields.append("email") #add email to list
    if new_username:
        if User.objects.filter(username = new_username).exists(): #if username is already being used
            return False
        if not new_username: #blank username entered
            return False
        if len(new_username) < 3 or len(new_username) > 20:
            return False
        if not all(c.isalnum() or c == "_" for c in new_username): #only allows letters, numbers and underscores
            return False
        user.username = new_username
        updated_fields.append("username")
    if new_first_name:
        if not new_first_name: #blank name entered
            return False
        if len(new_first_name) < 3 or len(new_first_name) > 20: 
            return False
        if not new_first_name.isalpha(): #only allows letters
            return False
        user.first_name = new_first_name
        updated_fields.append("first_name")
    if new_last_name:
        if not new_last_name: #blank name entered
            return False
        if len(new_last_name) < 3 or len(new_last_name) > 20: 
            return False
        if not new_last_name.isalpha(): #only allows letters
            return False
        user.last_name = new_last_name
        updated_fields.append("last_name")
    if new_phone_number:
        digits_only = "".join(c for c in new_phone_number if c.isdigit())  
        if len(new_phone_number) != 10: #only 10 digits
            return False
        digits_only = "".join(c for c in new_phone_number if c.isdigit())  #remove characters
        if len(digits_only) != 10:  #exactly 10 numbers
            return False

        user.phone_number = digits_only  #save only actualy numbers
        updated_fields.append("phone_number")
        
    if updated_fields:
        user.save(update_fields=updated_fields)#only saves updated fields
        user.refresh_from_db() 
        return True
    
    return False
    

