from django.db import models
from django.contrib.auth.models import User


class CashFlow(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    LOAN_GIVEN = 'loan_given'
    LOAN_TAKEN = 'loan_taken'
    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
        (LOAN_GIVEN, 'Loan Given'),
        (LOAN_TAKEN, 'Loan Taken'),
    ]

    PENDING = 'pending'
    CLEARED = 'cleared'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CLEARED, 'Cleared'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cash_flows')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    person = models.CharField(max_length=100)
    reason = models.CharField(max_length=200)
    cash_flow_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_cash_flow_type_display()} - {self.amount} ({self.person})"