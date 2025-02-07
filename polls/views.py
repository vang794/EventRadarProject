from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
#from Methods.Login import Login
from Methods.forms import CreateAccountForm
from polls.models import User


# Create your views here.
class LoginAuth(View):

    def get(self, request):
        request.session.pop('id', None)  # Remove user ID from session
        return render(request, "login.html")

    def post(self, request):
        return redirect("homepage")
class CreateAcct(View):
    def get(self, request):
        form = CreateAccountForm()  #Create an empty form instance
        return render(request, "create_account.html", {"form": form})

    def post(self, request):
        """Handle form submission and create a new user."""
        form = CreateAccountForm(request.POST)  # Bind form data
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'User'  # Assign role as User (if role is part of the model)
            user.save()  # Save user to the database
            return redirect("login")  # Redirect to login page after success

        # If form is invalid, re-render the page with errors
        return render(request, "create_account.html", {"form": form})

class HomePage(View):
    """Displays the settings page."""
    def get(self, request):
        return render(request, "homepage.html")

    def post(self, request):
        pass
class SettingsPage(View):
    """Displays the settings page."""
    def get(self, request):
        return render(request, "settings.html")

    def post(self, request):
        if "logout" in request.POST:
            request.session.flush()  # Clears all session data
            return redirect("/")  # Redirects to the root URL (login page)
        return render(request, "settings.html")  # Reload settings page if no logout request

class sign_out:
    def get(self,request):
        pass
    def post(self,request):
        pass