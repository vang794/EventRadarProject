import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Roles(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    EVENT_MANAGER = 'Event_Manager', 'Event Manager'
    USER = 'User', 'User'


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    username = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

class POI(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    place_id = models.CharField(max_length=255, unique=True, null=True, blank=True, help_text="Unique ID from the data source (e.g., Geoapify place_id)")
    title = models.CharField(max_length=100)
    description = models.TextField()
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pois')
    category = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class EventType(models.TextChoices):
    Festival = 'Festival', 'Festival'
    Convention = 'Convention', 'Convention'
    Business = 'Business', 'Business'
    Concert = 'Concert', 'Concert'
    Exhibition = 'Exhibition', 'Exhibition'
    Recreational = 'Recreational', 'Recreational'
    Social = 'Social', 'Social'
    Misc = 'Misc', 'Misc'

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    category = models.CharField(max_length=50,choices=EventType.choices,blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class SearchedArea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField()
    has_events = models.BooleanField(default=False)
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Area at ({self.latitude}, {self.longitude}) with radius {self.radius} miles"

class ApplicationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    DENIED = 'denied', 'Denied'


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices,default=ApplicationStatus.PENDING)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)  #When submission was added

    def __str__(self):
        return f"Application from {self.user.username} - Status: {self.get_status_display()}"

class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    events = models.ManyToManyField("Event", blank=True, related_name="plans")

    def __str__(self):
        return self.name or f"Plan from {self.start_date} to {self.end_date}"

class Parking(models.Model):
    events = models.ManyToManyField("Event", blank=True, related_name="parkings")
    poi = models.ForeignKey("POI", related_name="parkings", on_delete=models.CASCADE)

    def __str__(self):
        return f"Parking at {self.poi.title}"