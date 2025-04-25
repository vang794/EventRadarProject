from django import forms
from django.core.exceptions import ValidationError

from polls.models import User
from polls.models import Event,EventType

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
    category = forms.ChoiceField(
        choices=EventType.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    end_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    image_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    location_name = forms.CharField(
        label='Address',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'location_name',
            'start_date',
            'end_date',
            'category',
            'image_url',
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before end date.")
            elif end_date < start_date:
                raise ValidationError("End date must be after start date.")