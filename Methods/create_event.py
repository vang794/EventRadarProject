from datetime import timezone, datetime

from polls.models import User, Event  # imports user model from poll app
from datetime import datetime, time, timedelta
from django.utils import timezone

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

    #title methods
    def set_title(self, event,title):
        event.title = title
        event.save()

    #overall check title
    def check_title(self,title):
        pass
    def title_length(self,title):
        title_length = len(title)
        #check title length meets requirements (more than 0 characters and less than 100 characters)
        if 0<title_length<=100:
            return False
        else:
            return True

    #description methods
    def set_desc(self, event, description):
        event.description = description
        event.save()

    #set location name after getting the information from the queue
    def set_location_name(self, user, location_name):
        pass

    # set location latitude after getting the information from the queue
    def set_latitude(self, user, latitude):
        pass

    # set location longitude after getting the information from the queue
    def set_longitude(self, user, longitude):
        pass

    # convert date of the given information into a format suitable for the model
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

    #Set category
    def set_category(self, event, category):
        pass
    def get_category(self):
        pass