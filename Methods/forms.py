from django import forms
from polls.models import User

class CreateAccountForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
        required=True
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone_number']
