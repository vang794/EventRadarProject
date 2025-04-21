from datetime import timezone, datetime

from polls.models import User, Event  # imports user model from poll app
from datetime import datetime, time, timedelta
from django.utils import timezone
#for email validation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CreateEvent:
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
    def create_event(self,title,description,place_id,location_name,latitude,longitude,event_date,user,category):
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
    #get event
    def get_event(self):
        pass
    #Check event exists
    #If event exists, return true
    def check_event(self,event,title):
        if event is not None:
            return event.objects.filter(title=title) is not None

    #from getting queue, set place id
    def set_place_id(self):
        pass

    def set_title(self, event,title):
        #if user exists, allow change title
        event.title = title
        event.save()
    def set_desc(self, event, description):
        event.description = description
        event.save()
    def set_location_name(self, user, location_name):
        pass
    def set_latitude(self, user, latitude):
        pass
    def set_longitude(self, user, longitude):
        pass

    def date_conversion(self, event_date_str):
        event_date_str=event_date_str
        event_date = None
        if event_date_str is not None:
            try:
                event_date = timezone.make_aware(datetime.strptime(event_date_str, '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                event_date = None
        return event_date

    #temp but use for start date and end date
    def set_date(self, event, event_date_str):
        date=self.date_conversion(event_date_str)
        #set as event's date
        if event is not None:
            event.event_date = date
            event.save()

    #def set_start_date(self, user, event_date):
        #pass
    #def set_end_date(self, user, event_date):
        #pass

    def set_user(self, user):
        pass
    def change_account_role(self, user, role):
        #Check if user exists and is not None
        if user is not None:
            self.change_role(user, role)

    def change_role(self, user, role):
        user.role = role  #Update the user's role
        user.save()