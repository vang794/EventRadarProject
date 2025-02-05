from django.db import models

# Create your models here.
class Roles(models.TextChoices):
    Event_Manager = 'Event_Manager'
    User = 'User'

class User(models.TextChoices):
    #id can also be username
    id = models.CharField(max_length=20,primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    phone_number = models.IntegerField()
    role = models.CharField(max_length=50, choices=Roles)
