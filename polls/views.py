from django.core.validators import EmailValidator
from django.contrib.auth.views import logout_then_login
from django.shortcuts import render
from django.contrib import messages

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from django.core.exceptions import ValidationError

from Methods.Login import Login
from Methods.forms import CreateAccountForm
from polls.models import User
import re

#For resetting password
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm

from Methods.sendgrid_email import send_confirmation_email, send_password_reset_email
from django.contrib.auth import logout

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
        user_email = request.session.get('email')
        if not user_email:
            return redirect('login')
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return redirect('login')
        return render(request, "SettingPage.html", {"user": user})

    def post(self, request):
        user_email = request.session.get('email')
        if not user_email:
            return redirect('login')
        
        try:
            user = User.objects.get(email=user_email)
            
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            
            if phone and phone.strip() and phone.lower() != "none":
                try:
                    user.phone_number = int(phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', ''))
                except ValueError:
                    user.phone_number = None
            else:
                user.phone_number = None
                
            user.save()
            
            if email != user_email:
                request.session['email'] = email
                
            messages.success(request, "Your settings have been updated successfully.")
            return redirect('settings')
            
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "SettingPage.html", {"user": user})


class SignOutView(View):
    def post(self, request):
        logout(request)
        request.session.flush()
        return redirect('login')

#Override auth_views.PasswordResetView
class CustomPasswordResetView(auth_views.PasswordResetView):

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        #put in method where it sends via sendgrid
        getEmail=request.POST.get('email')
        send_password_reset_email(getEmail)
        return super().post(request, *args, **kwargs)