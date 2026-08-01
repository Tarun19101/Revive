from django import forms
from .models import Quest


class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'category']