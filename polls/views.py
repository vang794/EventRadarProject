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

#For resetting password
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm

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
        return render(request, "SettingPage.html")

    def post(self, request):
        logout_then_login(request)
        return redirect('login')  # Redirects to the root URL (login page)


class sign_out:
    def get(self,request):
        pass
    def post(self,request):
        pass

#Override auth_views.PasswordResetView
#class CustomPasswordResetView(auth_views.PasswordResetView):

    #def get(self, request, *args, **kwargs):
        #return super().get(request, *args, **kwargs)

    # Optional: Customizing the POST method
   # def post(self, request, *args, **kwargs):
        #put in method where it sends via sendgrid
        #getEmail=request.POST.get('email')
        #send_password_reset_email(getEmail)
        #return super().post(request, *args, **kwargs)