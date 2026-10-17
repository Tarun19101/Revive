from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PlayerProfile, PlayerRecord, PlayerAchievement
from .constants import UTC_OFFSET_CHOICES


def utc_offset_field():
    return forms.TypedChoiceField(
        label='Time zone (UTC offset)',
        choices=[('', 'Select your UTC offset')] + UTC_OFFSET_CHOICES,
        coerce=int,
    )

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class OnboardingForm(forms.ModelForm):
    utc_offset_minutes = utc_offset_field()

    class Meta:
        model = PlayerProfile
        fields = ['date_of_birth', 'weight_kg', 'height_cm', 'utc_offset_minutes']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The model allows blanks, but onboarding exists to collect all four answers.
        for name in ('date_of_birth', 'weight_kg', 'height_cm'):
            self.fields[name].required = True


class ProfileEditForm(forms.ModelForm):
    utc_offset_minutes = utc_offset_field()

    class Meta:
        model = PlayerProfile
        fields = ['weight_kg', 'height_cm', 'utc_offset_minutes']


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