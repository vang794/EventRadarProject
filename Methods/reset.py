#Inherit from PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from polls.models import User
from django.contrib.auth.views import PasswordResetView
from django import forms


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email is not registered")
        return email

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
