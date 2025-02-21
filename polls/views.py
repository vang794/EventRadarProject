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

from Methods.change_account_details import change_account_details 
from django.shortcuts import get_object_or_404



from Methods.sendgrid_email import send_confirmation_email

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
        form = CreateAccountForm()
        return render(request, "create_account.html", {"form": form})

    def post(self, request):
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'User'
            user.save()
            send_confirmation_email(user)
            return redirect("login")
        else:
            return render(request, "create_account.html", {"form": form})
class HomePage(View):
    #Homepage
    def get(self, request):
        return render(request, "homepage.html")

    def post(self, request):
        pass
class SettingPage(View):
    def get(self, request):
        #user_id = request.session.get("user_id")
        #if not user_id:
            #return redirect("login") #redirect if unauthenticated
        return render(request, "SettingPage.html")
        
    def post(self, request):
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login") #redirect if unauthenticated

        user = get_object_or_404(User, id=user_id)

        if "logout" in request.POST:
            request.session.flush()
            return redirect('login')  # Redirects to the root URL (login page)
        
        success_message = None
        error_message = None

        if "update_email" in request.POST:
            new_email = request.POST.get("email") #clicked on
            if new_email: #user entered something
                result = change_account_details(user, new_email=new_email)
                if result: 
                    success_message = "Your email has been updated successfully"
                else:
                    error_message = "Failed to update email"

        elif "update_username" in request.POST:
            new_username = request.POST.get("username")
            if new_username:
                result = change_account_details(user, new_username=new_username)
                if result: 
                    success_message = "Your username has been updated successfully"
                else:
                    error_message = "Failed to update your username"

        elif "update_first_name" in request.POST:
            new_first_name = request.POST.get("first_name")
            if new_first_name:
                result = change_account_details(user, new_first_name=new_first_name)
                if result: 
                    success_message = "Your first name has been updated successfully"
                else:
                    error_message = "Failed to update your first name"
                    
        elif "update_last_name" in request.POST:
            new_last_name = request.POST.get("last_name")
            if new_last_name:
                result = change_account_details(user, new_last_name=new_last_name)
                if result: 
                    success_message = "Your last name has been updated successfully"
                else:
                    error_message = "Failed to update your last name"

        if success_message:
            return redirect("settings")

        return render(request, "SettingPage.html", {"success": success_message, "error": error_message})
        


class sign_out:
    def get(self,request):
        pass
    def post(self,request):
        pass