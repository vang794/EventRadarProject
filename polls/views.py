from django.core.validators import EmailValidator
from django.contrib.auth.views import logout_then_login
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from django.core.exceptions import ValidationError

from Methods.Login import Login
from Methods.forms import CreateAccountForm
from polls.models import User
import re

from Methods.change_account_details import change_account_details  # Import function
from django.contrib import messages


# Create your views here.
class LoginAuth(View):

    def get(self, request):
        request.session.pop('id', None)  # Remove user ID from session
        return render(request, "login.html")

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Initialize errors dictionary
        errors = {}

        login = Login()
        # Check if fields are blank
        if not login.isNotBlank(email, password):
            return render(request, "login.html", {"error": "Invalid email or password"})
        elif login.authenticate(email, password):
                user = User.objects.get(email=email)
                request.session['email'] = user.email
                return redirect("homepage")
        else:
            return render(request, "login.html", {"error": "Invalid email or password"})  # Show error message
class CreateAcct(View):
    def get(self, request):
        form = CreateAccountForm()  # Create an empty form instance
        return render(request, "create_account.html", {"form": form})

    def post(self, request):
        # Extract form data
        user_id = request.POST.get('id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phonenumber = request.POST.get('phonenumber')

        # Initialize errors dictionary
        errors = {}

        # Check if fields are blank
        if not user_id:
            errors['id'] = ["ID field can't be blank."]
        if not first_name:
            errors['first_name'] = ["First Name field can't be blank."]
        if not last_name:
            errors['last_name'] = ["Last Name field can't be blank."]
        if not email:
            errors['email'] = ["Email field can't be blank."]
        if not password:
            errors['password'] = ["Password field can't be blank."]
        if not phonenumber:
            errors['phonenumber'] = ["Phone number field can't be blank."]

        # Validate user ID length
        if len(user_id) > 20:
            errors['id'] = ["ID cannot be more than 20 characters."]

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            errors['email'] = ["This email is already in use."]
        else:
            # Validate email format
            try:
                EmailValidator()(email)
            except ValidationError:
                errors['email'] = ["Enter a valid email address."]

        # Check if the phone number is in a valid format (10 digits)
        if phonenumber:
            phone_pattern = re.compile(r'^\d{10}$')  # Adjust this regex to fit your phone number format
            if not phone_pattern.match(phonenumber):
                errors['phonenumber'] = ["Enter a valid 10-digit phone number."]

        if errors:
            return render(request, "create_account.html", {"errors": errors, "user_data": request.POST})

        # Create a new user if no errors
        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phonenumber,
            role='User'  # Default role is User
        )
        user.save()

        return redirect("login")
class HomePage(View):
    #Homepage
    def get(self, request):
        return render(request, "homepage.html")

    def post(self, request):
        pass
class SettingPage(View):
    def get(self, request):
        return render(request, "SettingPage.html")

    def post(self, request):
        if "logout" in request.POST:
            logout_then_login(request)
            return redirect('login')  # Redirects to the root URL (login page)
        
        if "update_email" in request.POST:
            new_email = request.POST.get("email") #clicked on
            if new_email: #user entered something
                result = change_account_details(request.user, new_email=new_email)
                if result: 
                    return render(request, "SettingPage.html", {"success": "Your email has been updated successfully"})
                else:
                    return render(request, "SettingPage.html", {"error": "Failed to update your email"})

        elif "update_username" in request.POST:
            new_username = request.POST.get("username")
            if new_username:
                result = change_account_details(request.user, new_username=new_username)
                if result: 
                    return render(request, "SettingPage.html", {"success": "Your username has been updated successfully"})
                else:
                    return render(request, "SettingPage.html", {"error": "Failed to update your username"})

        elif "update_first_name" in request.POST:
            new_first_name = request.POST.get("first_name")
            if new_first_name:
                result = change_account_details(request.user, new_first_name=new_first_name)
                if result: 
                    return render(request, "SettingPage.html", {"success": "Your first name has been updated successfully"})
                else:
                    return render(request, "SettingPage.html", {"error": "Failed to update your first name"})

        elif "update_last_name" in request.POST:
            new_last_name = request.POST.get("last_name")
            if new_last_name:
                result = change_account_details(request.user, new_last_name=new_last_name)
                if result: 
                    return render(request, "SettingPage.html", {"success": "Your last name has been updated successfully"})
                else:
                    return render(request, "SettingPage.html", {"error": "Failed to update your last name"})

        #reloads page if there was an update
        if account_details_changed:
            return redirect("settings")


class sign_out:
    def get(self,request):
        pass
    def post(self,request):
        pass