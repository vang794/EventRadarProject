import requests
from django.contrib import messages

from math import radians, sin, cos, sqrt, atan2

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
from django.utils import timezone


#Login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import never_cache

from Methods.Application import ApplicationMethods
from Methods.Delete import DeleteAcct
from Methods.Login import Login
from Methods.Verification import VerifyAccount
from Methods.forms import CreateAccountForm

from polls.models import User, POI, Event, SearchedArea, Application, ApplicationStatus, Plan, PlanOrder
from Methods.sendgrid_reset import CustomTokenGenerator, send_reset_email
from EventRadarProject.settings import EVENT_API_KEY
import re

#For resetting password
from django.contrib.auth import views as auth_views, authenticate, login
from django.shortcuts import render
from Methods.reset import Reset
from django.utils.http import urlsafe_base64_decode
from Methods.CustomTokenGenerator import CustomTokenGenerator



from Methods.change_account_details import change_account_details
from django.shortcuts import get_object_or_404


from Methods.sendgrid_email import send_confirmation_email


import folium
from folium import DivIcon
from folium.plugins import MarkerCluster, PolyLineTextPath

from polls.geocoding import GeocodingService
from django.contrib.auth.hashers import make_password

#Mixins
from Methods.SessionLoginMixin import SessionLoginRequiredMixin
from Methods.userPermissions import UserRequiredMixin,AdminManagerRequiredMixin,EventManagerRequiredMixin,AdminRequiredMixin

from polls.api import fetch_pois_from_api
import json

