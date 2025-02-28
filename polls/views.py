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
import re

#For resetting password
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm


from Methods.change_account_details import change_account_details
from django.shortcuts import get_object_or_404


from Methods.sendgrid_email import send_confirmation_email
from django.contrib.auth import logout

import folium
from folium.plugins import MarkerCluster

import requests

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
class CustomPasswordResetView(auth_views.PasswordResetView):

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        #put in method where it sends via sendgrid
        getEmail=request.POST.get('email')
        send_password_reset_email(getEmail)
        return super().post(request, *args, **kwargs)

class WeatherView(View):
    def get(self, request):
        # Render the weather form template for GET requests
        return render(request, "weather.html")

    def post(self, request):
        api_key = '438802557a5074e655e46b4140076665'  # Move this to settings.py for better security
        location_type = request.POST.get('locationType')
        location_input = request.POST.get('locationInput').strip()

        if not location_input:
            return render(request, "weather.html", {'error': 'Please enter a location.'})

        api_url = f'https://api.openweathermap.org/data/2.5/forecast?appid={api_key}&units=metric'

        try:
            if location_type == 'city':
                api_url += f'&q={location_input}'
            elif location_type == 'zip':
                if not location_input.isdigit() or len(location_input) != 5:
                    return render(request, "weather.html", {'error': 'Invalid zip code format.'})
                api_url += f'&zip={location_input}'
            elif location_type == 'coords':
                lat, lon = map(str.strip, location_input.split(','))
                if not (lat.replace('.', '').isdigit() and lon.replace('.', '').isdigit()):
                    return render(request, "weather.html", {'error': 'Invalid coordinates format.'})
                api_url += f'&lat={lat}&lon={lon}'
            else:
                return render(request, "weather.html", {'error': 'Invalid location type.'})

            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for bad status codes
            weather_data = response.json()
            return render(request, "weather.html", {'weather_data': weather_data})

        except requests.exceptions.RequestException as e:
            return render(request, "weather.html", {'error': f'Failed to fetch weather data: {str(e)}'})