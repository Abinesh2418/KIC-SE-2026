from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class ParticipantRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=15, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 9876543210'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-input',
                'autocomplete': 'off',
            })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-input',
            'autocomplete': 'off',
        })


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username or Email', widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Username or Email',
        'autocomplete': 'off',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password',
    }))


class EventSettingsForm(forms.Form):
    duration_minutes = forms.IntegerField(
        min_value=1, max_value=300,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    max_tab_switches = forms.IntegerField(
        min_value=0, max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    leaderboard_public = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    show_score_to_participant = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
