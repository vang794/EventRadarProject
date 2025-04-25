from datetime import timezone, datetime
from math import radians, sin, cos, sqrt, atan2
import math
import logging
from polls.models import User, Event  # imports user model from poll app
from datetime import datetime, time, timedelta
from django.utils import timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Create_Parking:
    #get the user
    #check user exists
    #title
    #description
    #retrieve from address (which gets lat and long and place id)
    #event date (temp)
    #set start date
    #set end date
    #created_by user (gets user from the session)
    #set category
    def create_parking(self,title,description,place_id,location_name,latitude,longitude,event_date,user,category):
        new_event = Event(
            place_id=place_id,
            title = title,
            description = description,
            location_name = location_name,
            latitude = latitude,
            longitude = longitude,
            event_date = event_date,
            created_by = user,
            category = category,
            img_url = "",
        )
        new_event.save()

    #Reusing code for parking
    def get_events_within_radius(self, center_lat, center_lon, radius_miles, system_user):
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
        logger.info(f"Found {potential_events.count()} potential events in bounding box for Haversine check.")

        nearby_events = []
        for event in potential_events:
            distance = self.calculate_distance(center_lat, center_lon, event.latitude, event.longitude)
            if distance <= radius_miles:
                nearby_events.append(event)

        logger.info(f"Filtered down to {len(nearby_events)} events within precise radius.")
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
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance