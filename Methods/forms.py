from django import forms
from polls.models import User
from polls.models import Event

class CreateAccountForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
        required=True
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone_number']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'location_name',
            'latitude',
            'longitude',
            'start_date',
            'end_date',
            'category',
            'image_url',  
        ]