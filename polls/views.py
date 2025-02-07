from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
#from Methods.Login import Login
from Methods.forms import CreateAccountForm
from polls.models import User

class CreateAcct(View):
    def get(self, request):
        form = CreateAccountForm()  # Create an empty form instance
        return render(request, "create_account.html", {"form": form})

    def post(self, request):
        """Handle form submission and create a new user."""
        form = CreateAccountForm(request.POST)  # Bind form data
        if form.is_valid():
            form.save()  # Save user to the database
            return redirect("login")  # Redirect to login page after success

        # If form is invalid, re-render the page with errors
        return render(request, "create_account.html", {"form": form})
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