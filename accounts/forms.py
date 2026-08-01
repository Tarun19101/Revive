from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PlayerProfile, PlayerRecord
from .constants import CHOICE_OPTIONS

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class OnboardingForm(forms.ModelForm):
    martial_art = forms.ChoiceField(choices=[(m, m) for m in CHOICE_OPTIONS['martial_art']])
    weapon = forms.ChoiceField(choices=[(w, w) for w in CHOICE_OPTIONS['weapon']])
    hobby = forms.ChoiceField(choices=[(h, h) for h in CHOICE_OPTIONS['hobby']])

    class Meta:
        model = PlayerProfile
        fields = ['date_of_birth', 'weight_kg', 'height_cm']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = ['weight_kg', 'height_cm']


class PlayerRecordForm(forms.ModelForm):
    class Meta:
        model = PlayerRecord
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 6, 'placeholder': "What happened today?"}),
        }

