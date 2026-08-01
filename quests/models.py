from django.db import models
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from datetime import date


class Quest(models.Model):
    TEN_YEAR_FIRST = 'ten_year_first'
    TEN_YEAR_SECOND = 'ten_year_second'
    YEARLY = 'yearly'
    MONTHLY = 'monthly'
    CATEGORY_CHOICES = [
        (TEN_YEAR_FIRST, '10 Year Goal (1st Half)'),
        (TEN_YEAR_SECOND, '10 Year Goal (2nd Half)'),
        (YEARLY, 'Yearly Goal'),
        (MONTHLY, 'Monthly Goal'),
    ]

    ACTIVE = 'active'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
    ]

    XP_REWARDS = {
        TEN_YEAR_FIRST: 500,
        TEN_YEAR_SECOND: 750,
        YEARLY: 125,
        MONTHLY: 20,
    }

    PENALTY_LEVELS = {
        TEN_YEAR_FIRST: 5,
        TEN_YEAR_SECOND: 5,
        YEARLY: 2,
        MONTHLY: 1,
    }

    SLOT_LIMITS = {
        TEN_YEAR_FIRST: 3,
        TEN_YEAR_SECOND: 3,
        YEARLY: 2,
        MONTHLY: 1,
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quests')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    created_date = models.DateField(auto_now_add=True)
    deadline = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

def calculate_deadline(category, profile_created_at):
    profile_start = profile_created_at.date()

    if category == Quest.TEN_YEAR_FIRST:
        return profile_start + relativedelta(years=5)
    elif category == Quest.TEN_YEAR_SECOND:
        return profile_start + relativedelta(years=10)
    elif category == Quest.YEARLY:
        today = date.today()
        return date(today.year, 12, 31)
    elif category == Quest.MONTHLY:
        today = date.today()
        next_month = today.replace(day=28) + relativedelta(days=4)
        return next_month.replace(day=1) - relativedelta(days=1)

def check_and_apply_penalties(user):
    """Run on every quest page load. Expires overdue active quests and applies penalties."""
    today = date.today()
    overdue = Quest.objects.filter(user=user, status=Quest.ACTIVE, deadline__lt=today)

    profile = user.profile

    for quest in overdue:
        penalty = Quest.PENALTY_LEVELS[quest.category]
        profile.level = max(1, profile.level - penalty)
        profile.xp = 0
        profile.save()

        quest.delete()