from django.db import models

# Create your models here.

class Roles(models.TextChoices):
    EVENT_MANAGER = 'Event_Manager', 'Event Manager'  # First is stored value, second is human-readable
    USER = 'User', 'User'

class User(models.Model):
    id = models.CharField(max_length=20, primary_key=True, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)


    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
