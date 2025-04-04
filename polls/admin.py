# Register your models here.
from django.contrib import admin
from .models import User, Event, Application

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')
    readonly_fields = ('id',)

admin.site.register(User, UserAdmin)
admin.site.register(Event)
admin.site.register(Application)
