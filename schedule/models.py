from django.contrib.auth.models import User
from django.db import models

from .utils import hour_label


class WeekSchedule(models.Model):
    """One hour-by-hour plan per user per week. week_start is always a Sunday."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='week_schedules')
    week_start = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_start']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'week_start'], name='one_schedule_per_user_per_week'
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - week of {self.week_start}"


class ScheduleSlot(models.Model):
    """What the player planned for one hour of one day. Empty hours are not stored."""
    schedule = models.ForeignKey(WeekSchedule, on_delete=models.CASCADE, related_name='slots')
    day = models.PositiveSmallIntegerField()   # 0 = Sunday ... 6 = Saturday
    hour = models.PositiveSmallIntegerField()  # 0 = 12:00 am hour ... 23 = 11:00 pm hour
    text = models.CharField(max_length=200)

    class Meta:
        ordering = ['day', 'hour']
        constraints = [
            models.UniqueConstraint(fields=['schedule', 'day', 'hour'], name='one_slot_per_hour'),
            models.CheckConstraint(condition=models.Q(day__gte=0, day__lte=6), name='slot_day_range'),
            models.CheckConstraint(condition=models.Q(hour__gte=0, hour__lte=23), name='slot_hour_range'),
        ]

    @property
    def time_label(self):
        return hour_label(self.hour)

    def __str__(self):
        return f"{self.time_label}: {self.text}"