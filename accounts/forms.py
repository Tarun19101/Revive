from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PlayerProfile, PlayerRecord, PlayerAchievement


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class OnboardingForm(forms.ModelForm):

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

class AchievementForm(forms.ModelForm):
    class Meta:
        model = PlayerAchievement
        fields = [
            'bench_press', 'shoulder_press', 'deadlift', 'weighted_squats',
            'max_pushups', 'max_pullups', 'max_russian_crunches',
            'run_5km_minutes', 'run_5km_seconds',
        ]