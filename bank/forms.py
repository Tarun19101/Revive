from django import forms
from .models import CashFlow


class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = ['amount', 'person', 'reason', 'cash_flow_type']