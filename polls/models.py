import uuid
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
    password = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

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
    
    category = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title
