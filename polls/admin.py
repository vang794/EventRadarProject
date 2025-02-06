from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User  # Import the models

# Register your models here
admin.site.register(User)