# Create your views here.
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from polls.config.category_mapping import category_mapping
import math
from django.db.models import Max
import time
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginAuth(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'email' in request.session:
            return redirect("homepage")  #If logged in then go to homepage

        response = render(request, "login.html")
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Initialize errors dictionary
        errors = {}

        login_auth = Login()
        # Check if fields are blank
        if not login_auth.isNotBlank(email, password):
            return render(request, "login.html", {"error": "Invalid email or password"})

        elif login_auth.authenticate(email, password):
                user = User.objects.get(email=email)
                request.session['email'] = user.email
                request.session["is_authenticated"] = True
                request.session['role'] = user.role
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
            user.password = make_password(user.password)  #hashes the password
            user.role = 'User'
            user.save()
            send_confirmation_email(user)
            return redirect("login")
        else:
            print(f"Form errors: {form.errors}")
            return render(request, "create_account.html", {"form": form})
class HomePage(SessionLoginRequiredMixin,View):
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):

       #retrieving the start date and end date
        start_date_str = request.session.get('start_date')
        end_date_str = request.session.get('end_date')
        error=None

        start_date = None
        end_date = None

        if start_date_str:
            try:
                start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                start_date = None

        if end_date_str:
            try:
                end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                end_date = None

        radius = request.session.get('radius', 5)
        location_name = request.session.get('location', 'Milwaukee')
        location_coords = request.session.get('location_coords')
        if not location_coords:
            geocoder = GeocodingService()
            location_coords = geocoder.get_coordinates(location_name)
            if not location_coords:
                location_coords = (43.0389, -87.9065)
            request.session['location_coords'] = location_coords
        if isinstance(location_coords, tuple):
            location = list(location_coords)
        else:
            location = location_coords

        logger.info(f"Session location: {request.session.get('location')}, radius: {request.session.get('radius')}, location_coords: {request.session.get('location_coords')}")

        max_searched_radius_data = SearchedArea.objects.filter(
            latitude=location[0],
            longitude=location[1]
        ).aggregate(Max('radius'))

        max_searched_radius = max_searched_radius_data['radius__max']

        if max_searched_radius is not None and radius <= max_searched_radius:
            needs_fetch = False
            logger.info(f"Found previous search for location ({location[0]}, {location[1]}) with max radius {max_searched_radius}. Requested radius {radius} is covered. No fetch needed.")
        else:
            needs_fetch = True
            if max_searched_radius is not None:
                logger.info(f"Largest previous search for location ({location[0]}, {location[1]}) was {max_searched_radius} miles. Requested radius {radius} is larger. Fetch required.")
            else:
                logger.info(f"No previous SearchedArea record found for location ({location[0]}, {location[1]}). Fetch required.")

        logger.info(f"Final decision for needs_fetch: {needs_fetch}")

        pois = self.get_pois_within_radius(location[0], location[1], radius)
        logger.info(f"Displaying {len(pois)} POIs currently in DB within {radius} miles.")
        #Error if start_date is larger than end_date or end-date is less than start date
        if start_date and end_date and start_date > end_date:
            error = "Start date must be before end date"
        elif start_date and end_date and end_date < start_date:
            error = "End date must be after start date"

        system_email = "system@eventradar.local"
        system_user = User.objects.filter(email=system_email).first()
        if not system_user:
            system_user = User.objects.create(
                username="system",
                first_name="System",
                last_name="User",
                email=system_email,
                password="!",
                role="Admin"
            )

        user_events = self.get_events_within_radius2(location[0], location[1], radius, system_user)

        if start_date and end_date:
            user_events = [event for event in user_events if start_date <= event.event_date <= end_date]
        elif start_date:
            user_events = [event for event in user_events if event.event_date >= start_date]
        elif end_date:
            user_events = [event for event in user_events if event.event_date <= end_date]
        # else: user_events already filtered by radius

        categorized_pois = {}
        for poi in pois:
            category = poi.category or "Uncategorized"
            if category not in categorized_pois:
                categorized_pois[category] = []
            categorized_pois[category].append(poi)
        
        sorted_categories = sorted(categorized_pois.keys())
        
        poi_categories = []
        for category in sorted_categories:
            sorted_pois = sorted(
                categorized_pois[category],
                key=lambda e: self.calculate_distance(location[0], location[1], e.latitude, e.longitude)
            )
            poi_categories.append({
                'name': category,
                'events': sorted_pois 
            })
        
        for category_group in poi_categories:
            for poi in category_group['events']:
                poi.is_expanded = False

        map_html = self.generate_map(location[0], location[1], radius, pois)

        # Returning user's role (For permissions)
        email = request.session.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.error(f"User with email {email} does not exist. Redirecting to login.")
            request.session.flush()
            return redirect("login")

        user_role = user.role
        
        for category_group in poi_categories:
            for poi in category_group['events']:
                poi.distance = round(self.calculate_distance(
                    location[0], location[1], poi.latitude, poi.longitude
                ), 1)
                
                if poi.description:
                    lines = poi.description.split('\n')
                    poi.short_description = lines[0] if lines else ""
                    
                    phone_match = re.search(r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', poi.description)
                    poi.phone = phone_match.group(0) if phone_match else None
                    
                    website_match = re.search(r'https?://[^\s]+', poi.description)
                    poi.website = website_match.group(0) if website_match else None
        
        context = {
            'map_html': map_html,
            'event_categories': poi_categories,
            'current_location': request.session.get('location_name', 'Milwaukee'),
            'current_radius': radius,
            'current_latitude': location[0],
            'current_longitude': location[1],
            'needs_fetch': needs_fetch,
            'user_role': user_role,
            'user_events': user_events,
            'error':error
        }

        return render(request, "homepage.html", context)

    def post(self, request):
        start_date_str = request.POST.get('start_date_str', '')
        end_date_str = request.POST.get('end_date_str', '')
        start_date = None
        end_date = None

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_date = timezone.make_aware(start_date)
            except ValueError:
                start_date = None

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                #making sure end of day is the current day and 23 hrs +59 min
                end_of_day = (end_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
                end_date = timezone.make_aware(end_of_day)
            except ValueError:
                end_date = None

        #Put the date into session
        if start_date:
            request.session['start_date'] = start_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            request.session.pop('start_date', None)
        if end_date:
            request.session['end_date'] =end_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            request.session.pop('end_date', None)

        location_name = request.POST.get('location', 'Milwaukee')
        radius = request.POST.get('radius', 5)

        try:
            radius = int(radius)
            if not (1 <= radius <= 50):
                radius = 5
        except (ValueError, TypeError):
            radius = 5

        geocoder = GeocodingService()
        location_coords = geocoder.get_coordinates(location_name)

        if not location_coords:
            messages.error(request, f"Could not find coordinates for '{location_name}'. Using previous location.")
            request.session['radius'] = radius
        else:
            request.session['location_name'] = location_name
            request.session['radius'] = radius
            request.session['location_coords'] = location_coords
            logger.info(f"POST request: Updated session location_name='{location_name}', radius={radius}, coords={location_coords}")

            # Fetch events within the radius for the system user
            system_user = User.objects.get(email="system@eventradar.local")
            user_events = self.get_events_within_radius2(location_coords[0], location_coords[1], radius, system_user)

            # Filter user-made events based on the start and end date
            if start_date and end_date:
                user_events = [event for event in user_events if start_date <= event.event_date <= end_date]
                print(user_events)
            elif start_date:
                user_events = [event for event in user_events if event.event_date >= start_date]
                print(user_events)
            elif end_date:
                user_events = [event for event in user_events if event.event_date <= end_date]
                print(user_events)
            else:
                user_events = []
                print("NO EVENTS")
        return redirect("homepage")

    def get_pois_within_radius(self, center_lat, center_lon, radius_miles):
        lat_change_per_mile = 1.0 / 69.0
        lon_change_per_mile = 1.0 / (69.0 * math.cos(math.radians(center_lat)))

        min_lat = center_lat - (radius_miles * lat_change_per_mile)
        max_lat = center_lat + (radius_miles * lat_change_per_mile)
        min_lon = center_lon - (radius_miles * lon_change_per_mile)
        max_lon = center_lon + (radius_miles * lon_change_per_mile)

        potential_pois = POI.objects.filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon
        )
        logger.info(f"Found {potential_pois.count()} potential POIs in bounding box for Haversine check.")

        nearby_pois = []
        for poi in potential_pois:
            distance = self.calculate_distance(center_lat, center_lon, poi.latitude, poi.longitude)
            if distance <= radius_miles:
                nearby_pois.append(poi)

        logger.info(f"Filtered down to {len(nearby_pois)} POIs within precise radius.")
        return nearby_pois

    def get_events_within_radius2(self, center_lat, center_lon, radius_miles, system_user):
        lat_change_per_mile = 1.0 / 69.0
        lon_change_per_mile = 1.0 / (69.0 * math.cos(math.radians(center_lat)))

        min_lat = center_lat - (radius_miles * lat_change_per_mile)
        max_lat = center_lat + (radius_miles * lat_change_per_mile)
        min_lon = center_lon - (radius_miles * lon_change_per_mile)
        max_lon = center_lon + (radius_miles * lon_change_per_mile)

        potential_events = Event.objects.filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon,

        ).exclude(created_by=system_user)
        logger.info(f"Found {potential_events.count()} potential user events in bounding box for Haversine check.")

        nearby_events = []
        for event in potential_events:
            distance = self.calculate_distance(center_lat, center_lon, event.latitude, event.longitude)
            if distance <= radius_miles:
                nearby_events.append(event)

        logger.info(f"Filtered down to {len(nearby_events)} user events within precise radius.")
        return nearby_events
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using the Haversine formula.
        Returns distance in miles.
        """
        # Earth radius in miles
        R = 3958.8
        
        # Convert coordinates from degrees to radians
        lat1_rad = radians(float(lat1))
        lon1_rad = radians(float(lon1))
        lat2_rad = radians(float(lat2))
        lon2_rad = radians(float(lon2))
        
        # Difference in coordinates
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance

    def generate_map(self, center_lat, center_lon, radius_miles, pois):
        m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
        radius_in_meters = radius_miles * 1609.34

        folium.Circle(
            location=[center_lat, center_lon],
            radius=radius_in_meters,
            color='#3186cc',
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.2,
            tooltip=f"{radius_miles:.1f} miles radius"
        ).add_to(m)
        marker_cluster = MarkerCluster().add_to(m)

        # Only show non-parking POIs by default
        for poi in pois:
            if (poi.category or '').lower() == 'parking':
                continue  # Skip parking POIs for default map display

            try:
                event_date_str = poi.event_date.strftime('%B %d, %Y at %I:%M %p')
            except AttributeError:
                event_date_str = "Date not available"

            popup_html = f"""
            <div class="event-popup">
                <h3>{poi.title}</h3>
                <p><strong>Date:</strong> {event_date_str}</p>
                <p><strong>Category:</strong> {poi.category or 'N/A'}</p>
                <p>{poi.description or 'No description available.'}</p>
            </div>
            """

            folium.Marker(
                location=[poi.latitude, poi.longitude],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=poi.title,
                icon=folium.Icon(icon="info-sign", prefix='fa', color="blue"),
            ).add_to(marker_cluster)

        return m._repr_html_()

class SettingPage(SessionLoginRequiredMixin,View):
    login_url = 'login'
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
                    request.session["email"] = user.email  
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
        
        elif "update_phone_number" in request.POST:
            new_phone_number = request.POST.get("phone_number")
            if new_phone_number:
                result = change_account_details(user, new_phone_number=new_phone_number)
                if result:
                    success_message = "Your phone number has been updated successfully"
                else:
                    error_message = "Failed to update your phone number"


        if success_message:
            return redirect("settings")

        return render(request, "SettingPage.html", {
            "user": user,
            "success": success_message,
            "error": error_message
        })


class SignOutView(View):
    def post(self, request):
        request.session.clear()
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
            if check.authenticate_email(email):
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

class WeatherView(View):
    def get(self, request):
        # Render the weather form template for GET requests
        return render(request, "weather.html")

    def post(self, request):
        api_key = '438802557a5074e655e46b4140076665'  # Consider moving this to settings.py for better security
        location_type = request.POST.get('locationType')
        location_input = request.POST.get('locationInput').strip()

        if not location_input:
            return render(request, "weather.html", {'error': 'Please enter a location.'})

        api_url = f'httpshttps://api.openweathermap.org/data/2.5/forecast?appid={api_key}&units=metric'

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

            # Check for a 404 response and return a friendly error message
            if response.status_code == 404:
                return render(request, "weather.html", {'error': 'Location not found. Please check your spelling.'})

            response.raise_for_status()  # Raise an exception for other HTTP errors
            weather_data = response.json()

            # Convert temperatures from Celsius to Fahrenheit
            for item in weather_data['list']:
                item['main']['temp'] = (item['main']['temp'] * 9/5) + 32

            return render(request, "weather.html", {'weather_data': weather_data})

        except requests.exceptions.RequestException as e:
            return render(request, "weather.html", {'error': f'Failed to fetch weather data: {str(e)}'})

class DeleteView(View):
    # DELETE page
    # Send to page that confirms that they understand that they will not be able to retrieve their account
    # If they click yes, they get brought to a page that they enter their email and enter their password two times
    # if they successfully enter the right email and passwords, the account is deleted and if it is successfully
    # deleted, they are redirected to a page that they successfully deleted account and go to login page

    def get(self, request):
        return render(request, "delete.html")
    def post(self,request):

        #Get the input information
        email=request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        auth = DeleteAcct()
        # Check if fields are blank
        if auth.isNotBlank(email, password1, password2):
            session_user=request.session.get('email')
            if session_user != email:
                return render(request, "delete.html", {"error": "Incorrect Email"})

            #Check if fields are blank
            #Check if passwords match
            if not auth.pass_exact(password1,password2):
                return render(request, "delete.html", {"error": "Passwords don't match"})


            if not auth.del_acct(email,password1,password2):
                return render(request, "delete.html", {"error": "Incorrect Email or Password"})
            else:
                request.session.clear()
                return redirect("delete_complete")

        #If none, return error at bottom of page
        else:
            return render(request, "delete.html", {"error": "Enter an email and password"})


class DeleteCompleteView(View):
    def get(self,request):
        return render(request, "delete_complete.html")

@csrf_exempt
@require_POST
def fetch_and_save_events_api(request):
    try:
        data = json.loads(request.body)
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        radius = float(data['radius'])
        location_name = str(data.get('location_name', 'Unknown Location'))

        logger.info(f"API endpoint called: Fetching events for lat={lat}, lon={lon}, radius={radius}")
        api_start_time = time.time()
        features = fetch_pois_from_api(lat, lon, radius, EVENT_API_KEY)
        api_end_time = time.time()
        logger.info(f"API fetch took {api_end_time - api_start_time:.2f} seconds.")

        if features:
            logger.info(f"API returned {len(features)} events.")

            logger.info("Starting bulk processing and saving/updating events...")
            start_time = time.time()
            num_processed = 0
            pois_to_create = []
            pois_to_update = []
            created_count = 0
            updated_count = 0
            update_fields = ['title', 'latitude', 'longitude', 'description', 'location_name', 'event_date', 'category', 'image_url']

            try:
                admin_user = User.objects.get(email='system@eventradar.local')
            except User.DoesNotExist:
                logger.error("System user not found during API fetch.")
                return JsonResponse({'status': 'error', 'message': 'Internal configuration error: System user missing.'}, status=500)

            api_place_ids = [f['properties'].get('place_id') for f in features if f.get('properties', {}).get('place_id')]
            if not api_place_ids:
                 logger.info("No valid place_ids found in API response.")
            else:
                existing_pois = POI.objects.filter(place_id__in=api_place_ids).in_bulk(field_name='place_id')
                logger.info(f"Found {len(existing_pois)} existing POIs in DB for comparison.")

                for feature in features:
                    props = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    place_id = props.get('place_id')

                    if not place_id or not geometry or 'coordinates' not in geometry:
                        continue

                    try:
                        latitude = float(geometry['coordinates'][1])
                        longitude = float(geometry['coordinates'][0])
                        
                        description_parts = []
                        for key in ['address_line1', 'address_line2', 'address_line3', 'phone', 'website', 'datasource_name']:
                            value = props.get(key)
                            if value is not None:
                                description_parts.append(str(value))
                        
                        street = props.get('street')
                        if street and str(street) not in description_parts:
                            description_parts.append(f"Street: {str(street)}")
                        
                        description = "\n".join(description_parts)
                        
                        title = None
                        
                        if props.get('name'):
                            title = str(props.get('name'))
                        
                        elif props.get('street'):
                            house_number = str(props.get('housenumber', ''))
                            street = str(props.get('street', ''))
                            if house_number and street:
                                title = f"{house_number} {street}"
                            else:
                                title = street
                        
                        elif props.get('city') or props.get('locality'):
                            location_prefix = str(props.get('city') or props.get('locality'))
                            street = str(props.get('street', ''))
                            if street:
                                title = f"{street}, {location_prefix}"
                            else:
                                title = location_prefix
                        
                        elif props.get('formatted'):
                            address_parts = str(props.get('formatted', '')).split(',')
                            if address_parts:
                                title = address_parts[0].strip()
                        
                        if not title:
                            api_categories = props.get('categories', [])
                            if api_categories:
                                category_parts = str(api_categories[0]).split('.')
                                title = category_parts[-1].replace('_', ' ').title()
                            else:
                                title = "Location Point"
                        
                        api_categories = props.get('categories', [])
                        category_label = None
                        
                        api_categories = [str(cat) for cat in api_categories]
                        
                        for cat in reversed(api_categories):
                            if cat in category_mapping:
                                category_label = category_mapping[cat]
                                break

                        if not category_label and api_categories:
                            for cat in reversed(api_categories):
                                cat_parts = cat.split('.')
                                for i in range(len(cat_parts), 0, -1):
                                    prefix = '.'.join(cat_parts[:i])
                                    if prefix in category_mapping:
                                        category_label = category_mapping[prefix]
                                        break
                                if category_label:
                                    break

                        if not category_label and api_categories:
                            last_cat = api_categories[-1]
                            last_segment = last_cat.split('.')[-1]
                            category_label = last_segment.replace('_', ' ').title()

                        if not category_label:
                            category_label = 'Point of Interest'
                        
                        formatted_location = str(props.get('formatted', location_name))
                        image_url = props.get('datasource', {}).get('raw', {}).get('image')
                        if image_url is not None:
                            image_url = str(image_url)
                        
                        logger.info(f"Processing place: {title} | Categories: {api_categories} | Mapped to: {category_label}")
                        
                        existing_poi = existing_pois.get(place_id)

                        if existing_poi:
                            update_needed = False
                            for field in update_fields:
                                new_value = locals().get(field)
                                if field == 'event_date': new_value = timezone.now()
                                if getattr(existing_poi, field) != new_value:
                                    setattr(existing_poi, field, new_value)
                                    update_needed = True
                            if update_needed:
                                pois_to_update.append(existing_poi)
                        else:
                            pois_to_create.append(
                                POI(
                                    place_id=place_id,
                                    title=title,
                                    latitude=latitude,
                                    longitude=longitude,
                                    description=description,
                                    location_name=formatted_location,
                                    event_date=timezone.now(),
                                    created_by=admin_user,
                                    category=category_label,
                                    image_url=image_url,
                                )
                            )
                        num_processed += 1
                    except (TypeError, ValueError) as e:
                        logger.error(f"Error processing feature {place_id}: {e}")
                        continue

                created_count = 0
                if pois_to_create:
                    try:
                        created_objs = POI.objects.bulk_create(pois_to_create)
                        created_count = len(created_objs)
                        logger.info(f"Bulk created {created_count} new POIs.")
                    except Exception as e:
                        logger.error(f"Error during bulk_create: {e}")

                updated_count = 0
                if pois_to_update:
                    try:
                        updated_count = POI.objects.bulk_update(pois_to_update, update_fields)
                        logger.info(f"Bulk updated {updated_count} existing POIs.")
                    except Exception as e:
                        logger.error(f"Error during bulk_update: {e}")


            end_time = time.time()
            total_time = end_time - start_time
            logger.info(f"Finished bulk processing {num_processed} POIs in {total_time:.2f} seconds.")

            logger.info(f"Updating SearchedArea: lat={lat}, lon={lon}, radius={radius}, has_events=True")
            SearchedArea.objects.update_or_create(
                latitude=lat, longitude=lon, radius=radius,
                defaults={'has_events': True, 'last_checked': timezone.now()}
            )

            logger.info(f"API endpoint: Saved {created_count} new POIs via bulk.")
            return JsonResponse({
                'status': 'success',
                'message': f'{created_count} new POIs found and saved.',
                'processed_count': num_processed
            })
        else:
            created_count = 0
            num_processed = 0
            logger.info(f"Updating SearchedArea: lat={lat}, lon={lon}, radius={radius}, has_events=False (API fetch failed)")
            SearchedArea.objects.update_or_create(
                latitude=lat, longitude=lon, radius=radius,
                defaults={'has_events': False, 'last_checked': timezone.now()}
            )
            logger.info("API endpoint: No POIs found or API error occurred.")
            return JsonResponse({
                'status': 'success',
                'message': 'No new POIs found or API error occurred.',
                'processed_count': 0
            })

    except json.JSONDecodeError:
        logger.error("API endpoint: Invalid JSON received.")
        return JsonResponse({'status': 'error', 'message': 'Invalid request format.'}, status=400)
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"API endpoint: Invalid data received - {e}")
        return JsonResponse({'status': 'error', 'message': f'Invalid data: {e}'}, status=400)
    except Exception as e:
        logger.exception("API endpoint: An unexpected error occurred.")
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred.'}, status=500)

###application
#make sure this is only viewable through users/admins (not event managers) only
class ApplicationClass(UserRequiredMixin,View):
    def get(self, request):
        return render(request, "application.html")
    def post(self, request):
        auth=VerifyAccount()
        applic=ApplicationMethods()
        session_user = request.session.get('email')
        #get the user from session
        email = request.session.get("email")
        user = User.objects.get(email=email)  # Find user by email
        message = request.POST.get('app_message', '')
        #check that the form is under 3000 characters
        if message and len(message)<3000:
            applic.create_app(user=user,message=message)

            return redirect("app_confirmation")

        else:
            return render(request, "application.html", {"error": "Invalid message"})


        #create form object
class App_Confirm(View):
    def get(self, request):
        return render(request, "App_Confirm.html")

class Approval(AdminRequiredMixin,View):
    def get(self, request):
        pending_apps = Application.objects.filter(status=ApplicationStatus.PENDING)

        return render(request, "admin_app_approval.html",{'applications': pending_apps})

    def post(self, request):
        #load all applications that have pending status
        application_id = request.POST.get('application_id')  #Get the app id
        action = request.POST.get('action') #getting the action

        if application_id and action:
            application = get_object_or_404(Application, id=application_id)

            #If accepted button is pressed
            #Put status as accepted
            if action == 'accept':
                application.status = "Accepted"
                application.save()

                #change user's role to event manager
                user = application.user
                user.role = 'Event_Manager'
                user.save()

            #if denied
            #just change app status
            elif action == 'deny':
                application.status = "Denied"
                application.save()

                # After processing, redirect back to the application approval page
            return redirect('app_approve')

        # If something went wrong, redirect back to the same page
        return redirect('app_approve')

def get_event_details(request, event_id):
    try:
        event = Event.objects.get(id=event_id)

        phone = None
        website = None
        if event.description:
            phone_match = re.search(r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', event.description)
            phone = phone_match.group(0) if phone_match else None
            website_match = re.search(r'https?://[^\s]+', event.description)
            website = website_match.group(0) if website_match else None


        return JsonResponse({
            'id': str(event.id),
            'title': event.title,
            'description': event.description,
            'location_name': event.location_name,
            'latitude': event.latitude,
            'longitude': event.longitude,
            'category': event.category,
            'image_url': event.image_url,
            'event_date': event.event_date.strftime('%B %d, %Y at %I:%M %p') if event.event_date else None,
            'phone': phone,
            'website': website
        })
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

def event_details_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    place_details = fetch_place_details(event.place_id)

    context = {
        'event': event,
        'place_details': place_details
    }
    return render(request, 'event_details.html', context)

def fetch_place_details(place_id):
    api_url = f"https://api.geoapify.com/v2/place-details?id={place_id}&apiKey={settings.EVENT_API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch place details: {e}")
    return None

class EventPlan(SessionLoginRequiredMixin, View):
    def get(self, request):
        email = request.session.get("email")
        user = User.objects.get(email=email)  # Find user by email
        plans = Plan.objects.filter(user=user).prefetch_related('events')
        user_plans = plans
        return render(request, "eventplan.html", {
            'plans': plans,
            'user_plans': user_plans,
        })

    def post(self, request):
        email = request.session.get("email")
        user = User.objects.get(email=email)
        plans = Plan.objects.filter(user=user).prefetch_related('events')
        user_plans = plans

        # Handle create form
        if "create_name" in request.POST:
            name = request.POST.get("create_name", "").strip()
            start_date_str = request.POST.get("start_date_str", "").strip()
            end_date_str = request.POST.get("end_date_str", "").strip()
            error = None

            if not name or not start_date_str or not end_date_str:
                error = "All fields are required."
            else:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    if start_date > end_date:
                        error = "Start date must be before or equal to end date."
                except ValueError:
                    error = "Invalid date format."

            if not error:
                Plan.objects.create(
                    user=user,
                    name=name,
                    start_date=start_date,
                    end_date=end_date
                )
                plans = Plan.objects.filter(user=user).prefetch_related('events')
                user_plans = plans
                return render(request, "eventplan.html", {
                    'plans': plans,
                    'user_plans': user_plans,
                    'success': "Plan created successfully!"
                })
            else:
                return render(request, "eventplan.html", {
                    'plans': plans,
                    'user_plans': user_plans,
                    'error': error
                })

        # Handle edit form
        elif "edit_name" in request.POST:
            plan_id = request.POST.get("selected_plan")
            new_name = request.POST.get("edit_name", "").strip()
            new_start = request.POST.get("edit_start_date", "").strip()
            new_end = request.POST.get("edit_end_date", "").strip()
            error = None

            if not plan_id or not new_name or not new_start or not new_end:
                error = "All fields are required."
            else:
                try:
                    plan = Plan.objects.get(id=plan_id, user=user)
                    start_date = datetime.strptime(new_start, "%Y-%m-%d").date()
                    end_date = datetime.strptime(new_end, "%Y-%m-%d").date()
                    if start_date > end_date:
                        error = "Start date must be before or equal to end date."
                    else:
                        plan.name = new_name
                        plan.start_date = start_date
                        plan.end_date = end_date
                        plan.save()
                except Plan.DoesNotExist:
                    error = "Plan not found."
                except ValueError:
                    error = "Invalid date format."

            plans = Plan.objects.filter(user=user).prefetch_related('events')
            user_plans = plans
            if not error:
                return render(request, "eventplan.html", {
                    'plans': plans,
                    'user_plans': user_plans,
                    'success': "Plan updated successfully!",
                    'edit_mode': True
                })
            else:
                return render(request, "eventplan.html", {
                    'plans': plans,
                    'user_plans': user_plans,
                    'error': error,
                    'edit_mode': True
                })

        # Handle delete form
        elif "del_selected" in request.POST:
            plan_id = request.POST.get("del_selected")
            error = None
            if not plan_id:
                error = "Please select a plan to delete."
            else:
                try:
                    plan = Plan.objects.get(id=plan_id, user=user)
                    plan.delete()
                except Plan.DoesNotExist:
                    error = "Plan not found."

            plans = Plan.objects.filter(user=user).prefetch_related('events')
            user_plans = plans
            if not error:
                return render(request, "eventplan.html", {
                    'plans': plans,
                    'user_plans': user_plans,
                    'success': "Plan deleted successfully!",
                    'delete_mode': True
                })
            else:
                return render(request, "eventplan.html", {
                    'plans': plans,
                    'user_plans': user_plans,
                    'error': error,
                    'delete_mode': True
                })

        # Fallback
        return render(request, "eventplan.html", {
            'plans': plans,
            'user_plans': user_plans,
            'error': "Invalid message"
        })

@csrf_exempt
@require_POST
def add_to_plan(request):
    """
    Add a POI or Event to a user's plan.
    POST data: plan_id, item_type ('poi' or 'event'), item_id
    """
    user_email = request.session.get("email")
    if not user_email:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    user = User.objects.get(email=user_email)
    plan_id = request.POST.get('plan_id')
    item_type = request.POST.get('item_type')
    item_id = request.POST.get('item_id')
    if not (plan_id and item_type and item_id):
        return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)
    try:
        plan = Plan.objects.get(id=plan_id, user=user)
        if item_type == 'event':
            event = Event.objects.get(id=item_id)
            plan.events.add(event)
        elif item_type == 'poi':
            poi = POI.objects.get(id=item_id)
            plan.pois.add(poi)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid item type'}, status=400)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def get_user_plans(request):
    user_email = request.session.get("email")
    if not user_email:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    user = User.objects.get(email=user_email)
    plans = Plan.objects.filter(user=user)
    return JsonResponse({
        'plans': [
            {'id': str(plan.id), 'name': plan.name, 'start_date': str(plan.start_date), 'end_date': str(plan.end_date)}
            for plan in plans
        ]
    })

class MyPlansView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(email=request.session["email"])
        plans = (
            Plan.objects.filter(user=user)
            .prefetch_related("events", "pois")
            .order_by("-start_date")
        )

        selected_plan_id = request.GET.get("plan_id")
        selected_plan = plans.filter(id=selected_plan_id).first() if selected_plan_id else None

        merged_items: list = []
        if selected_plan:
            order = getattr(selected_plan, "plan_order", None)
            if order and order.order_json:
                try:
                    import json
                    order_list = json.loads(order.order_json)
                    items_by_id = {str(obj.id): obj for obj in list(selected_plan.events.all()) + list(selected_plan.pois.all())}
                    merged_items = [items_by_id[iid] for iid in order_list if iid in items_by_id]
                    for obj in list(selected_plan.events.all()) + list(selected_plan.pois.all()):
                        if str(obj.id) not in order_list:
                            merged_items.append(obj)
                except Exception:
                    merged_items = sorted(
                        list(selected_plan.events.all()) + list(selected_plan.pois.all()),
                        key=lambda obj: getattr(obj, "start_date", None) or getattr(obj, "event_date", None) or timezone.now(),
                    )
            else:
                for e in selected_plan.events.all():
                    e._plan_date = e.start_date
                for p in selected_plan.pois.all():
                    p._plan_date = p.event_date
                merged_items = sorted(
                    list(selected_plan.events.all()) + list(selected_plan.pois.all()),
                    key=lambda obj: getattr(obj, "_plan_date", None) or timezone.now(),
                )

        map_html = None
        if selected_plan and merged_items:
            coords = [
                (obj.latitude, obj.longitude)
                for obj in merged_items
                if obj.latitude is not None and obj.longitude is not None
            ]
            centre = coords[0] if coords else (43.0389, -87.9065)

            fm = folium.Map(location=centre, zoom_start=15, control_scale=True)
            mcluster = MarkerCluster().add_to(fm)

            for idx, obj in enumerate(merged_items, start=1):
                folium.Marker(
                    location=[obj.latitude, obj.longitude],
                    tooltip=f"{idx}. {obj.title}",
                    popup=folium.Popup(f"<b>{obj.title}</b><br>{obj.location_name}", max_width=280),
                    icon=DivIcon(
                        icon_size=(28, 28),
                        icon_anchor=(14, 14),
                        html=(
                            f'<div style="background:#7a3bda;color:#fff;'
                            f'border-radius:50%;width:28px;height:28px;'
                            f'line-height:28px;text-align:center;font-weight:bold;">{idx}</div>'
                        ),
                    ),
                ).add_to(mcluster)

            if len(coords) > 1:
                base_line = folium.PolyLine(
                    coords, color="#7a3bda", weight=4, opacity=0.85
                ).add_to(fm)
                try:
                    PolyLineTextPath(
                        base_line,
                        "   ➔   ",
                        repeat=True,
                        offset=6,
                        attributes={"font-size": "14", "fill": "#7a3bda"},
                    ).add_to(fm)
                except Exception:
                    pass

            map_html = fm._repr_html_()

        return render(
            request,
            "myplans.html",
            {
                "plans": plans,
                "selected_plan": selected_plan,
                "merged_items": merged_items,
                "map_html": map_html,
            },
        )

@csrf_exempt
@require_POST
def save_plan_order(request):
    import json
    user_email = request.session.get("email")
    if not user_email:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    user = User.objects.get(email=user_email)
    plan_id = request.POST.get('plan_id')
    order_json = request.POST.get('order')
    if not (plan_id and order_json):
        return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)
    try:
        plan = Plan.objects.get(id=plan_id, user=user)
        plan_order, _ = PlanOrder.objects.get_or_create(plan=plan)
        plan_order.order_json = order_json
        plan_order.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_GET
def get_plan_map(request):
    user_email = request.session.get("email")
    if not user_email:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    user = User.objects.get(email=user_email)
    plan_id = request.GET.get('plan_id')
    if not plan_id:
        return JsonResponse({'success': False, 'error': 'Missing plan_id'}, status=400)
    try:
        plan = Plan.objects.get(id=plan_id, user=user)
        order = getattr(plan, "plan_order", None)
        if order and order.order_json:
            import json
            order_list = json.loads(order.order_json)
            items_by_id = {str(obj.id): obj for obj in list(plan.events.all()) + list(plan.pois.all())}
            merged_items = [items_by_id[iid] for iid in order_list if iid in items_by_id]
            for obj in list(plan.events.all()) + list(plan.pois.all()):
                if str(obj.id) not in order_list:
                    merged_items.append(obj)
        else:
            for e in plan.events.all():
                e._plan_date = e.start_date
            for p in plan.pois.all():
                p._plan_date = p.event_date
            merged_items = sorted(
                list(plan.events.all()) + list(plan.pois.all()),
                key=lambda obj: getattr(obj, "_plan_date", None) or timezone.now(),
            )
        map_html = None
        if merged_items:
            coords = [
                (obj.latitude, obj.longitude)
                for obj in merged_items
                if obj.latitude is not None and obj.longitude is not None
            ]
            centre = coords[0] if coords else (43.0389, -87.9065)
            fm = folium.Map(location=centre, zoom_start=15, control_scale=True)
            mcluster = MarkerCluster().add_to(fm)
            for idx, obj in enumerate(merged_items, start=1):
                folium.Marker(
                    location=[obj.latitude, obj.longitude],
                    tooltip=f"{idx}. {obj.title}",
                    popup=folium.Popup(f"<b>{obj.title}</b><br>{obj.location_name}", max_width=280),
                    icon=DivIcon(
                        icon_size=(28, 28),
                        icon_anchor=(14, 14),
                        html=(
                            f'<div style="background:#7a3bda;color:#fff;'
                            f'border-radius:50%;width:28px;height:28px;'
                            f'line-height:28px;text-align:center;font-weight:bold;">{idx}</div>'
                        ),
                    ),
                ).add_to(mcluster)
            if len(coords) > 1:
                base_line = folium.PolyLine(
                    coords, color="#7a3bda", weight=4, opacity=0.85
                ).add_to(fm)
                try:
                    PolyLineTextPath(
                        base_line,
                        "   ➔   ",
                        repeat=True,
                        offset=6,
                        attributes={"font-size": "14", "fill": "#7a3bda"},
                    ).add_to(fm)
                except Exception:
                    pass
            map_html = fm._repr_html_()
        return JsonResponse({'success': True, 'map_html': map_html})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)