from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from .constants import HABIT_CATALOG


class PlayerHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    habit_key = models.CharField(max_length=50)
    streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_completed = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'habit_key')

    @property
    def name(self):
        return HABIT_CATALOG[self.habit_key]['name']

    @property
    def skill_key(self):
        return HABIT_CATALOG[self.habit_key]['skill_key']

    @property
    def done_today(self):
        return self.last_completed == date.today()

    def __str__(self):
        return f"{self.user.username} - {self.name}"