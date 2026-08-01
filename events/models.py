from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    ONCE = 'once'
    YEARLY = 'yearly'
    TYPE_CHOICES = [
        (ONCE, 'Once'),
        (YEARLY, 'Repeated Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.date})"


import calendar as cal_module
from datetime import date


def get_events_for_month(user, year, month):
    """Returns events falling in the given year/month, handling yearly recurrence."""
    once_events = Event.objects.filter(
        user=user, event_type=Event.ONCE, date__year=year, date__month=month
    )
    yearly_events = Event.objects.filter(
        user=user, event_type=Event.YEARLY, date__month=month
    )
    # Combine and sort by day-of-month
    combined = list(once_events) + list(yearly_events)
    combined.sort(key=lambda e: e.date.day)
    return combined


def get_calendar_grid(year, month):
    """Returns a list of weeks, each week a list of day numbers (0 = blank/no day)."""
    cal = cal_module.Calendar(firstweekday=0)  # Monday start
    return cal.monthdayscalendar(year, month)