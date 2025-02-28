from django.core.validators import EmailValidator
from django.contrib.auth.views import logout_then_login
from django.shortcuts import render
from django.contrib import messages

# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from django.core.exceptions import ValidationError
from django.utils import timezone


from Methods.Login import Login
from Methods.forms import CreateAccountForm
from polls.models import User, Event
from Methods.sendgrid_reset import CustomTokenGenerator, send_reset_email
from polls.models import User
import re

#For resetting password
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from Methods.reset import Reset
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from Methods.CustomTokenGenerator import CustomTokenGenerator



from Methods.change_account_details import change_account_details
from django.shortcuts import get_object_or_404


from Methods.sendgrid_email import send_confirmation_email
from django.contrib.auth import logout

import folium
from folium.plugins import MarkerCluster

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
            print(f"Form errors: {form.errors}")
            return render(request, "create_account.html", {"form": form})
class HomePage(View):
    def get(self, request):
        # we are just using this location for now
        m = folium.Map(location=[43.0389, -87.9065], zoom_start=12,
                     tiles="cartodbpositron")

        marker_cluster = MarkerCluster().add_to(m)

        # SAMPLE EVENTS! we will use our database for this later
        sample_events = [
            {
                'title': 'Music in the Park',
                'description': 'Live music performance at Veterans Park',
                'latitude': 43.0450,
                'longitude': -87.8900,
                'date': timezone.now() + timezone.timedelta(days=2),
                'category': 'Music'
            },
            {
                'title': 'Food Festival',
                'description': 'Annual food festival with local restaurants',
                'latitude': 43.0381,
                'longitude': -87.9066,
                'date': timezone.now() + timezone.timedelta(days=5),
                'category': 'Food'
            },
            {
                'title': 'Art Exhibition',
                'description': 'Modern art showcase at Milwaukee Art Museum',
                'latitude': 43.0401,
                'longitude': -87.8972,
                'date': timezone.now() + timezone.timedelta(days=3),
                'category': 'Art'
            },
            {
                'title': 'Tech Meetup',
                'description': 'Network with tech professionals in Milwaukee',
                'latitude': 43.0336,
                'longitude': -87.9125,
                'date': timezone.now() + timezone.timedelta(days=7),
                'category': 'Technology'
            }
        ]

        for event in sample_events:
            event_date = event['date'].strftime('%B %d, %Y at %I:%M %p')

            popup_html = f"""
            <div class="event-popup">
                <h3>{event['title']}</h3>
                <p><strong>Date:</strong> {event_date}</p>
                <p><strong>Category:</strong> {event['category']}</p>
                <p>{event['description']}</p>
            </div>
            """

            folium.Marker(
                location=[event['latitude'], event['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=event['title'],
                icon=folium.Icon(icon="info-sign", prefix='fa', color="blue"),
            ).add_to(marker_cluster)

        # circle for the search radius
        folium.Circle(
            location=[43.0389, -87.9065],
            radius=5000,
            color='#3186cc',
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.2,
            tooltip="5km radius"
        ).add_to(m)

        map_html = m._repr_html_()

        return render(request, "homepage.html", {
            'map_html': map_html,
            'sample_events': sample_events
        })

    def post(self, request):
        location = request.POST.get('location', 'Milwaukee')
        radius = request.POST.get('radius', 5)

        try:
            radius = int(radius)
        except ValueError:
            radius = 5

        # rerender the map with new radius, not implemented yet
        return redirect('homepage')

class SettingPage(View):
    def get(self, request):
        email = request.session.get("email")
        if not email:
            return redirect("login") #redirect if unauthenticated

        try:
            user = User.objects.get(email=email)
            return render(request, "SettingPage.html", {"user": user})
        except User.DoesNotExist:
            request.session.flush()
            return redirect("login")

    def post(self, request):
        email = request.session.get("email")
        if not email:
            return redirect("login")  #redirect if unauthenticated

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')

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

        return render(request, "SettingPage.html", {
            "user": user,
            "success": success_message,
            "error": error_message
        })


class SignOutView(View):
    def post(self, request):
        logout(request)
        request.session.flush()
        return redirect('login')


#Override auth_views.PasswordResetView
class PasswordResetView(View):

    def get(self, request):
        return render(request, "password_reset.html")

    def post(self, request):
        #put in method where it sends via sendgrid
        from Methods.sendgrid_reset import send_reset_email
        check = Reset()
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()
        #check that the email is valid
        if user:
            if check.authenticate(email):
                #then get username
                send_reset_email(request,user)
                #if the email is valid and email is send to user email, go to password_reset_done page
                return redirect("password_reset_done")
            else:
                return render(request, "password_reset.html", {"error": "Invalid email"})
        else:
            return render(request, "password_reset.html", {"error": "Invalid email"})
class PasswordResetDoneView(View):
    def get(self, request,):
        return render(request, "password_reset_sent.html")

class PasswordResetConfirmView(View):

    def get(self, request, uidb64, token):
        token_generator = CustomTokenGenerator()
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None

        if user and token_generator.check_token(user, token):
            return render(request, "password_reset_form.html", {"valid": True, "uidb64": uidb64, "token": token})
        else:
            return render(request, "password_reset_form.html", {"valid": False, "error": "Invalid or expired token"})

    def post(self, request, uidb64, token):

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None

        errors = {}
        check = Reset()

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if user:
            # Check if the password meets the length requirements
            if check.pass_maximum(password1):
                # Check if the two passwords match
                if check.pass_exact(password1, password2):
                    check.set_password(user.email, password1)
                    return redirect("password_reset_complete")
                else:
                    errors["match"] = "Passwords don't match"
            else:
                errors["char"] = "Password must be more than 0 characters but less than 51 characters"
        else:
            # Return error if the token is invalid or expired
            errors["token"] = ["Invalid or expired token"]

            # Render error messages
        return render(request, "password_reset_form.html", {"errors": errors, "user_data": request.POST})




